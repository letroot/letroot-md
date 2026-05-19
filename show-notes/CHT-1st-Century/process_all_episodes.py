#!/usr/bin/env python3
import re
import os
import glob
import subprocess

BASE_DIR = "/Users/letroot/Documents/notes/obsidian-vaults/letroot-md/show-notes/CHT-1st-Century"

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def clean_transcript(text):
    text = re.sub(r'>>\s*\[.*?\]\s*>>', '', text)
    text = text.replace('[music]', '')
    text = text.replace('&quot;', '"')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_standard_segments(text):
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

def get_video_metadata(video_id):
    cmd = f'yt-dlp --print "%(title)s|%(upload_date)s" "https://www.youtube.com/watch?v={video_id}"'
    stdout, stderr, rc = run_cmd(cmd)
    if rc != 0 or not stdout:
        return None, None
    parts = stdout.split('|')
    title = parts[0]
    upload_date = parts[1] if len(parts) > 1 else ""
    if upload_date and len(upload_date) == 8:
        date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
    else:
        date = "2024-01-01"
    return title, date

def create_markdown(video_id, title, date, body_text, episode_code=""):
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()
    safe_title = re.sub(r'\s+', '-', safe_title).lower()
    
    if episode_code.startswith('S'):
        filename = f"{episode_code.lower()}-{safe_title}.md"
    else:
        filename = f"{safe_title}.md"
    
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

{body_text}

## Closing

Thank you for listening to Church History and Theology. We hope this episode has enriched your understanding of the church's history and deepened your appreciation for the theological foundations of our faith.

Don't forget to subscribe to our podcast and follow us on social media for more content on church history and theology.
"""
    
    return filename, md

def main():
    # Process all clean text files
    txt_files = glob.glob(os.path.join(BASE_DIR, "*_clean.txt"))
    
    for txt_path in txt_files:
        basename = os.path.basename(txt_path)
        
        # Extract video ID
        match = re.search(r'\[([a-zA-Z0-9_-]+)\]', basename)
        if not match:
            continue
        
        video_id = match.group(1)
        
        # Check if markdown already exists
        existing = glob.glob(os.path.join(BASE_DIR, f"*{video_id}*.md"))
        if existing:
            continue
        
        # Get metadata
        print(f"Getting metadata for {video_id}...")
        raw_title, date = get_video_metadata(video_id)
        
        if not raw_title:
            print(f"  Warning: Could not get metadata for {video_id}")
            continue
        
        # Clean title
        title = re.sub(r'^CHT\s+\|\s+', '', raw_title)
        title = re.sub(r'^S\d+E\d+:\s*', '', title)
        title = re.sub(r'^Resource:\s*', 'Resource: ', title)
        title = re.sub(r'^CHT\s+S\d+E\d+\s+', '', title)
        title = title.strip()
        
        # Extract episode code
        ep_match = re.search(r'(S\d+E\d+)', raw_title)
        episode_code = ep_match.group(1) if ep_match else ""
        
        # Read and process text
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        text = clean_transcript(text)
        text = remove_standard_segments(text)
        body = format_paragraphs(text)
        
        filename, md = create_markdown(video_id, title, date, body, episode_code)
        
        filepath = os.path.join(BASE_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"  Created: {filename}")

if __name__ == '__main__':
    main()
