#!/usr/bin/env python3
"""
Step 2: Apple Vision OCR (ocrmac) - M1 Optimized Edition
- Uses Apple's Native Vision Framework via the ANE (Apple Neural Engine).
- Zero Segmentation Faults / No OpenMP hangs.
- Provides bounding boxes in [x, y, w, h] format.
"""

import json
from ocrmac import ocrmac
from pathlib import Path
import os
import gc

def main():
    # Setup Paths
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    preprocessed_dir = project_root / "data" / "preprocessed"
    output_dir = project_root / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = preprocessed_dir / "all_metadata.json"
    if not metadata_path.exists():
        print(f"Error: {metadata_path} not found.")
        return

    with open(metadata_path, 'r') as f:
        all_metadata = json.load(f)

    output_file = output_dir / "ocr_output_vision.jsonl"
    print(f"Starting Apple Vision OCR... Streaming to: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f_out:
        for pdf_meta in all_metadata:
            pub_name = pdf_meta.get('source_pdf')
            
            for page in pdf_meta.get('pages', []):
                page_num = page.get('page_num')
                print(f"Processing {pub_name} - Page {page_num}...")

                for snip in page.get('snippets', []):
                    img_path = snip['path']
                    if not os.path.exists(img_path): continue

                    try:
                        # ocrmac.OCR takes a file path string
                        # it returns a list of tuples: (text, confidence, [x, y, w, h])
                        # The [x,y,w,h] are top-left pixel coordinates.
                        ocr_engine = ocrmac.OCR(img_path)
                        annotations = ocr_engine.recognize()
                        
                        for text, conf, bbox in annotations:
                            text = text.strip()
                            
                            if text:
                                x_off = snip['x_offset']
                                y_off = snip['y_offset']
                                
                                # ocrmac bbox is [x, y, w, h]
                                b_x, b_y, b_w, b_h = bbox

                                # Construct global coordinates based on offsets
                                entry = {
                                    "pub": pub_name,
                                    "page": page_num,
                                    "col": snip.get('column', 0),
                                    "text": text,
                                    "conf": round(conf, 3), # Vision already uses 0-1.0 scale
                                    "bbox": [
                                        int(b_x + x_off),
                                        int(b_y + y_off),
                                        int(b_w),
                                        int(b_h)
                                    ]
                                }
                                f_out.write(json.dumps(entry, ensure_ascii=False) + "\n")
                        
                        # Flush for streaming safety
                        f_out.flush()

                    except Exception as e:
                        print(f"Error on snippet {img_path}: {e}")
                    
                    finally:
                        # Clean up
                        if 'ocr_engine' in locals(): del ocr_engine
                        gc.collect()

    print(f"\n✓ Apple Vision OCR Complete. Results in {output_file}")

if __name__ == "__main__":
    main()