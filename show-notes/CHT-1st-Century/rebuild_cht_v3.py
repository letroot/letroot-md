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
    # Remove "CHT" prefix with various separators (pipe, colon, space)
    t = re.sub(r'^CHT\s*[\|:\uff1a]?\s*', '', t)
    # Remove episode code (S2E1, S2E21, etc.) with various separators
    t = re.sub(r'\s*S2E\d+\s*[-:\uff1a]?\s*', ' ', t)
    # Remove trailing [video_id]
    t = re.sub(r'\s*\[.*?\]\s*$', '', t)
    # Clean whitespace
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

def split_sentences(text):
    sents = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [s.strip() for s in sents if s.strip()]

def detect_headings(sentences):
    breaks = []
    bible_books = ['acts','genesis','exodus','leviticus','numbers','deuteronomy','joshua','judges','ruth',
                   '1 samuel','2 samuel','1 kings','2 kings','1 chronicles','2 chronicles','ezra','nehemiah',
                   'esther','job','psalms','psalm','proverbs','ecclesiastes','isaiah','jeremiah','ezekiel',
                   'daniel','hosea','joel','amos','obadiah','jonah','micah','nahum','habakkuk','zephaniah',
                   'haggai','zechariah','malachi','matthew','mark','luke','john','romans','1 corinthians',
                   '2 corinthians','galatians','ephesians','philippians','colossians','1 thessalonians',
                   '2 thessalonians','1 timothy','2 timothy','titus','philemon','hebrews','james','1 peter',
                   '2 peter','1 john','2 john','3 john','jude','revelation']
    for i, sent in enumerate(sentences):
        low = sent.lower()
        for book in bible_books:
            pat = rf'\b{re.escape(book)}\s+(?:chapter\s+)?\d+'
            if re.match(pat, low):
                m = re.match(pat, low)
                ref = m.group(0).title()
                breaks.append((i, f"## {ref}"))
                break
        else:
            for tp in [r"(?:now\s+)?let[\s']*(?:us|'s)?\s+(?:look\s+at|turn\s+to|go\s+to|consider|delve\s+into|examine|read\s+(?:from\s+)?)\s+([^.]{5,50})",
                       r'(?:now\s+)?this\s+brings\s+us\s+to\s+([^.]{5,50})',
                       r'(?:now\s+)?we\s+(?:come\s+to|arrive\s+at|turn\s+to)\s+(?:the\s+)?([^.]{5,50})',
                       r"(?:now\s+)?i\s+want\s+to\s+(?:talk\s+about|look\s+at|share|show\s+you)\s+(?:the\s+)?([^.]{5,50})"]:
                m = re.match(tp, low)
                if m:
                    topic = m.group(1).strip()
                    topic = re.sub(r'\b(and|the|in|of|to|for|with|by|from|on|at|is|are|was|were|a|an)\b', '', topic, flags=re.IGNORECASE)
                    topic = re.sub(r'\s+', ' ', topic).strip()
                    if 4 < len(topic) < 40:
                        breaks.append((i, f"## {topic.title()}"))
                    break
    return breaks

def build_sections(sentences, breaks):
    if not breaks:
        return [(None, sentences)]
    sections = []
    current = []
    bi = 0
    for i, sent in enumerate(sentences):
        if bi < len(breaks) and i == breaks[bi][0]:
            if current:
                sections.append((breaks[bi][1], current))
            current = []
            bi += 1
        current.append(sent)
    if current:
        sections.append((breaks[bi][1] if bi < len(breaks) else None, current))
    return sections

def format_paragraphs(sents, max_s=5):
    paras = []
    cur = []
    for s in sents:
        cur.append(s)
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
    sents = split_sentences(text)
    breaks = detect_headings(sents)
    sections = build_sections(sents, breaks)
    lines = ['---', f'title: "{title}"', f'date: {date}',
             'tags: [podcast, church-history, cht]',
             f'url: "https://www.youtube.com/watch?v={vid}"',
             'type: solo', 'series: "1st Century"', f'episode: "{ep}"', '---', '',
             f'# {title}', '', '## Introduction', '']
    for heading, ss in sections:
        if heading:
            lines.append('')
            lines.append(heading)
            lines.append('')
        for p in format_paragraphs(ss):
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
