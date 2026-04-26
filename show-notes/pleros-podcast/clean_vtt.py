import re

def clean_vtt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    text_lines = []
    prev_line = ""
    for line in lines:
        line = line.strip()
        if not line or line == "WEBVTT" or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3}', line):
            continue
        line = re.sub(r'<[^>]+>', '', line)
        if line and line != prev_line:
            text_lines.append(line)
            prev_line = line
            
    return ' '.join(text_lines)

text = clean_vtt('ep114.en.vtt')
with open('ep114_clean.txt', 'w', encoding='utf-8') as f:
    f.write(text)
