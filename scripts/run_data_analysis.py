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


def run_script(script_name, extra_args=None):
    """
    Run a Python script and handle errors.

    Args:
        script_name: Name of the script to run
        extra_args: List of extra arguments to pass to the script
    """
    script_path = Path(__file__).parent / script_name
    print(f"\n{'=' * 60}")
    print(f"Running: {script_name}")
    print('=' * 60)

    # Build command
    cmd = [sys.executable, str(script_path)]
    if extra_args:
        cmd.extend(extra_args)

    try:
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


def find_ocr_output_file():
    """
    Auto-detect the most recent OCR output file in data/raw/.

    Returns:
        str: Filename of the OCR output (just the filename, not full path)
    """
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    raw_dir = project_root / "data" / "raw"

    if not raw_dir.exists():
        print(f"Error: {raw_dir} does not exist")
        return None

    # Look for OCR output files (both .jsonl and .json)
    ocr_files = list(raw_dir.glob("ocr_output*.jsonl")) + list(raw_dir.glob("ocr_output*.json"))

    if not ocr_files:
        print(f"Error: No OCR output files found in {raw_dir}")
        print("Looking for files matching: ocr_output*.jsonl or ocr_output*.json")
        return None

    # Sort by modification time, most recent first
    ocr_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    most_recent = ocr_files[0]

    print(f"Auto-detected OCR file: {most_recent.name}")
    if len(ocr_files) > 1:
        print(f"  (Found {len(ocr_files)} OCR files, using most recent)")

    return most_recent.name


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Run the newspaper analysis part of pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration file (default: use built-in defaults)'
    )
    parser.add_argument(
        '--ocr-file',
        type=str,
        default=None,
        help='OCR output filename to use (default: auto-detect most recent)'
    )

    args = parser.parse_args()

    # Prepare config arguments to pass to scripts
    config_args = []
    if args.config:
        config_args = ['--config', args.config]

    print("=" * 60)
    print("NEWSPAPER UTILITIES - DATA ANALYSIS PIPELINE")
    print("=" * 60)

    if args.config:
        print(f"Configuration: {args.config}")
    else:
        print("Configuration: Default (built-in)")
    print("=" * 60)

    # Auto-detect or use specified OCR file
    if args.ocr_file:
        ocr_filename = args.ocr_file
        print(f"Using specified OCR file: {ocr_filename}")
    else:
        ocr_filename = find_ocr_output_file()
        if not ocr_filename:
            print("\nError: Could not find OCR output file.")
            print("Please run OCR processing first, or specify --ocr-file")
            sys.exit(1)

    print("=" * 60)

    # The Pipeline Sequence when the ocr'ing has already been done.
    #
    # Steps that use config: tag, timeline, analyze, entities, dashboard
    steps = [
        ("segment_articles.py", ["--input", ocr_filename]),  # Step 3: Article Grouping (with auto-detected file)
        ("tag_articles.py", config_args),  # Step 4: Thematic Classification (configurable)
        ("generate_timeline.py", config_args),  # Step 5: Timeline Analysis (configurable)
        ("analyze_text.py", config_args),  # Step 6: Text Analysis (configurable)
        ("extract_entities_enhanced.py", config_args),  # Step 7: Entity Extraction & Network Analysis (optional)
        ("generate_dashboard.py", config_args),  # Step 8: Generate HTML Dashboard (optional)
    ]

    success_count = 0

    for script, extra_args in steps:
        if run_script(script, extra_args):
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
    print(" or run python serve.py and go to https://localhost:8000")


if __name__ == "__main__":
    main()
