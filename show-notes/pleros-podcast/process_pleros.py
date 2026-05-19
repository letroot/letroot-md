import re

# Episode data: (episode_num, title, video_id, date)
episodes = [
    (132, "Preservation in the Newness of Life (Part 4)", "fujZakdSLPM", "2026-05-14"),
    (133, "Preservation in the Newness of Life (Part 5)", "g8OMJ2hOrd0", "2026-05-15"),
    (134, "Preservation in the Newness of Life (Part 6)", "_mw-DjbPOlg", "2026-05-16"),
    (135, "Preservation in the Newness of Life (Part 7)", "iSvIbIyeunI", "2026-05-18"),
    (136, "Preservation in the Newness of Life (Part 8)", "uf_jgpwSSU8", "2026-05-19"),
]

def clean_transcript(text):
    """Clean transcript artifacts while keeping text verbatim."""
    # Remove transcript noise
    text = re.sub(r'>>\s*\[.*?\]\s*>>', '', text)
    text = text.replace('[music]', '')
    text = re.sub(r'&gt;&gt;\s*\[.*?\]\s*&gt;&gt;', '', text)
    text = re.sub(r'&gt;&gt;', '', text)
    # Fix common ASR errors
    text = text.replace('Plural\'s', 'Pleros')
    text = text.replace('Pastor Aking', 'Pastor Akim')
    text = text.replace('Pleroma', 'Pleros')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_standard_segments(text):
    """Remove the standard intro/outro that duplicates the template."""
    # Remove standard intro variations
    patterns = [
        r'Welcome to Pleros? podcast\. You are about to be blessed.*?taught (today|to be)\.?\s*',
        r'Welcome to Pleros? podcast\. You are about to be blessed.*?God\'s word.*?\.?\s*',
        r"Let's get right into it\.\s*All right, welcome back to the Pleros? podcast\.\s*",
        r"Let's get right into it\.\s*Welcome back to the Pleros? podcast\.\s*",
        r'This is your daily dose of God\'s word transforming you to fulfill God\'s purpose for your life\.\s*',
        r'welcome back to the Pleros? podcast.*?daily dose of God\'s word.*?\.?\s*',
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove outro variations
    outro_patterns = [
        r'We trust you (were|are) blessed by.*?keep walking in his purpose\.?',
        r'visit pleros\.org.*?social media handles.*?\.?\s*',
        r'For now, stay blessed and keep walking in his purpose\.?\s*',
        r'To learn more of God\'s word.*?\.?\s*',
        r'don\'t forget to join the Pleros? community channel.*?\.?\s*',
        r'You will find answers to your questions on the gospel.*?\.?\s*',
    ]
    
    for pattern in outro_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Clean up
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

def format_episode(text, title, episode_num, video_id, date):
    text = clean_transcript(text)
    text = remove_standard_segments(text)
    body = format_paragraphs(text)
    
    kebab = title.lower().replace(' ', '-').replace('(', '').replace(')', '')
    filename = f"episode-{episode_num:03d}-{kebab}.md"
    
    md = f"""---
title: "{title}"
date: {date}
tags: [podcast, pleros]
url: "https://www.youtube.com/watch?v={video_id}"
type: solo
---

# {title}

## Introduction to the Pleros Podcast

Welcome to Pleros podcast. You are about to be blessed by the teaching ministry of Pastor Akim. It is going to be an enlightening time in God's word, renewing your mind and transforming your life to fulfill God's purpose. We pray for you that you are established in all the truths of God's word taught today.

Let's get right into it. Welcome back to the Pleros podcast. This is your daily dose of God's word transforming you to fulfill God's purpose for your life.

## {title.split('(')[0].strip()}

{body}

## Closing Charge

All right that'll be it for now. Thank you. Fulfill God's purpose and see you on the next one.

We trust you were blessed by today's episode. Do stay in faith about all you've heard to walk in it. To learn more of God's word, visit pleros.org. You will find answers to your questions on the gospel, God, his purpose, and how to fulfill it. Whilst on our website, don't forget to join the Pleros community channel on WhatsApp and follow us on all our social media handles at Pleros_HQ. For now, stay blessed and keep walking in his purpose.
"""
    
    return filename, md

for ep_num, title, vid, date in episodes:
    with open(f"ep{ep_num}_clean.txt", 'r', encoding='utf-8') as f:
        text = f.read()
    
    filename, md = format_episode(text, title, ep_num, vid, date)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"Wrote {filename}")
