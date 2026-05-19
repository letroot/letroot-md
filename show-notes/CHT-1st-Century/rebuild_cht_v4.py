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

def fix_asr_artifacts(text):
    """Fix common ASR transcription errors."""
    # Fix "he" -> "the" when followed by common nouns (ASR drops the 't')
    he_fixes = ['Roman', 'first', 'church', 'New', 'same', 'way', 'early', 'Lord', 'Spirit',
                'book', 'gospel', 'apostles', 'apostle', 'Bible', 'scriptures', 'year', 'time',
                'day', 'world', 'gathering', 'Christians', 'people', 'rest', 'fact', 'idea',
                'reason', 'point', 'beginning', 'end', 'very', 'most', 'only', 'other', 'next',
                'last', 'whole', 'entire', 'exact', 'right', 'left', 'top', 'bottom', 'middle',
                'same', 'way', 'place', 'thing', 'things', 'matter', 'question', 'answer',
                'truth', 'word', 'words', 'text', 'passage', 'verse', 'chapter', 'context',
                'evidence', 'record', 'account', 'story', 'history', 'teaching', 'lesson',
                'message', 'letter', 'epistle', 'writing', 'writings', 'document', 'source',
                'tradition', 'practice', 'custom', 'belief', 'faith', 'hope', 'love', 'grace',
                'mercy', 'peace', 'joy', 'power', 'authority', 'kingdom', 'heaven', 'earth',
                'city', 'house', 'home', 'room', 'door', 'window', 'wall', 'floor', 'ceiling',
                'table', 'chair', 'bed', 'lamp', 'light', 'dark', 'night', 'morning', 'evening',
                'afternoon', 'hour', 'minute', 'moment', 'season', 'century', 'generation',
                'age', 'period', 'era', 'epoch', 'age', 'time', 'times', 'periods', 'days',
                'weeks', 'months', 'years', 'decades', 'centuries', 'millennia']
    for word in he_fixes:
        text = re.sub(rf'\bhe\b\s+{word}', f'the {word}', text, flags=re.IGNORECASE)

    # Fix missing first letters from ASR
    fixes = {
        r'\b([b-df-hj-np-tv-z])xperience\b': r'\1experience',
        r'\b([b-df-hj-np-tv-z])esigned\b': r'\1designed',
        r'\b([b-df-hj-np-tv-z])nominations\b': r'\1denominations',
        r'\b([b-df-hj-np-tv-z])iversity\b': r'\1diversity',
        r'\b([b-df-hj-np-tv-z])uper\b': r'\1super',
        r'\b([b-df-hj-np-tv-z])ntire\b': r'\1entire',
        r'\b([b-df-hj-np-tv-z])xpectation\b': r'\1expectation',
        r'\b([b-df-hj-np-tv-z])xpecting\b': r'\1expecting',
        r'\b([b-df-hj-np-tv-z])xperienced\b': r'\1experienced',
        r'\b([b-df-hj-np-tv-z])pression\b': r'\1expression',
        r'\b([b-df-hj-np-tv-z])press\b': r'\1express',
        r'\b([b-df-hj-np-tv-z])plain\b': r'\1explain',
        r'\b([b-df-hj-np-tv-z])tudy\b': r'\1study',
        r'\b([b-df-hj-np-tv-z])hurch\b': r'\1church',
        r'\b([b-df-hj-np-tv-z])istory\b': r'\1history',
        r'\b([b-df-hj-np-tv-z])heology\b': r'\1theology',
        r'\b([b-df-hj-np-tv-z])ellowship\b': r'\1fellowship',
        r'\b([b-df-hj-np-tv-z])ellow\b': r'\1fellow',
        r'\b([b-df-hj-np-tv-z])reaking\b': r'\1breaking',
        r'\b([b-df-hj-np-tv-z])reak\b': r'\1break',
        r'\b([b-df-hj-np-tv-z])elieve\b': r'\1believe',
        r'\b([b-df-hj-np-tv-z])elievers\b': r'\1believers',
        r'\b([b-df-hj-np-tv-z])elief\b': r'\1belief',
        r'\b([b-df-hj-np-tv-z])eloved\b': r'\1beloved',
        r'\b([b-df-hj-np-tv-z])etween\b': r'\1between',
        r'\b([b-df-hj-np-tv-z])ecause\b': r'\1because',
        r'\b([b-df-hj-np-tv-z])efore\b': r'\1before',
        r'\b([b-df-hj-np-tv-z])esides\b': r'\1besides',
        r'\b([b-df-hj-np-tv-z])less\b': r'\1bless',
        r'\b([b-df-hj-np-tv-z])lessed\b': r'\1blessed',
        r'\b([b-df-hj-np-tv-z])ody\b': r'\1body',
        r'\b([b-df-hj-np-tv-z])odies\b': r'\1bodies',
        r'\b([b-df-hj-np-tv-z])lood\b': r'\1blood',
        r'\b([b-df-hj-np-tv-z])ring\b': r'\1bring',
        r'\b([b-df-hj-np-tv-z])rings\b': r'\1brings',
        r'\b([b-df-hj-np-tv-z])rought\b': r'\1brought',
        r'\b([b-df-hj-np-tv-z])uild\b': r'\1build',
        r'\b([b-df-hj-np-tv-z])uilding\b': r'\1building',
        r'\b([b-df-hj-np-tv-z])uilt\b': r'\1built',
        r'\b([b-df-hj-np-tv-z])ver\b': r'\1ever',
        r'\b([b-df-hj-np-tv-z])veryone\b': r'\1everyone',
        r'\b([b-df-hj-np-tv-z])verywhere\b': r'\1everywhere',
        r'\b([b-df-hj-np-tv-z])verything\b': r'\1everything',
        r'\b([b-df-hj-np-tv-z])very\b': r'\1every',
        r'\b([b-df-hj-np-tv-z])arly\b': r'\1early',
        r'\b([b-df-hj-np-tv-z])arly\b': r'\1early',
        r'\b([b-df-hj-np-tv-z])xpress\b': r'\1express',
        r'\b([b-df-hj-np-tv-z])xpressed\b': r'\1expressed',
        r'\b([b-df-hj-np-tv-z])xpression\b': r'\1expression',
        r'\b([b-df-hj-np-tv-z])pect\b': r'\1expect',
        r'\b([b-df-hj-np-tv-z])pected\b': r'\1expected',
        r'\b([b-df-hj-np-tv-z])xpect\b': r'\1expect',
        r'\b([b-df-hj-np-tv-z])xpects\b': r'\1expects',
        r'\b([b-df-hj-np-tv-z])xpectation\b': r'\1expectation',
        r'\b([b-df-hj-np-tv-z])xpectations\b': r'\1expectations',
        r'\b([b-df-hj-np-tv-z])xplain\b': r'\1explain',
        r'\b([b-df-hj-np-tv-z])xplained\b': r'\1explained',
        r'\b([b-df-hj-np-tv-z])xplains\b': r'\1explains',
        r'\b([b-df-hj-np-tv-z])xplaining\b': r'\1explaining',
        r'\b([b-df-hj-np-tv-z])planation\b': r'\1explanation',
        r'\b([b-df-hj-np-tv-z])xploration\b': r'\1exploration',
        r'\b([b-df-hj-np-tv-z])xplore\b': r'\1explore',
        r'\b([b-df-hj-np-tv-z])xplored\b': r'\1explored',
        r'\b([b-df-hj-np-tv-z])xplores\b': r'\1explores',
        r'\b([b-df-hj-np-tv-z])xpanding\b': r'\1expanding',
        r'\b([b-df-hj-np-tv-z])xpand\b': r'\1expand',
        r'\b([b-df-hj-np-tv-z])xpanded\b': r'\1expanded',
        r'\b([b-df-hj-np-tv-z])poken\b': r'\1spoken',
        r'\b([b-df-hj-np-tv-z])peak\b': r'\1speak',
        r'\b([b-df-hj-np-tv-z])peaks\b': r'\1speaks',
        r'\b([b-df-hj-np-tv-z])peaking\b': r'\1speaking',
        r'\b([b-df-hj-np-tv-z])peech\b': r'\1speech',
        r'\b([b-df-hj-np-tv-z])pirit\b': r'\1spirit',
        r'\b([b-df-hj-np-tv-z])pirits\b': r'\1spirits',
        r'\b([b-df-hj-np-tv-z])pecial\b': r'\1special',
        r'\b([b-df-hj-np-tv-z])pecific\b': r'\1specific',
        r'\b([b-df-hj-np-tv-z])pecifically\b': r'\1specifically',
        r'\b([b-df-hj-np-tv-z])till\b': r'\1still',
        r'\b([b-df-hj-np-tv-z])tand\b': r'\1stand',
        r'\b([b-df-hj-np-tv-z])tands\b': r'\1stands',
        r'\b([b-df-hj-np-tv-z])tanding\b': r'\1standing',
        r'\b([b-df-hj-np-tv-z])tood\b': r'\1stood',
        r'\b([b-df-hj-np-tv-z])tory\b': r'\1story',
        r'\b([b-df-hj-np-tv-z])tories\b': r'\1stories',
        r'\b([b-df-hj-np-tv-z])trong\b': r'\1strong',
        r'\b([b-df-hj-np-tv-z])tronger\b': r'\1stronger',
        r'\b([b-df-hj-np-tv-z])trongest\b': r'\1strongest',
        r'\b([b-df-hj-np-tv-z])tructure\b': r'\1structure',
        r'\b([b-df-hj-np-tv-z])tructures\b': r'\1structures',
        r'\b([b-df-hj-np-tv-z])tudent\b': r'\1student',
        r'\b([b-df-hj-np-tv-z])tudents\b': r'\1students',
        r'\b([b-df-hj-np-tv-z])tudy\b': r'\1study',
        r'\b([b-df-hj-np-tv-z])tudies\b': r'\1studies',
        r'\b([b-df-hj-np-tv-z])tudied\b': r'\1studied',
        r'\b([b-df-hj-np-tv-z])tudying\b': r'\1studying',
        r'\b([b-df-hj-np-tv-z])uccess\b': r'\1success',
        r'\b([b-df-hj-np-tv-z])uccessful\b': r'\1successful',
        r'\b([b-df-hj-np-tv-z])uccessfully\b': r'\1successfully',
        r'\b([b-df-hj-np-tv-z])uffer\b': r'\1suffer',
        r'\b([b-df-hj-np-tv-z])uffered\b': r'\1suffered',
        r'\b([b-df-hj-np-tv-z])uffering\b': r'\1suffering',
        r'\b([b-df-hj-np-tv-z])uggest\b': r'\1suggest',
        r'\b([b-df-hj-np-tv-z])uggests\b': r'\1suggests',
        r'\b([b-df-hj-np-tv-z])uggested\b': r'\1suggested',
        r'\b([b-df-hj-np-tv-z])uggestion\b': r'\1suggestion',
        r'\b([b-df-hj-np-tv-z])upport\b': r'\1support',
        r'\b([b-df-hj-np-tv-z])upported\b': r'\1supported',
        r'\b([b-df-hj-np-tv-z])upporting\b': r'\1supporting',
        r'\b([b-df-hj-np-tv-z])uppose\b': r'\1suppose',
        r'\b([b-df-hj-np-tv-z])upposed\b': r'\1supposed',
        r'\b([b-df-hj-np-tv-z])upposedly\b': r'\1supposedly',
        r'\b([b-df-hj-np-tv-z])ure\b': r'\1sure',
        r'\b([b-df-hj-np-tv-z])urely\b': r'\1surely',
        r'\b([b-df-hj-np-tv-z])urprise\b': r'\1surprise',
        r'\b([b-df-hj-np-tv-z])urprised\b': r'\1surprised',
        r'\b([b-df-hj-np-tv-z])urprising\b': r'\1surprising',
        r'\b([b-df-hj-np-tv-z])urprisingly\b': r'\1surprisingly',
        r'\b([b-df-hj-np-tv-z])urround\b': r'\1surround',
        r'\b([b-df-hj-np-tv-z])urrounded\b': r'\1surrounded',
        r'\b([b-df-hj-np-tv-z])urrounding\b': r'\1surrounding',
        r'\b([b-df-hj-np-tv-z])urvive\b': r'\1survive',
        r'\b([b-df-hj-np-tv-z])urvived\b': r'\1survived',
        r'\b([b-df-hj-np-tv-z])urviving\b': r'\1surviving',
        r'\b([b-df-hj-np-tv-z])urvival\b': r'\1survival',
        r'\b([b-df-hj-np-tv-z])ystem\b': r'\1system',
        r'\b([b-df-hj-np-tv-z])ystems\b': r'\1systems',
    }
    for pattern, replacement in fixes.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text

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
    """Split text into sentences, handling ASR text that may lack proper capitalization."""
    # First try standard split on period+space+capital
    sents = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    # If that didn't split much, try splitting on period+space+any word
    if len(sents) < 5:
        sents = re.split(r'(?<=[.!?])\s+', text)
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

def format_paragraphs(sents, max_s=4):
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
    text = fix_asr_artifacts(text)
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
