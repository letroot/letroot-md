#!/usr/bin/env python3
"""Build CHT markdown files from clean text with Pleros-quality formatting."""
import re
import os
import glob
import subprocess

BASE_DIR = "/Users/letroot/Documents/notes/obsidian-vaults/letroot-md/show-notes/CHT-1st-Century"

def get_metadata(video_id):
    """Fetch title and upload date from YouTube."""
    try:
        cmd = f'yt-dlp --print "%(title)s|%(upload_date)s" "https://www.youtube.com/watch?v={video_id}" 2>/dev/null'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split("|")
            raw_title = parts[0]
            upload_date = parts[1] if len(parts) > 1 else ""
            
            # Clean title: remove CHT/S2EXX prefixes
            # Note: filenames may use fullwidth Unicode chars ｜ (U+FF5C) and ： (U+FF1A)
            title = re.sub(r'^CHT\s+[\|\｜]\s+', '', raw_title)
            title = re.sub(r'^CHT\s+S\d+E\d+\s*[:\-：]?\s*', '', title)
            title = re.sub(r'^S\d+E\d+[:\-：]?\s*', '', title)
            title = re.sub(r'^Resource[:\-：]?\s*', 'Resource: ', title)
            title = title.strip()
            
            if upload_date and len(upload_date) == 8:
                date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
            else:
                date = "2024-01-01"
            
            return title, date
    except Exception as e:
        print(f"  Error fetching metadata: {e}")
    return None, None

def clean_transcript(text):
    """Remove fillers and ASR artifacts while keeping content verbatim."""
    # Remove standalone filler sounds
    text = re.sub(r'\b(uh+|um+|ah+|eh+|er+|hmm+|mmm+)\b[,\s]*', '', text, flags=re.IGNORECASE)
    
    # Remove "you know" as filler
    text = re.sub(r'\byou know[,\s]+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[,\s]+you know\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\byou know\b', '', text, flags=re.IGNORECASE)
    
    # Remove "I mean" as filler
    text = re.sub(r'\bI mean[,\s]+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[,\s]+I mean\b', '', text, flags=re.IGNORECASE)
    
    # Remove other fillers
    text = re.sub(r'\bsort of\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bkind of\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bI guess\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bI suppose\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bif you will\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bif you like\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bin a way\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bin some ways?\b', '', text, flags=re.IGNORECASE)
    
    # Remove tag questions
    text = re.sub(r',\s*right\?', '?', text, flags=re.IGNORECASE)
    text = re.sub(r',\s*okay\?', '?', text, flags=re.IGNORECASE)
    
    # Fix repeated words
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text)
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text)
    
    # Fix common double words
    for word in ['and', 'the', 'to', 'of', 'in', 'a', 'is', 'it', 'that', 'this', 'we', 'you']:
        text = re.sub(rf'\b{word}\s+{word}\b', word, text, flags=re.IGNORECASE)
    
    # Fix broken words (e.g. "e- xperience")
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)
    
    # Fix bad contractions
    text = re.sub(r"(\w)\s+'\s*(\w)", r"\1'\2", text)
    
    # Fix "gon na" -> "gonna"
    text = re.sub(r'\bgo\s+na\b', 'gonna', text)
    text = re.sub(r'\bwan\s+na\b', 'wanna', text)
    
    # Clean whitespace around punctuation
    text = re.sub(r'\s+([.,;!?])', r'\1', text)
    text = re.sub(r'([.,;!?])\s+', r'\1 ', text)
    
    # Remove double punctuation
    text = re.sub(r',\s*,', ',', text)
    text = re.sub(r'\.\s*\.', '.', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def remove_template(text):
    """Remove standard intro/outro that duplicates the template."""
    # Intro
    text = re.sub(
        r'Welcome to Church History and Theology,\s+a study where we glean wisdom from those who came before us\.\s*Come, lay aside today\'s concerns for a bit and join in a study of the church throughout the ages\.\s*Our forebears have shaped our faith in countless ways\.\s*Let\'s go look into one of those influences today upon Church History and Theology\.',
        '', text, flags=re.DOTALL | re.IGNORECASE
    )
    text = re.sub(r'Well, greetings\.\s*Welcome to Church History and Theology\.\s*My name is Timothy Easley.*?\.', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'My name is Timothy Easley as we jump into yet again another episode.*?\.', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'Today we have a really fun one\.\s*I enjoyed prepping this lesson.*?\.', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Outro
    text = re.sub(r'Thank you for listening to Church History and Theology.*?\.', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'Don\'t forget to subscribe to our podcast.*?\.', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'We hope this episode has enriched your understanding.*?\.', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'follow us on social media for more content.*?\.', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    return text.strip()

def format_paragraphs(text):
    """Split into readable paragraphs with generous spacing."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    paragraphs = []
    current = []
    
    for sent in sentences:
        sent = sent.strip()
        if not sent or len(sent) < 10:
            continue
        current.append(sent)
        if len(current) >= 4:
            paragraphs.append(' '.join(current))
            current = []
    
    if current:
        paragraphs.append(' '.join(current))
    
    return '\n\n'.join(paragraphs)

def detect_heading(para_text):
    """Detect if paragraph starts a new topic."""
    first = para_text[:150].lower()
    
    # Biblical references
    bible_match = re.search(
        r'\b(Acts|Matthew|Mark|Luke|John|Romans|1\s*Corinthians|2\s*Corinthians|Galatians|Ephesians|Philippians|Colossians|1\s*Thessalonians|2\s*Thessalonians|1\s*Timothy|2\s*Timothy|Titus|Philemon|Hebrews|James|1\s*Peter|2\s*Peter|1\s*John|2\s*John|3\s*John|Jude|Revelation|Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|1\s*Samuel|2\s*Samuel|1\s*Kings|2\s*Kings|1\s*Chronicles|2\s*Chronicles|Ezra|Nehemiah|Esther|Job|Psalms|Proverbs|Ecclesiastes|Song\s*of\s*Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi)\s+(chapter\s+)?(\d+)',
        para_text, re.IGNORECASE
    )
    if bible_match:
        return f"{bible_match.group(1).title()} {bible_match.group(3)}"
    
    # Figures
    figures = {
        'ignatius': "Ignatius of Antioch",
        'justin martyr': "Justin Martyr",
        'polycarp': "Polycarp",
        'clement of rome': "Clement of Rome",
        'irenaeus': "Irenaeus",
        'tertullian': "Tertullian",
        'origen': "Origen",
        'cyprian': "Cyprian",
        'athanasius': "Athanasius",
        'augustine': "Augustine",
        'jerome': "Jerome",
        'chrysostom': "Chrysostom",
        'eusebius': "Eusebius",
        'constantine': "Constantine",
        'marcion': "Marcion",
        'montanus': "Montanus",
        'arius': "Arius",
    }
    for key, heading in figures.items():
        if key in first:
            return heading
    
    # Topics (first_100 match)
    topics = {
        'persecution': "Persecution",
        'martyrdom': "Martyrdom",
        'the canon': "The Canon",
        'eucharist': "The Eucharist",
        'baptism': "Baptism",
        'worship': "Worship",
        'prayer': "Prayer",
        'preaching': "Preaching",
        'house church': "House Churches",
        'synagogue': "The Synagogue",
        'temple': "The Temple",
        'gentiles': "The Gentile Mission",
        'great commission': "The Great Commission",
        'spiritual gifts': "Spiritual Gifts",
        'elders': "Elders",
        'deacons': "Deacons",
        'bishops': "Bishops",
        'apostles': "The Apostles",
        'apostolic fathers': "The Apostolic Fathers",
        'monasticism': "Monasticism",
        'liturgy': "Liturgy",
        'sacraments': "Sacraments",
        'doctrine': "Doctrine",
        'theology': "Theology",
        'heresy': "Heresy",
        'gnosticism': "Gnosticism",
        'trinity': "The Trinity",
        'christology': "Christology",
        'incarnation': "The Incarnation",
        'resurrection': "The Resurrection",
        'pentecost': "Pentecost",
        'holy spirit': "The Holy Spirit",
        'salvation': "Salvation",
        'justification': "Justification",
        'sanctification': "Sanctification",
        'gospel': "The Gospel",
        'kingdom of god': "The Kingdom of God",
        'the church': "The Church",
        'leadership': "Leadership",
        'reformation': "The Reformation",
        'crusades': "The Crusades",
        'luther': "Martin Luther",
        'calvin': "John Calvin",
        'vatican': "The Vatican",
        'pope': "The Pope",
        'orthodox church': "The Orthodox Church",
        'anglican': "The Anglican Church",
        'methodist': "The Methodist Church",
        'baptist': "The Baptist Church",
        'presbyterian': "The Presbyterian Church",
        'lutheran': "The Lutheran Church",
        'pentecostal': "The Pentecostal Church",
        'evangelical': "The Evangelical Church",
    }
    for key, heading in topics.items():
        if key in first:
            return heading
    
    return None

def add_headings(text, default_title):
    """Add content-based headings."""
    paragraphs = text.split('\n\n')
    sections = []
    current_heading = default_title
    current_content = []
    
    for para in paragraphs:
        if not para.strip():
            continue
        
        new_heading = detect_heading(para)
        
        if new_heading and new_heading != current_heading and len(current_content) > 0:
            sections.append((current_heading, current_content))
            current_heading = new_heading
            current_content = [para]
        else:
            current_content.append(para)
    
    if current_content:
        sections.append((current_heading, current_content))
    
    lines = []
    for heading, paras in sections:
        lines.append(f"## {heading}")
        lines.append('')
        lines.extend(paras)
        lines.append('')
    
    return '\n'.join(lines)

def build_markdown(episode_code, title, date, video_id, body):
    """Build final markdown."""
    safe = re.sub(r'[^\w\s-]', '', title).strip().lower()
    safe = re.sub(r'\s+', '-', safe)
    filename = f"{episode_code.lower()}-{safe}.md"
    
    md = f"""---
title: "{title}"
date: {date}
tags: [podcast, church-history, cht]
url: "https://www.youtube.com/watch?v={video_id}"
type: solo
series: "1st Century"
episode: "{episode_code}"
---

# {title}

## Introduction to Church History and Theology

Welcome to Church History and Theology. This is the podcast where we explore the rich history of the Christian church and dive deep into theological topics that shape our faith today. Join us as we journey through centuries of church history, examining key figures, movements, and doctrines that have defined Christianity.

## {title}

{body}

## Closing

Thank you for listening to Church History and Theology. We hope this episode has enriched your understanding of the church's history and deepened your appreciation for the theological foundations of our faith.

Don't forget to subscribe to our podcast and follow us on social media for more content on church history and theology.
"""
    return filename, md

def main():
    txt_files = sorted(glob.glob(os.path.join(BASE_DIR, "*_clean.txt")))
    print(f"Processing {len(txt_files)} episodes...")
    
    for txt_path in txt_files:
        basename = os.path.basename(txt_path)
        
        # Extract video ID
        match = re.search(r'\[([a-zA-Z0-9_-]+)\]', basename)
        if not match:
            continue
        video_id = match.group(1)
        
        # Extract episode code
        ep_match = re.search(r'(S\d+E\d+)', basename)
        episode_code = ep_match.group(1) if ep_match else ""
        if not episode_code:
            continue
        
        print(f"\nProcessing {episode_code} ({video_id})...")
        
        # Get metadata
        title, date = get_metadata(video_id)
        if not title:
            # Fallback: extract from filename
            # Note: filenames may use fullwidth Unicode chars ｜ (U+FF5C) and ： (U+FF1A)
            raw = basename.replace('_clean.txt', '').replace('[', '').replace(']', '')
            title = re.sub(r'^CHT\s+[\|\｜]\s+', '', raw)
            title = re.sub(r'^CHT\s+S\d+E\d+\s*[:\-：]?\s*', '', title)
            title = re.sub(r'^S\d+E\d+[:\-：]?\s*', '', title)
            title = re.sub(r'^Resource[:\-：]?\s*', 'Resource: ', title)
            title = title.strip()
            date = "2024-01-01"
            print(f"  Using fallback title: {title}")
        else:
            print(f"  Title: {title}")
            print(f"  Date: {date}")
        
        # Read and process
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        text = clean_transcript(text)
        text = remove_template(text)
        body = format_paragraphs(text)
        body = add_headings(body, title)
        
        filename, md = build_markdown(episode_code, title, date, video_id, body)
        
        filepath = os.path.join(BASE_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"  -> {filename}")

if __name__ == '__main__':
    main()
