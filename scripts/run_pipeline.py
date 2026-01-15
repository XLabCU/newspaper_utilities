#!/usr/bin/env python3
"""
Pipeline Runner Script - Newspaper Utilities
Executes the full data processing sequence with configurable parameters.
Defaults to Tesseract OCR for stability.
"""

import sys
import subprocess
import argparse
from pathlib import Path

<<<<<<< HEAD

def run_script(script_name, extra_args=None):
    """
    Run a Python script and handle errors.

    Args:
        script_name: Name of the script to run
        extra_args: List of extra arguments to pass to the script
    """
=======
def run_script(script_name, script_args=None):
    """Run a Python script and handle errors"""
>>>>>>> origin/claude/review-ocr-pipeline-uRC5D
    script_path = Path(__file__).parent / script_name
    print(f"\n{'=' * 60}")
    print(f"Running: {script_name}")
    print('=' * 60)

    # Build command
    cmd = [sys.executable, str(script_path)]
    if extra_args:
        cmd.extend(extra_args)

    try:
<<<<<<< HEAD
=======
        # Build command with optional arguments
        cmd = [sys.executable, str(script_path)]
        if script_args:
            cmd.extend(script_args)

        # We use capture_output=False so you can see the
        # real-time progress prints from the OCR and Preprocessor
>>>>>>> origin/claude/review-ocr-pipeline-uRC5D
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"✓ {script_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {script_name} failed with error")
        print(f"Error: {e}")
        return False


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Run the newspaper OCR and analysis pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--ocr-engine',
        choices=['tesseract', 'paddleocr', 'gemini', 'surya', 'ocrmac'],
        default='tesseract',
        help='OCR engine to use: "tesseract" (default/stable), "paddleocr" (deep learning), "gemini" (API), or "surya" (batch)'
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration file (default: use built-in defaults)'
    )

    args = parser.parse_args()

    # Prepare config arguments to pass to scripts
    config_args = []
    if args.config:
        config_args = ['--config', args.config]

    print("=" * 60)
    print("NEWSPAPER UTILITIES - DATA PROCESSING PIPELINE")
    print("=" * 60)
    print(f"OCR Engine: {args.ocr_engine.upper()}")
    if args.config:
        print(f"Configuration: {args.config}")
    else:
        print("Configuration: Default (built-in)")
    print("=" * 60)

    # Logic to select Step 2 script and determine OCR output filename
    if args.ocr_engine == "gemini":
        ocr_script = "process_pdfs_gemini.py"
        ocr_output_file = "ocr_output.json"
    elif args.ocr_engine == "paddleocr":
        ocr_script = "process_pdfs.py"
        ocr_output_file = "ocr_output.jsonl"
    elif args.ocr_engine == "surya":
        ocr_script = "process_images_surya_batch.py"
<<<<<<< HEAD
    elif args.ocr_engine == "ocrmac":
        ocr_script = "process_images_ocrmac.py"
=======
        ocr_output_file = "ocr_output.jsonl"
>>>>>>> origin/claude/review-ocr-pipeline-uRC5D
    else:
        ocr_script = "process_pdfs_tesseract.py"
        ocr_output_file = "ocr_output_tesseract.jsonl"

<<<<<<< HEAD
    # The Pipeline Sequence
    # Steps that don't use config: preprocess, OCR, segment
    # Steps that use config: tag, timeline, analyze, entities, dashboard
    steps = [
        ("preprocess.py", None),           # Step 1: 300DPI Snippets
        (ocr_script, None),                # Step 2: OCR Engine
        ("segment_articles.py", None),     # Step 3: Article Grouping
        ("tag_articles.py", config_args),  # Step 4: Thematic Classification (configurable)
        ("generate_timeline.py", config_args),  # Step 5: Timeline Analysis (configurable)
        ("analyze_text.py", config_args),  # Step 6: Text Analysis (configurable)
        ("extract_entities_enhanced.py", config_args),  # Step 7: Entity Extraction & Network Analysis (optional)
        ("generate_dashboard.py", config_args),  # Step 8: Generate HTML Dashboard (optional)
=======
    # The Canonical 6-Step Sequence
    # Note: scripts can be tuples of (script_name, [args])
    scripts = [
        ("preprocess.py", None),                              # Step 1: 300DPI Snippets + Split at 2000px
        (ocr_script, None),                                   # Step 2: The chosen OCR Engine (Default: Tesseract)
        ("segment_articles.py", ["--input", ocr_output_file]), # Step 3: JSONL -> Article Grouping
        ("tag_articles.py", None),                            # Step 4: Thematic/Ripper Classification
        ("generate_timeline.py", None),                       # Step 5: Historical News Lag Analysis
        ("analyze_text.py", None)                             # Step 6: Linguistic Sensationalism Index
>>>>>>> origin/claude/review-ocr-pipeline-uRC5D
    ]

    success_count = 0

<<<<<<< HEAD
    for script, extra_args in steps:
        if run_script(script, extra_args):
=======
    for script_info in scripts:
        if isinstance(script_info, tuple):
            script, script_args = script_info
        else:
            script, script_args = script_info, None

        if run_script(script, script_args):
>>>>>>> origin/claude/review-ocr-pipeline-uRC5D
            success_count += 1
        else:
            print(f"\nPipeline stopped due to error in {script}")
            print("Troubleshooting: Check memory usage or file paths.")
            sys.exit(1)

    print("\n" + "=" * 60)
    print(f"PIPELINE COMPLETE!")
    print(f"Successfully completed {success_count}/{len(steps)} steps")
    print("=" * 60)
    print("\nGenerated data files:")
    print("  - data/raw/ocr_output_*.jsonl        (Raw OCR)")
    print("  - data/processed/articles.json       (Segments)")
    print("  - data/processed/tagged_articles.json (Tagged Data)")
    print("  - data/processed/timeline.json       (Timeline/Correlation)")
    print("  - data/processed/text_analysis.json  (Linguistic Stats)")
    print("  - data/processed/entities.json       (Entities)")
    print("  - data/processed/entity_network.json (Network Data)")
    print("  - dashboard/index.html               (Interactive Dashboard)")
    print("\nReady for visualization and analysis!")
    print("\nTo view the dashboard, open:")
    print("  dashboard/index.html in your web browser")


if __name__ == "__main__":
    main()
