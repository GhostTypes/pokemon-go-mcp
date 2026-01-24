#!/usr/bin/env python3
"""
Clean mypy documentation markdown by removing navigation and footer content.
Keeps only the main documentation content.
"""

import re
import sys

def clean_mypy_markdown(content):
    """
    Clean mypy documentation markdown content.
    
    Removes:
    - Navigation header (everything before first H1 heading)
    - Footer navigation (Next/Previous links)
    - Copyright notice
    - "On this page" table of contents
    - Permalink anchors (¶) in headings
    """
    lines = content.split('\n')
    
    # Find the start of actual content (first H1 heading)
    start_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('# ') and '[¶]' in line:
            start_idx = i
            break
    
    # Find the end of actual content
    # Look for ALL footer markers and use the earliest one
    footer_markers = []
    
    for i in range(len(lines) - 1, start_idx, -1):
        line = lines[i].strip()
        
        # Look for standalone navigation markers
        if line in ['[Next', '[Previous']:
            footer_markers.append(('nav', i))
        
        # Look for copyright
        if 'Copyright ©' in line:
            footer_markers.append(('copyright', i))
        
        # Look for "On this page" table of contents
        if line == 'On this page':
            footer_markers.append(('toc', i))
    
    # Use the earliest footer marker found
    if footer_markers:
        # Sort by line number and take the first (earliest)
        footer_markers.sort(key=lambda x: x[1])
        marker_type, end_idx = footer_markers[0]
        
        # Remove trailing blank lines before the footer marker
        while end_idx > start_idx and lines[end_idx - 1].strip() == '':
            end_idx -= 1
    else:
        end_idx = len(lines)
    
    # Extract the main content
    cleaned_lines = lines[start_idx:end_idx]
    
    # Remove permalink anchors from headings
    # Pattern: [¶](#some-anchor "Link to this heading")
    permalink_pattern = r'\[¶\]\(#[^)]+\s+"[^"]+"\)'
    
    cleaned_lines = [re.sub(permalink_pattern, '', line) for line in cleaned_lines]
    
    # Join back together
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Clean up excessive blank lines (more than 2 consecutive)
    cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)
    
    # Strip leading/trailing whitespace
    cleaned_content = cleaned_content.strip()
    
    return cleaned_content

def main():
    if len(sys.argv) < 2:
        print("Usage: clean_markdown.py <input_file> [output_file]", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Read input
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Clean the content
    cleaned = clean_mypy_markdown(content)
    
    # Output
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f"Cleaned content saved to: {output_file}", file=sys.stderr)
    else:
        print(cleaned)

if __name__ == "__main__":
    main()
