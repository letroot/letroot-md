#!/usr/bin/env python3
import re
import os

BASE_DIR = "/Users/letroot/Documents/notes/obsidian-vaults/letroot-md/show-notes/CHT-1st-Century"

# Episode metadata: (video_id, title, date, episode_code)
episodes = [
    ("tQj1zllDneU", "What is Church History", "2024-05-02", "S2E1"),
    ("-yTXSOh0z0c", "Why Study Church History", "2024-05-09", "S2E2"),
    ("kvq79XT-N2E", "Christ the Head of Church History", "2024-05-16", "S2E3"),
    ("hJtGL1pth3w", "The NT Church is Born", "2024-05-23", "S2E4"),
    ("Y0Sn6OVpZ5E", "The First Deacons - Stephen and Philip", "2024-05-30", "S2E5"),
    ("wy94M2JLxnM", "Leadership in the Apostolic Church", "2024-06-06", "S2E6"),
    ("u5hzMaK1tiY", "The Real Peter - the Apostle to the Jews", "2024-06-13", "S2E7"),
    ("uHGnPXIqhqY", "Paul - the Apostle to the Gentiles", "2024-06-20", "S2E8"),
    ("RoObwQtL-Pc", "Wolves Will Arise", "2024-06-27", "S2E9"),
    ("V-DIes28IMw", "The Church in Ephesus and Its Mystical Culture", "2024-07-11", "S2E10"),
    ("1kDRa-5d4YU", "The Jerusalem Council", "2024-07-18", "S2E11"),
    ("y65_w9typmk", "All Christians are Saints", "2024-07-25", "S2E12"),
]

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

def create_markdown(video_id, title, date, body_text, episode_code):
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()
    safe_title = re.sub(r'\s+', '-', safe_title).lower()
    filename = f"{episode_code.lower()}-{safe_title}.md"
    
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

for video_id, title, date, ep_code in episodes:
    # Find clean text file
    import glob
    txt_pattern = f"*{video_id}*_clean.txt"
    txt_files = glob.glob(os.path.join(BASE_DIR, txt_pattern))
    
    if not txt_files:
        print(f"Warning: No text file for {ep_code} ({video_id})")
        continue
    
    txt_path = txt_files[0]
    
    # Check if already exists
    expected_file = f"{ep_code.lower()}-*.md"
    existing = glob.glob(os.path.join(BASE_DIR, expected_file))
    if existing:
        print(f"Skipping {ep_code} - already exists")
        continue
    
    # Read and process
    with open(txt_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    text = clean_transcript(text)
    text = remove_standard_segments(text)
    body = format_paragraphs(text)
    
    filename, md = create_markdown(video_id, title, date, body, ep_code)
    
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"Created: {filename}")
