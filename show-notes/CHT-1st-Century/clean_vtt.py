import re
import sys

def parse_vtt_dedup(vtt_path):
    """
    Parse YouTube auto-generated VTT with word-level timing.
    Handles the format where each cue appears twice:
    - Once with <c> tags for word timing
    - Once as plain text
    Also removes overlap between consecutive cues.
    """
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines
    lines = content.split('\n')
    
    # Extract plain text lines (skip WEBVTT header, timing, and <c> tag lines)
    plain_text_segments = []
    
    for line in lines:
        line = line.strip()
        
        # Skip header and empty lines
        if not line or line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
            continue
        
        # Skip timing lines
        if '-->' in line or re.match(r'^\d{2}:\d{2}:\d{2}', line):
            continue
        
        # Skip lines that are just position info
        if line.startswith('align:') or line.startswith('position:'):
            continue
        
        # Skip lines with <c> tags (word-level timing)
        if '<c>' in line or '<c.' in line:
            continue
        
        # Skip lines that are just whitespace markers
        if line == ' ' or not line:
            continue
        
        # This should be a plain text line
        # Clean up any remaining HTML tags
        clean = re.sub(r'<[^>]+>', '', line).strip()
        if clean:
            plain_text_segments.append(clean)
    
    # Now deduplicate by removing overlap between consecutive segments
    # YouTube VTT has overlap: each new segment starts with words from the end of the previous
    result_parts = []
    previous_text = ""
    
    for segment in plain_text_segments:
        # Skip exact duplicates
        if segment == previous_text:
            continue
        
        # Find overlap with previous segment
        # The new segment likely starts with some words from the end of the previous
        overlap_len = 0
        
        # Try to find the longest suffix of previous that matches prefix of current
        max_overlap = min(len(previous_text), len(segment))
        for i in range(max_overlap, 0, -1):
            if previous_text.endswith(segment[:i]):
                overlap_len = i
                break
        
        # Add only the non-overlapping part
        if overlap_len > 0:
            new_part = segment[overlap_len:].strip()
            if new_part:
                result_parts.append(new_part)
        else:
            result_parts.append(segment)
        
        previous_text = segment
    
    # Join all parts with spaces
    text = ' '.join(result_parts)
    
    # Clean up
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 clean_vtt.py <vtt_file>")
        sys.exit(1)
    
    vtt_file = sys.argv[1]
    text = parse_vtt_dedup(vtt_file)
    
    # Save to .txt file
    output_file = vtt_file.replace('.en.vtt', '_clean.txt').replace('.vtt', '_clean.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"Cleaned text saved to: {output_file}")
    print(f"Total characters: {len(text)}")

if __name__ == '__main__':
    main()
