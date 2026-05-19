#!/usr/bin/env python3
"""Rebuild CHT 1st Century podcast transcripts to match Pleros quality standards."""

import os, re, subprocess, glob

WORK_DIR = "/Users/letroot/Documents/notes/obsidian-vaults/letroot-md/show-notes/CHT-1st-Century"

def extract_video_info(filename):
    m = re.search(r'\[([^\]]+)\]', filename)
    video_id = m.group(1) if m else None
    m2 = re.search(r'[Ss]2[Ee](\d+)', filename)
    ep = f"S2E{m2.group(1)}" if m2 else None
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

def split_into_chunks(text):
    """Split text into logical chunks/sentences - more intelligent approach."""
    chunks = []
    
    # First, try splitting on actual punctuation
    # Pattern: period/exclamation/question mark followed by space and capital
    s1 = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    if len(s1) >= 10:
        return [s.strip() for s in s1 if s.strip()]
    
    # Second, try split on period followed by any word
    s2 = re.split(r'(?<=[.!?])\s+', text)
    if len(s2) >= 10:
        return [s.strip() for s in s2 if s.strip()]
    
    # Third, split on sentence-like markers for ASR
    # Look for: period + capital OR question + capital OR clear paragraph breaks
    # Also look for "and" or "but" at start of sentence after a break
    s3 = re.split(r'(\.)\s+(?=[A-Z])', text)
    if len(s3) >= 10:
        return [s.strip() for s in s3 if s.strip()]
    
    # For ASR without punctuation - split by logical phrases
    # Look for patterns like "word. word" where first word is short
    # More robust: split on any of these: . ? ! followed by space
    s4 = re.split(r'[.!?]\s+', text)
    if len(s4) >= 10:
        return [s.strip() for s in s4 if s.strip()]
    
    # Last resort: split by very long phrases (50-100 chars)
    # Group words until we hit ~60 characters
    words = text.split()
    current = []
    for word in words:
        current.append(word)
        if len(' '.join(current)) > 55:  # ~55 chars per chunk
            chunks.append(' '.join(current))
            current = []
    if current:
        chunks.append(' '.join(current))
    
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
        lower = chunk.lower().strip()
        
        # Skip very short chunks (probably not sentence starts)
        if len(chunk.split()) < 3:
            continue
            
        # Look for Bible references at start of chunk
        for book in bible_books:
            pattern = rf'^(?:the\s+)?{re.escape(book)}\s+(?:chapter\s+)?\d+'
            m = re.match(pattern, lower)
            if m:
                ref = m.group(0).replace('the ', '').title()
                breaks.append((i, f"## {ref}"))
                break
        else:
            # Look for explicit topic transitions at chunk start
            transitions = [
                r"^(?:now|so|well|okay|alright|first|second|third|next|finally)\s+",
                r"^let['']*(?:us|'?s)?\s+(?:look|turn|go|consider|delve|examine|read|jump)",
                r"^(?:this|that)\s+(?:brings?|leads?|leads?)\s+(?:us|me)\s+to",
                r"^(?:moving|let'?s)\s+(?:on|go)\s+to",
                r"^(?:the|our|my)\s+(?:first|next|main|primary)\s+(?:point|thing|aspect)",
                r"^as\s+we\s+(?:look|consider|examine|delve)",
                r"^(?:now|so|well)\s+(?:we|i)\s+(?:can|will|should|want|need)",
            ]
            for pattern in transitions:
                if re.match(pattern, lower):
                    # Try to extract a meaningful heading from the context
                    # Look for key nouns after the transition
                    words = lower.split()
                    if len(words) > 2:
                        # Find the main topic (typically 3-10 words into the chunk)
                        potential = ' '.join(words[1:6]) if len(words) > 5 else ' '.join(words[1:])
                        # Clean up
                        potential = re.sub(r'^(the|a|an|and|or|but|to|of|for|in|on|at|by)\s+', '', potential)
                        if 3 < len(potential) < 35:
                            breaks.append((i, f"## {potential.title()}"))
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
    """Format into paragraphs of 2-4 sentences each (matching Pleros standard)."""
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
    m = re.search(r'[Ss]2[Ee](\d+)', ep_code)
    n = m.group(1) if m else '00'
    t = title.lower()
    t = re.sub(r'[^\w\s-]', '', t)
    t = re.sub(r'\s+', '-', t)
    t = re.sub(r'-+', '-', t).strip('-')
    if len(t) > 50:
        t = t[:50].rsplit('-', 1)[0]
    return f"s2e{n}-{t}.md"

def process(filepath):
    fn = os.path.basename(filepath)
    vid, ep = extract_video_info(fn)
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
    chunks = split_into_chunks(text)
    breaks = detect_headings(chunks)
    sections = build_sections(chunks, breaks)
    lines = ['---', f'title: "{title}"', f'date: {date}',
             'tags: [podcast, church-history, cht]',
             f'url: "https://www.youtube.com/watch?v={vid}"',
             'type: solo', 'series: "1st Century"', f'episode: "{ep}"', '---', '',
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
    for fp in files:
        r = process(fp)
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
