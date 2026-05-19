#!/usr/bin/env python3
"""Rebuild CHT 1st Century podcast transcripts to match Pleros quality standards."""

import os, re, subprocess, glob

WORK_DIR = os.getcwd()  # Use current working directory

def extract_video_info(filename, fallback_num=None):
    m = re.search(r'\[([^\]]+)\]', filename)
    video_id = m.group(1) if m else None
    
    # Try S2E pattern (1st Century)
    m2 = re.search(r'[Ss]2[Ee](\d+)', filename)
    ep = f"S2E{m2.group(1)}" if m2 else None
    
    # Try Deep Dive #X pattern
    if not ep:
        m3 = re.search(r'[Dd]eep\s+[Dd]ive\s+#?\s*(\d+)', filename)
        ep = f"DD{m3.group(1)}" if m3 else None
    
    # Try Modern Church pattern (MC1, MC2, etc)
    if not ep:
        m4 = re.search(r'[Mm]odern\s+[Cc]hurch\s+#?\s*(\d+)', filename)
        ep = f"MC{m4.group(1)}" if m4 else None
    
    # Use fallback number if no pattern matched
    if not ep and fallback_num:
        ep = f"DD{fallback_num}"
    
    return video_id, ep

def fetch_metadata(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        r = subprocess.run(['yt-dlp', '--print', '%(title)s|||%(upload_date)s', url],
                          capture_output=True, text=True, timeout=60)
        if r.returncode == 0 and r.stdout.strip() and '|||' in r.stdout:
            t, d = r.stdout.strip().split('|||', 1)
            t = t.strip()
            d = d.strip()
            if len(d) == 8:
                d = f"{d[:4]}-{d[4:6]}-{d[6:8]}"
            return t, d if d else None
    except Exception as e:
        print(f"  Error: {e}")
    return None, None

def clean_title(yt_title):
    if not yt_title:
        return "Unknown"
    t = yt_title.strip()
    t = re.sub(r'^CHT\s*[\|:\uff1a]?\s*', '', t)
    t = re.sub(r'\s*S2E\d+\s*[-:\uff1a]?\s*', ' ', t)
    t = re.sub(r'\s*\[.*?\]\s*$', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def remove_intro(text):
    patterns = [
        r'\[Music\]\s*welcome to church history and theology,?\s*a study where we glean wisdom from those who came before us\.?\s*come,?\s*lay aside today\'?s concerns for a bit and join in a study of the church throughout the ages\.?\s*our forebears have shaped our faith in countless ways\.?\s*let\'?s go look into one of those influences today\s*(?:upon|on)\s*church history and\s*\[Music\]\s*theology\s*',
        r'welcome to church history and theology,?\s*a study where we glean wisdom from those who came before us\.?\s*come,?\s*lay aside today\'?s concerns for a bit and join in a study of the church throughout the ages\.?\s*our forebears have shaped our faith in countless ways\.?\s*let\'?s go look into one of those influences today\s*(?:upon|on)\s*church history',
        r'Welcome to Church History and Theology, a study where we glean wisdom from those who came before us\. Come, lay aside today\'s concerns for a bit and join in a study of the church throughout the ages\. Our forebears have shaped our faith in countless ways\. Let\'s go look into one of those influences today upon Church.*?(?=\b(?:Well|Greetings|Hello|Today|My name|Let\'?s get|welcome again))',
    ]
    for p in patterns:
        text = re.sub(p, '', text, count=1, flags=re.IGNORECASE | re.DOTALL)
    return text

def remove_outro(text):
    text = re.sub(r'\n\s*##\s*Closing\s*\n.*$', '', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'Thank you for listening to Church History and Theology\..*$', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"Don't forget to subscribe.*$", '', text, flags=re.IGNORECASE | re.MULTILINE)
    return text.strip()

def clean_text(text):
    text = re.sub(r'\[Music\]', '', text, flags=re.IGNORECASE)
    for f in [r'\buh\b', r'\bum\b', r'\bah\b', r'\beh\b', r'\ber\b', r'\bhmm\b', r'\bhuh\b']:
        text = re.sub(f, '', text, flags=re.IGNORECASE)
    for fp in [r'\s*,?\s*you know,?\s*', r'\s*,?\s*I mean,?\s*', r'\s*,?\s*sort of,?\s*',
               r'\s*,?\s*kind of,?\s*', r'\s*,?\s*I guess,?\s*', r'\s*,?\s*I suppose,?\s*',
               r'\s*,?\s*if you will,?\s*', r'\s*,?\s*if you like,?\s*', r'\s*,?\s*in a way,?\s*',
               r'\s*,?\s*right\?', r'\s*,?\s*okay\?']:
        text = re.sub(fp, ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)
    text = re.sub(r"(\w)\s+'\s*(\w)", r"\1'\2", text)
    text = re.sub(r"(\w)\s+'(\w)", r"\1'\2", text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def has_punctuation(text):
    """Check if text has sufficient punctuation for sentence splitting."""
    period_count = len(re.findall(r'\.', text))
    return period_count >= 10  # At least 10 periods suggests decent punctuation

def split_by_punctuation(text):
    """Split text using punctuation - works for well-punctuated content."""
    # Try standard split on period+space+capital
    sents = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    if len(sents) >= 10:
        return [s.strip() for s in sents if s.strip()]
    
    # Fallback: split on any period
    sents = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sents if s.strip()]

def split_no_punctuation(text):
    """Split ASR text with no punctuation into logical chunks."""
    chunks = []
    words = text.split()
    
    # For unpunctuated text, group words into logical "phrases"
    # Look for natural pause indicators: short words like "and", "but", "so" at start
    current = []
    
    i = 0
    while i < len(words):
        word = words[i]
        current.append(word)
        
        # Split points: when we hit certain keywords at word boundary
        # Look for phrases that indicate a new thought
        if len(current) >= 8:  # At least 8 words before considering split
            # Check if next word is a transition word
            next_word = words[i+1].lower() if i+1 < len(words) else ''
            transition_words = ['now', 'so', 'but', 'and', 'well', 'okay', 'alright', 
                               'first', 'next', 'then', 'finally', 'also', 'however',
                               'therefore', 'because', 'since', 'while', 'when', 'if']
            if next_word in transition_words:
                chunks.append(' '.join(current))
                current = []
            elif len(current) >= 15:  # Force split at 15 words
                chunks.append(' '.join(current))
                current = []
        i += 1
    
    if current:
        chunks.append(' '.join(current))
    
    # If still only 1-2 chunks, try splitting by every 10 words
    if len(chunks) <= 2:
        chunks = []
        for i in range(0, len(words), 10):
            chunk = ' '.join(words[i:i+10])
            if chunk.strip():
                chunks.append(chunk.strip())
    
    return chunks

def detect_headings(chunks):
    """Detect content-based section headings from chunk transitions."""
    breaks = []
    bible_books = ['acts','genesis','exodus','leviticus','numbers','deuteronomy','joshua','judges','ruth',
                   '1 samuel','2 samuel','1 kings','2 kings','1 chronicles','2 chronicles','ezra','nehemiah',
                   'esther','job','psalms','psalm','proverbs','ecclesiastes','isaiah','jeremiah','ezekiel',
                   'daniel','hosea','joel','amos','obadiah','jonah','micah','nahum','habakkuk','zephaniah',
                   'haggai','zechariah','malachi','matthew','mark','luke','john','romans','1 corinthians',
                   '2 corinthians','galatians','ephesians','philippians','colossians','1 thessalonians',
                   '2 thessalonians','1 timothy','2 timothy','titus','philemon','hebrews','james','1 peter',
                   '2 peter','1 john','2 john','3 john','jude','revelation']
    
    for i, chunk in enumerate(chunks):
        if len(chunk.split()) < 3:  # Skip short fragments
            continue
            
        lower = chunk.lower().strip()
        
        # Check for Bible references
        for book in bible_books:
            pattern = rf'^(?:the\s+)?{re.escape(book)}\s+(?:chapter\s+)?\d+'
            m = re.match(pattern, lower)
            if m:
                ref = m.group(0).replace('the ', '').title()
                breaks.append((i, f"## {ref}"))
                break
        else:
            # Check for topic transition phrases - more specific patterns
            patterns = [
                (r"^let['']*(?:us|'?s)?\s+(?:look|turn|go|consider|delve|examine|read|jump|start|begin)\s+(?:at|to|into|about|on)\s+(?:the\s+)?(\w+)", 'topic'),
                (r"^(?:now|so|well|okay)\s+(?:we|i|let)\s+(?:can|will|should|want|need|going|start|look|consider)", 'new_section'),
                (r"^(?:the|our|this|that)\s+(?:first|second|third|next|main|primary|key|important)\s+(?:point|thing|aspect|topic|issue|question)", 'new_section'),
                (r"^as\s+we\s+(?:look|consider|examine|delve|see|find|discover)", 'new_section'),
                (r"^(?:moving|let'?s)\s+(?:on|go)\s+(?:to|into|about)", 'new_section'),
            ]
            
            for pattern, ptype in patterns:
                m = re.match(pattern, lower)
                if m:
                    if ptype == 'topic' and m.group(1):
                        topic = m.group(1).title()
                        breaks.append((i, f"## {topic}"))
                    else:
                        # For new_section, use the chunk itself as heading
                        words = chunk.split()[:5]
                        if len(words) > 0:
                            heading = ' '.join(words[:4])
                            breaks.append((i, f"## {heading.title()}"))
                    break
    return breaks

def build_sections(chunks, breaks):
    if not breaks:
        return [(None, chunks)]
    sections = []
    current = []
    bi = 0
    for i, chunk in enumerate(chunks):
        if bi < len(breaks) and i == breaks[bi][0]:
            if current:
                sections.append((breaks[bi][1], current))
            current = []
            bi += 1
        current.append(chunk)
    if current:
        sections.append((breaks[bi][1] if bi < len(breaks) else None, current))
    return sections

def format_paragraphs(chunks, max_s=3):
    """Format into paragraphs of 2-4 sentences each."""
    paras = []
    cur = []
    for chunk in chunks:
        cur.append(chunk)
        if len(cur) >= max_s:
            paras.append(' '.join(cur))
            cur = []
    if cur:
        paras.append(' '.join(cur))
    return paras

def make_filename(ep_code, title):
    # Get directory name to determine prefix
    dir_name = os.path.basename(WORK_DIR)
    
    if ep_code and ep_code.startswith('S2E'):
        n = ep_code[3:]
        prefix = 's2e'
    elif ep_code and ep_code.startswith('DD'):
        n = ep_code[2:]
        if 'modern' in dir_name.lower():
            prefix = 'mc'
        else:
            prefix = 'dd'
    elif ep_code and ep_code.startswith('MC'):
        n = ep_code[2:]
        prefix = 'mc'
    else:
        n = '00'
        prefix = 'episode'
    
    t = title.lower()
    t = re.sub(r'[^\w\s-]', '', t)
    t = re.sub(r'\s+', '-', t)
    t = re.sub(r'-+', '-', t).strip('-')
    if len(t) > 50:
        t = t[:50].rsplit('-', 1)[0]
    return f"{prefix}{n}-{t}.md"

def process(filepath, fallback_num=None):
    fn = os.path.basename(filepath)
    vid, ep = extract_video_info(fn, fallback_num)
    if not vid or not ep:
        print(f"  Skip {fn}")
        return None
    print(f"  {ep} ({vid})")
    yt_title, date = fetch_metadata(vid)
    if not date:
        date = "2024-01-01"
    title = clean_title(yt_title) if yt_title else fn.replace('_clean.txt','').strip()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read()
    
    text = remove_intro(raw)
    text = remove_outro(text)
    text = clean_text(text)
    
    # Choose splitting strategy based on punctuation
    if has_punctuation(text):
        chunks = split_by_punctuation(text)
    else:
        chunks = split_no_punctuation(text)
    
    breaks = detect_headings(chunks)
    sections = build_sections(chunks, breaks)
    
    # Determine series name based on episode code or directory name
    dir_name = os.path.basename(WORK_DIR)
    if ep and ep.startswith('S2E'):
        series_name = "1st Century"
    elif ep and ep.startswith('DD'):
        if 'modern' in dir_name.lower():
            series_name = "Modern Church"
        else:
            series_name = "Deep Dives"
    elif ep and ep.startswith('MC'):
        series_name = "Modern Church"
    else:
        series_name = dir_name if dir_name else "CHT"
    
    lines = ['---', f'title: "{title}"', f'date: {date}',
             'tags: [podcast, church-history, cht]',
             f'url: "https://www.youtube.com/watch?v={vid}"',
             'type: solo', 
             f'series: "{series_name}"',
             f'episode: "{ep}"', '---', '',
             f'# {title}', '', '## Introduction', '']
    
    for heading, sec_chunks in sections:
        if heading:
            lines.append('')
            lines.append(heading)
            lines.append('')
        for p in format_paragraphs(sec_chunks):
            lines.append(p)
            lines.append('')
    
    lines.append('')
    lines.append('## Closing')
    lines.append('')
    return '\n'.join(lines), make_filename(ep, title)

def main():
    files = sorted(glob.glob(os.path.join(WORK_DIR, "*_clean.txt")))
    print(f"Found {len(files)} files")
    results = []
    for i, fp in enumerate(files, 1):
        r = process(fp, fallback_num=i)
        if r:
            content, outfn = r
            outpath = os.path.join(WORK_DIR, outfn)
            with open(outpath, 'w', encoding='utf-8') as f:
                f.write(content)
            results.append(outfn)
            print(f"    -> {outfn}")
    print(f"\nCreated {len(results)} files")

if __name__ == '__main__':
    main()
