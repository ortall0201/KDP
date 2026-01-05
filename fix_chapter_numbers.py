#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Chapter Numbering in Manuscript
Replaces "CHAPTER undefined" with proper chapter numbers
"""

import re
import os
from pathlib import Path
from datetime import datetime

def find_latest_manuscript(manuscripts_dir):
    """Find the most recent manuscript file"""
    manuscripts = list(Path(manuscripts_dir).glob('*.txt'))

    if not manuscripts:
        raise FileNotFoundError(f"No manuscripts found in {manuscripts_dir}")

    # Sort by filename (which contains timestamp)
    manuscripts.sort(reverse=True)
    latest = manuscripts[0]

    print(f"Found latest manuscript: {latest.name}")
    return latest

def fix_chapter_numbers(manuscript_path, output_dir=None):
    """Replace CHAPTER undefined with numbered chapters"""

    # Read the manuscript
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all occurrences of "CHAPTER undefined"
    pattern = r'CHAPTER undefined'
    matches = re.findall(pattern, content, re.IGNORECASE)
    chapter_count = len(matches)

    print(f"\nFound {chapter_count} chapters with 'undefined'")

    if chapter_count == 0:
        print("No 'CHAPTER undefined' found. Manuscript may already be fixed.")
        return None

    # Replace each occurrence with proper chapter number
    chapter_number = 1

    def replace_with_number(match):
        nonlocal chapter_number
        replacement = f"CHAPTER {chapter_number}"
        print(f"  Replacing: {match.group(0)} -> {replacement}")
        chapter_number += 1
        return replacement

    fixed_content = re.sub(pattern, replace_with_number, content, flags=re.IGNORECASE)

    # Create output filename with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    output_filename = f"{timestamp}_fiction_FIXED.txt"

    # Determine output directory
    if output_dir is None:
        output_dir = manuscript_path.parent

    output_path = Path(output_dir) / output_filename

    # Save the fixed manuscript
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    # Verify the fix
    verify_count = len(re.findall(r'CHAPTER \d+', fixed_content))

    print(f"\n✓ Fixed manuscript saved: {output_path.name}")
    print(f"✓ Total chapters: {verify_count}")
    print(f"✓ File size: {len(fixed_content):,} characters")
    print(f"✓ Word count: {len(fixed_content.split()):,} words")

    # Show first few chapter headers
    print("\nFirst 5 chapter headers:")
    chapter_headers = re.findall(r'CHAPTER \d+', fixed_content)[:5]
    for header in chapter_headers:
        print(f"  - {header}")

    return output_path

def main():
    """Main function"""
    print("=" * 60)
    print("MANUSCRIPT CHAPTER NUMBER FIXER")
    print("=" * 60)

    # Configuration
    manuscripts_dir = Path("books/manuscripts")

    # Check if directory exists
    if not manuscripts_dir.exists():
        print(f"\nError: Directory not found: {manuscripts_dir}")
        print("Please run this script from the KDP root directory")
        return

    try:
        # Find latest manuscript
        latest_manuscript = find_latest_manuscript(manuscripts_dir)

        # Show file info
        file_size = latest_manuscript.stat().st_size
        print(f"File size: {file_size:,} bytes")

        # Count undefined chapters without printing content
        with open(latest_manuscript, 'r', encoding='utf-8') as f:
            content = f.read()
            undefined_count = len(re.findall(r'CHAPTER undefined', content, re.IGNORECASE))

        print(f"\nChapters with 'undefined': {undefined_count}")

        # Ask for confirmation
        response = input("\nFix chapter numbers in this manuscript? (yes/no): ").strip().lower()

        if response not in ['yes', 'y']:
            print("Cancelled.")
            return

        # Fix the manuscript
        fixed_path = fix_chapter_numbers(latest_manuscript, manuscripts_dir)

        if fixed_path:
            print("\n" + "=" * 60)
            print("SUCCESS! Manuscript chapters have been numbered.")
            print("=" * 60)
            print(f"\nOriginal: {latest_manuscript.name}")
            print(f"Fixed:    {fixed_path.name}")
            print("\nYou can now use the fixed manuscript in your workflow.")
        else:
            print("\nNo changes needed.")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
