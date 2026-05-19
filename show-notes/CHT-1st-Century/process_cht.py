import re
import os
import glob

# Episode metadata from yt-dlp --print
# Each tuple: (video_id, title, date, episode_code)
episodes = [
    ("avchLhrCpd4", "Going to Church in 100 AD", "2025-05-01", "S2E21"),
    ("1fz8cCeKCPk", "The Inevitable New Testament", "2025-04-02", "S2E20"),
    ("iHVuKha3QyI", "The OT Canon in the 1st Century", "2025-03-01", "S2E19"),
    ("Tmm4TKjlaJk", "John the Last Apostle", "2025-02-14", "S2E18"),
    ("PFDFzUGiIKI", "Thecla, the Saint Who Never Existed", "2025-01-28", "S2E17"),
    ("ShbQcxk_dXQ", "James, the Lord's Brother", "2025-01-08", "S2E16"),
    ("ZULRk6VpNJY", "Rome of the First Century", "2024-11-28", "S2E15"),
    ("Mu2CnqKXBy0", "NT Canon and the Church", "2024-11-13", "S2E14"),
    ("Z4wwZaEFnXY", "Antioch - the Rome of the East", "2024-10-17", "S2E13"),
    ("7tEhFkRX2qY", "Resource: The Didache", "2024-12-12", "Resource"),
]

def clean_transcript(text):
    """Clean transcript artifacts while keeping text verbatim."""
    # Remove transcript noise
    text = re.sub(r'>>\s*\[.*?\]\s*>>', '', text)
    text = text.replace('[music]', '')
    
    # Fix common ASR errors and HTML entities
    text = text.replace('&quot;', '"')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    
    # Fix repeated words (common in ASR)
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_standard_segments(text):
    """Remove standard intro/outro that duplicates the template."""
    # Common CHT intro/outro patterns
    patterns = [
        r'welcome to church history and theology.*?this is the podcast.*?\.\s*',
        r'welcome to church history and theology.*?i\'m your host.*?\.\s*',
        r'let\'s get started.*?\.\s*',
        r'thanks for listening to church history and theology.*?\.\s*',
        r'thanks for joining us on church history and theology.*?\.\s*',
        r'don\'t forget to subscribe.*?\.\s*',
        r'find us on.*?social media.*?\.\s*',
        r'visit our website.*?\.\s*',
        r'join us next time.*?\.\s*',
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def format_paragraphs(text):
    """Split text into readable paragraphs (3-6 sentences)."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    paragraphs = []
    current_para = []
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        current_para.append(sent)
        if len(current_para) >= 5:
            paragraphs.append(' '.join(current_para))
            current_para = []
    if current_para:
        paragraphs.append(' '.join(current_para))
    
    return '\n\n'.join(paragraphs)

def create_markdown(episode, body_text):
    """Create markdown file for an episode."""
    video_id, title, date, ep_code = episode
    
    # Determine series
    series = "1st Century"
    
    # Create filename
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()
    safe_title = re.sub(r'\s+', '-', safe_title).lower()
    
    if ep_code.startswith('S'):
        filename = f"{ep_code.lower()}-{safe_title}.md"
    else:
        filename = f"{safe_title}.md"
    
    # Build markdown
    md = f"""---
title: "{title}"
date: {date}
tags: [podcast, church-history, cht]
url: "https://www.youtube.com/watch?v={video_id}"
type: solo
series: "{series}"
episode: "{ep_code}"
---

# {title}

## Introduction to Church History and Theology

Welcome to Church History and Theology. This is the podcast where we explore the rich history of the Christian church and dive deep into theological topics that shape our faith today. Join us as we journey through centuries of church history, examining key figures, movements, and doctrines that have defined Christianity.

## {title}

{body_text}

## Closing

Thank you for listening to Church History and Theology. We hope this episode has enriched your understanding of the church's history and deepened your appreciation for the theological foundations of our faith.

Don't forget to subscribe to our podcast and follow us on social media for more content on church history and theology.
"""
    
    return filename, md

def main():
    for episode in episodes:
        video_id, title, date, ep_code = episode
        
        # Find the clean text file
        txt_pattern = f"*{video_id}*_clean.txt"
        txt_files = glob.glob(txt_pattern)
        
        if not txt_files:
            print(f"Warning: No clean text file found for {title} ({video_id})")
            continue
        
        txt_path = txt_files[0]
        print(f"Processing: {title} ({txt_path})")
        
        # Read clean text
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Process
        text = clean_transcript(text)
        text = remove_standard_segments(text)
        body = format_paragraphs(text)
        
        filename, md = create_markdown(episode, body)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"  Wrote: {filename}")

if __name__ == '__main__':
    main()
