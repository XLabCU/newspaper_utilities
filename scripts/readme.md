The pipeline can be invoked from the pipeline script, or you can run each script in turn.

We're working with pdfs from the BANQ of the Shawville Equity, published weekly since the 1880s in Shawville Quebec.

First we preprocess the images so that we reduce the size while retaining quality as best we can. Then, because of some regularities in how the oldest editions of the Equity were laid out, we use that to snip the thing into article-sized chunks. However, some of the potential OCR models have limitations on vertical height, so we also snip long pieces in half.

Then, we perform the OCR steps. There are some options here; we've tried to cover a variety that might work for you. The pipeline script assumes pytesseract as default. This writes the OCR to individual jsonL, so even if things should stop, you've still got most of your output. OCR is a memory hog.

The next step is to re-assemble snipped pieces back into full articles using `segment_articles.py`.

At this step, you could do whatever you want with the results. We also include three more scripts for tagging, for generating a timeline, and for some text analysis. For these last three, I was looking at issues of the Equity that included coverage of Jack the Ripper. I was wondering, 'what does it mean for that story to be republished in a small village in West Quebec?' which accounts for some of the idiosyncracy. But for present purposes, they can work as a model for moving the data along. Outputs are written as json files which could then be dumped into various visualiations.

# Tuning the Preprocessing Step

The preprocessing pipeline works like this:

## 1. Calculate Optimal DPI

```
INPUT: pdf_path, target_mb (default: 4)

Convert first page at 100 DPI as test
Estimate megabytes from pixel count
Scale DPI to hit target size
Clamp result between 75–200 DPI

OUTPUT: optimal_dpi
```

## 2. Detect Column Boundaries (Core)

```
INPUT: image_array, page_num, expected_columns (default: 5)

# --- PREPROCESSING ---
Convert to grayscale
Binarize with Otsu's threshold (text=white, background=black)

# --- ADAPTIVE ROI (⚠️ TUNABLE) ---
IF page 1:
    roi_top = height × 0.18      ← Skip masthead
ELSE:
    roi_top = height × 0.05      ← Skip header only
roi_bottom = height × 0.98       ← Skip footer
Crop image to ROI

# --- SIGNAL A: Physical Divider Lines ---
Create tall thin kernel (1px wide × 100px tall)  ← ⚠️ TUNABLE
Morphological OPEN to extract vertical lines
Sum pixels vertically → line_signal (1D array)

# --- SIGNAL B: Whitespace Gutters ---
Create wide short kernel (15px wide × 1px tall)  ← ⚠️ TUNABLE
Dilate to "smear" text horizontally
Sum pixels vertically → gutter_signal (1D array)

# --- HYBRID SCORING ---
Normalize line_signal to 0.0–1.0
Invert & normalize gutter_signal (low density = high score)
combined_score = (line × 0.7) + (gutter × 0.3)  ← ⚠️ TUNABLE weights

# --- PEAK DETECTION (⚠️ TUNABLE) ---
min_col_width = image_width ÷ (expected_columns + 2)
Find peaks in combined_score where:
    distance ≥ min_col_width    ← Minimum gap between peaks
    height ≥ 0.1                ← Minimum absolute score
    prominence ≥ 0.05           ← Must stand out from neighbors

boundaries = [0] + peaks + [image_width]

OUTPUT: boundaries (list of x-coordinates)
```

## 3. Split Into Columns

```
INPUT: image_array, boundaries, margin (default: 10)  ← ⚠️ TUNABLE

FOR each adjacent pair of boundaries:
    x_start = boundary[i] - margin   ← Expand left
    x_end = boundary[i+1] + margin   ← Expand right
    Clamp to image bounds
    Extract column slice

OUTPUT: list of (column_image, metadata)
```

## Debug

The preprocess.py script has a `--debug` flag to try to see how it's making the determination of where to snip.

## If the columns are getting truncated

|Parameter | Current Value | Effect | To Reduce Truncation |
|----------|---------------|--------|----------------------|
|`margin` in `split_into_columns`| 10 px | Padding added to each column edge | Increase to 20-30|
|`gutter_kernel` width | 15 px | How far text "smears" horizontally | Increase to 25-40 (makes gutters narrower, boundaries more centered)|
|`prominence` in `find_peaks` | 0.05 | How distinct a peak must be | Increase to 0.1-0.15 (fewer false boundaries)|
|`line_kernel` height | 100 px | Minimum length of detected divider lines | Increase if detecting noise |
|ROI top margins | 18%/5% | Excludes header area from analysis | Adjust if headers are throwing off detection |

The quickest fix, if columns are truncated is likely increasing `margin` from 10 to 25–30 pixels. If boundaries themselves are landing in the wrong spots, increase the `gutter_kernel` width or raise `prominence`.

For instance:

```python
def split_into_columns(image_array, boundaries, margin=10):  # ← Change to 20–30
```
This pads both sides equally. Quick fix, but also widens the left edge unnecessarily.

Or, you could change things asymmetrically:

```python
def split_into_columns(image_array, boundaries, left_margin=5, right_margin=25):
    ...
    x_start = max(0, boundaries[i] - left_margin)
    x_end = min(width, boundaries[i + 1] + right_margin)
```
This lets you pad the right edge more aggressively without over-expanding the left.

Or, you could shift the detected peaks rightward:

```python
peaks = [p + 10 for p in peaks]  # Shift boundaries 10px right
```

This recenters the boundaries in the actual gutter.
