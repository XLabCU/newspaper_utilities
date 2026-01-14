The pipeline can be invoked from the pipeline script, or you can run each script in turn.

We're working with pdfs from the BANQ of the Shawville Equity, published weekly since the 1880s in Shawville Quebec.

First we preprocess the images so that we reduce the size while retaining quality as best we can. Then, because of some regularities in how the oldest editions of the Equity were laid out, we use that to snip the thing into article-sized chunks. However, some of the potential OCR models have limitations on vertical height, so we also snip long pieces in half.

Then, we perform the OCR steps. There are some options here; we've tried to cover a variety that might work for you. The pipeline script assumes pytesseract as default. This writes the OCR to individual jsonL, so even if things should stop, you've still got most of your output. OCR is a memory hog.

The next step is to re-assemble snipped pieces back into full articles using `segment_articles.py`.

At this step, you could do whatever you want with the results. We also include three more scripts for tagging, for generating a timeline, and for some text analysis. For these last three, I was looking at issues of the Equity that included coverage of Jack the Ripper. I was wondering, 'what does it mean for that story to be republished in a small village in West Quebec?' which accounts for some of the idiosyncracy. But for present purposes, they can work as a model for moving the data along. Outputs are written as json files which could then be dumped into various visualiations.

# Tuning the Preprocessing Step

The preprocessing pipeline works like this:

### Main Loop

```
FOR each PDF:
    Extract pub_id and date from filename
    
    FOR each page (loaded one at a time for memory):
        Convert page to grayscale
        
        v_bounds = detect_vertical_columns(grayscale)
        
        FOR each column pair in v_bounds:
            x1, x2 = v_bounds[i], v_bounds[i+1]
            column_strip = image[:, x1:x2]          
            
            h_bounds = detect_horizontal_rules(column_strip)
            
            FOR each horizontal segment:
                Extract snippet
                Split if taller than 2000px
                Save as JPEG (quality=92)
                Discard if < 250KB (whitespace filter)
        
        Free memory, garbage collect
```

### Detect Vertical Columns

```
INPUT: img_gray

# Binarize
binary = adaptive_threshold(img_gray, GAUSSIAN, block=11, C=2)

# ROI: skip top/bottom 10%
roi = binary[height × 0.1 : height × 0.9]

# Extract vertical lines
v_kernel = rectangle(1px wide × 150px tall)       ← ⚠️ TUNABLE
v_lines = morphological_open(roi, v_kernel)

# Project vertically (sum each column)
v_proj = sum(v_lines, axis=0)
v_norm = v_proj / max(v_proj)

# Find local maxima above threshold
peaks = [x where v_norm[x] > 0.1                  ← ⚠️ TUNABLE threshold
         AND v_norm[x] > neighbors]

# Remove peaks too close together
min_col_width = image_width ÷ 12                  ← ⚠️ TUNABLE
clean_peaks = filter(peaks, spacing ≥ min_col_width)

OUTPUT: [0] + clean_peaks + [width]
```

### Detect Horizontal Rules

```
INPUT: column_gray

# Shave 5% off left/right edges                   ← ⚠️ TUNABLE
inner = column[:, 5% : 95%]

# Binarize
binary = adaptive_threshold(inner, GAUSSIAN, block=11, C=2)

# Horizontal line detection
kernel_width = column_width × 0.08                ← ⚠️ TUNABLE (8% of width)
h_kernel = rectangle(kernel_width × 1px tall)
detected = morphological_open(binary, h_kernel)
detected = morphological_close(detected, h_kernel, iterations=2)

# Project horizontally
y_proj = sum(detected, axis=1)
peak_thresh = max(y_proj) × 0.1                   ← ⚠️ TUNABLE

# Find peaks with 60px minimum spacing           ← ⚠️ TUNABLE
dividers = [y where y_proj[y] > peak_thresh, spaced ≥ 60px apart]

OUTPUT: [0] + dividers + [height]
```

In the main loop, you can add margins to the column detection like this:
```
# In main(), change:
column_strip = img_gray[:, x1:x2]

# To:
margin = 15  # Tunable
x1_safe = max(0, x1 - margin)
x2_safe = min(img_gray.shape[1], x2 + margin)
column_strip = img_gray[:, x1_safe:x2_safe]
```
You might want to experiment with asymetric edges:

```
left_margin, right_margin = 5, 20
x1_safe = max(0, x1 - left_margin)
x2_safe = min(img_gray.shape[1], x2 + right_margin)
column_strip = img_gray[:, x1_safe:x2_safe]
```
Or shift the peak detection a bit:
```
# After clean_peaks is built:
clean_peaks = [p + 10 for p in clean_peaks]  # Nudge boundaries into gutter center
```
### Quick Parameter Reference

|Parameter|Location|Current|Adjusting truncation along the vertical|
|-|-|-|-|
|Column margin|`main()` extraction|0|Add 15–25px|
|`v_kernel` height|`detect_vertical_columns`|150px|Increase if noisy|
|Peak threshold|`detect_vertical_columns`|0.1|Raise to reduce false positives|
|`min_col_width` divisor|`detect_vertical_columns`|w÷12|Lower divisor = wider minimum|


