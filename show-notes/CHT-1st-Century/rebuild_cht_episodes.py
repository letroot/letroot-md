#!/usr/bin/env python3
"""
Rebuild CHT 1st Century podcast transcripts to match Pleros quality standards.
Processes all 22 _clean.txt files into properly formatted markdown.
"""

import os
import re
import json
import subprocess
import glob

WORK_DIR = "/Users/letroot/Documents/notes/obsidian-vaults/letroot-md/show-notes/CHT-1st-Century"

# Standard intro/outro patterns to remove
STANDARD_INTRO_PATTERNS = [
    r"welcome to church history and theology,?\s*a study where we glean wisdom from those who came before us\.?\s*come,?\s*lay aside today'?s concerns for a bit and join in a study of the church throughout the ages\.?\s*our forebears have shaped our faith in countless ways\.?\s*let'?s go look into one of those influences today\s*(?:upon|on)\s*church history and\s*(?:\[Music\]\s*)?theology",
    r"welcome to church history and theology,?\s*a study where we glean wisdom from those who came before us\.?\s*come,?\s*lay aside today'?s concerns for a bit and join in a study of the church throughout the ages\.?\s*our forebears have shaped our faith in countless ways\.?\s*let'?s go look into one of those influences today\s*(?:upon|on)\s*church\s*(?:history and\s*)?theology",
]

STANDARD_OUTRO_PATTERNS = [
    r"thank you for listening to church history and theology\.?\s*we hope this episode has enriched your understanding of the church'?s history and deepened your appreciation for the theological foundations of our faith\.?\s*don'?t forget to subscribe to our podcast and follow us on social media for more content on church history and theology\.?",
    r"thank you for listening to church history and theology\.?\s*we hope this episode has enriched your understanding.*",
]

FILLER_WORDS = [
    r'\buh\b', r'\bum\b', r'\bah\b', r'\beh\b', r'\ber\b',
    r'\bhmm\b', r'\bhuh\b',
    r'\byou know\b', r'\bi mean\b', r'\bsort of\b', r'\bkind of\b',
    r'\bi guess\b', r'\bi suppose\b', r'\bif you will\b', r'\bif you like\b',
    r'\bin a way\b',
    r',?\s*right\?', r',?\s*okay\?',
]

# Bible book patterns for section detection
BIBLE_REFS = [
    r'(?:acts|genesis|exodus|leviticus|numbers|deuteronomy|joshua|judges|ruth|1\s*samuel|2\s*samuel|1\s*kings|2\s*kings|1\s*chronicles|2\s*chronicles|ezra|nehemiah|esther|job|psalms|psalm|proverbs|ecclesiastes|song\s*of\s*solomon|isaiah|jeremiah|lamentations|ezekiel|daniel|hosea|joel|amos|obadiah|jonah|micah|nahum|habakkuk|zephaniah|haggai|zechariah|malachi|matthew|mark|luke|john|romans|1\s*corinthians|2\s*corinthians|galatians|ephesians|philippians|colossians|1\s*thessalonians|2\s*thessalonians|1\s*timothy|2\s*timothy|titus|philemon|hebrews|james|1\s*peter|2\s*peter|1\s*john|2\s*john|3\s*john|jude|revelation)\s+(?:chapter\s+)?(?:\d{1,3}(?:\s*[-:]\s*\d{1,3})?(?:\s*(?:and|through|to)\s+\d{1,3})?)',
]

# Topic transition phrases
TRANSITION_PHRASES = [
    r"(?:now\s+)?let[\s']*(?:us|'s)?\s+(?:look\s+at|turn\s+to|go\s+to|consider|delve\s+into|examine|read\s+from|jump\s+to|open\s+up)",
    r'(?:now\s+)?this\s+brings\s+us\s+to',
    r'(?:now\s+)?we\s+(?:come\s+to|arrive\s+at|turn\s+to|move\s+on\s+to|look\s+at)',
    r'(?:now\s+)?another\s+(?:thing\s+)?(?:that\s+)?(?:we\s+)?(?:see|find|have|consider)',
    r"(?:now\s+)?let[\s']*(?:us|'s)?\s+(?:talk\s+about|discuss|think\s+about)",
    r"(?:now\s+)?i\s+want\s+to\s+(?:talk\s+about|look\s+at|share|show\s+you|read)",
    r'(?:now\s+)?we\s+see\s+(?:that\s+)?(?:in\s+)?(?:the\s+)?(?:book\s+of\s+)?(?:acts|genesis|exodus|leviticus|numbers|deuteronomy|joshua|judges|ruth|samuel|kings|chronicles|ezra|nehemiah|esther|job|psalms|psalm|proverbs|ecclesiastes|isaiah|jeremiah|ezekiel|daniel|hosea|joel|amos|obadiah|jonah|micah|nahum|habakkuk|zephaniah|haggai|zechariah|malachi|matthew|mark|luke|john|romans|corinthians|galatians|ephesians|philippians|colossians|thessalonians|timothy|titus|philemon|hebrews|james|peter|john|jude|revelation)',
    r'(?:now\s+)?(?:this|that)\s+(?:is|brings)\s+(?:where|us)',
    r'(?:now\s+)?the\s+(?:first|second|third|next|final)\s+(?:thing|point|aspect|element)',
]

# Key topics/names that might warrant headings
KEY_TOPICS = [
    'ignatius', 'justin martyr', 'the didache', 'first clement', 'polycarp',
    'pentecost', 'eucharist', 'baptism', 'persecution', 'martyr',
    'peter', 'paul', 'john', 'james', 'stephen', 'philip', 'thecla',
    'apostolic', 'apostles', 'bishop', 'elder', 'deacon',
    'liturgy', 'worship', 'prayer', 'synagogue', 'canon',
    'romans?', 'ephesus', 'antioch', 'jerusalem', 'corinth', 'philippi',
    'new testament', 'old testament', 'gospel', 'epistle',
    'saint', 'saints', 'gentile', 'gentiles', 'jewish',
]


def extract_video_info(filename):
    """Extract video ID and episode code from filename."""
    # Extract video ID from [...]
    video_id_match = re.search(r'\[([^\]]+)\]', filename)
    video_id = video_id_match.group(1) if video_id_match else None

    # Extract episode code (S2E1, S2E21, etc.)
    episode_match = re.search(r'[Ss]2[Ee](\d+)', filename)
    episode_num = episode_match.group(1) if episode_match else None
    episode_code = f"S2E{episode_num}" if episode_num else None

    return video_id, episode_code


def fetch_youtube_metadata(video_id):
    """Fetch title and upload date from YouTube using yt-dlp."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        result = subprocess.run(
            ['yt-dlp', '--print', '%(title)s|%(upload_date)s', url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split('|', 1)
            title = parts[0].strip()
            upload_date = parts[1].strip() if len(parts) > 1 else None
            # Format date as YYYY-MM-DD
            if upload_date and len(upload_date) == 8:
                upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
            return title, upload_date
    except Exception as e:
        print(f"  Error fetching metadata: {e}")
    return None, None


def clean_transcript(text):
    """Clean the transcript text."""
    # Remove [Music] tags
    text = re.sub(r'\[Music\]', '', text, flags=re.IGNORECASE)

    # Remove standard intro
    for pattern in STANDARD_INTRO_PATTERNS:
        text = re.sub(pattern, '', text, count=1, flags=re.IGNORECASE)

    # Remove standard outro
    for pattern in STANDARD_OUTRO_PATTERNS:
        text = re.sub(pattern, '', text, count=1, flags=re.IGNORECASE)

    # Remove filler words
    for pattern in FILLER_WORDS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Fix ASR artifacts
    # Repeated words: "the the" -> "the"
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)

    # Broken words: "e- xperience" -> "experience"
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)

    # Bad contractions: "don ' t" -> "don't"
    text = re.sub(r"(\w+)\s+'\s*(\w+)", r"\1'\2", text)
    text = re.sub(r"(\w+)\s+'(\w+)", r"\1'\2", text)

    # Fix extra spaces
    text = re.sub(r'\s{2,}', ' ', text)

    # Clean up leading/trailing whitespace
    text = text.strip()

    return text


def split_into_sentences(text):
    """Split text into sentences for paragraph building."""
    # Split on period, question mark, exclamation followed by space and capital letter
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [s.strip() for s in sentences if s.strip()]


def detect_section_breaks(sentences):
    """Detect natural section breaks based on content cues."""
    breaks = []
    for i, sentence in enumerate(sentences):
        lower = sentence.lower()

        # Check for Bible references at start of sentence
        for ref_pattern in BIBLE_REFS:
            if re.match(ref_pattern, lower):
                # Extract the reference for the heading
                match = re.match(ref_pattern, lower)
                if match:
                    ref_text = match.group(0)
                    # Capitalize properly
                    heading = ref_text.title()
                    breaks.append((i, f"## {heading}"))
                break

        # Check for transition phrases
        for trans_pattern in TRANSITION_PHRASES:
            if re.match(trans_pattern, lower):
                # Extract a meaningful heading from context
                # Look for the topic after the transition
                topic_match = re.search(r'(?:look\s+at|turn\s+to|go\s+to|consider|delve\s+into|examine|discuss|talk\s+about|read\s+(?:from\s+)?)\s+([^.]{5,60})', lower)
                if topic_match:
                    topic = topic_match.group(1).strip()
                    # Clean up the topic
                    topic = re.sub(r'\b(and|the|in|of|to|for|with|by|from|on|at|is|are|was|were)\b', '', topic, flags=re.IGNORECASE)
                    topic = re.sub(r'\s+', ' ', topic).strip()
                    if len(topic) > 3:
                        heading = topic.title()
                        breaks.append((i, f"## {heading}"))
                break

        # Check for key topics at start of sentence
        for topic in KEY_TOPICS:
            pattern = rf'\b{topic}\b'
            if re.match(pattern, lower):
                heading = topic.title()
                # Avoid too many breaks for common words
                if topic not in ['romans?', 'saint', 'saints', 'gentile', 'gentiles', 'jewish', 'new testament', 'old testament']:
                    breaks.append((i, f"## {heading}"))
                break

    return breaks


def build_sections(sentences, breaks):
    """Build sections with headings from sentences and detected breaks."""
    if not breaks:
        return [(None, sentences)]

    sections = []
    current_section = []
    break_idx = 0

    for i, sentence in enumerate(sentences):
        if break_idx < len(breaks) and i == breaks[break_idx][0]:
            if current_section:
                sections.append((breaks[break_idx][1], current_section))
            current_section = []
            break_idx += 1
        current_section.append(sentence)

    if current_section:
        if sections:
            sections.append((None, current_section))
        else:
            sections.append((None, current_section))

    return sections


def format_paragraphs(sentences, max_sentences=5):
    """Group sentences into paragraphs with generous spacing."""
    paragraphs = []
    current = []

    for sentence in sentences:
        current.append(sentence)
        if len(current) >= max_sentences:
            paragraphs.append(' '.join(current))
            current = []

    if current:
        paragraphs.append(' '.join(current))

    return paragraphs


def generate_filename(episode_code, title):
    """Generate kebab-case filename from episode code and title."""
    # Extract episode number
    ep_match = re.search(r'[Ss]2[Ee](\d+)', episode_code)
    ep_num = ep_match.group(1) if ep_match else '00'

    # Clean title for filename
    clean_title = title.lower()
    clean_title = re.sub(r'[^\w\s-]', '', clean_title)
    clean_title = re.sub(r'\s+', '-', clean_title)
    clean_title = re.sub(r'-+', '-', clean_title)
    clean_title = clean_title.strip('-')

    # Truncate if too long
    if len(clean_title) > 50:
        clean_title = clean_title[:50].rsplit('-', 1)[0]

    return f"s2e{ep_num}-{clean_title}.md"


def process_episode(filepath):
    """Process a single _clean.txt file into markdown."""
    filename = os.path.basename(filepath)
    video_id, episode_code = extract_video_info(filename)

    if not video_id or not episode_code:
        print(f"  Skipping {filename}: could not extract video ID or episode code")
        return None

    print(f"  Processing {episode_code} (video: {video_id})")

    # Fetch metadata
    title, upload_date = fetch_youtube_metadata(video_id)
    if not title:
        title = filename.replace('_clean.txt', '').strip()
    if not upload_date:
        upload_date = "2024-01-01"

    # Clean title for frontmatter (remove CHT prefix, clean up)
    clean_title = re.sub(r'^CHT\s*[\|：:]\s*', '', title).strip()
    clean_title = re.sub(r'\s*\[.*?\]\s*$', '', clean_title).strip()

    # Read and clean transcript
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    cleaned = clean_transcript(raw_text)

    # Split into sentences
    sentences = split_into_sentences(cleaned)

    # Detect section breaks
    breaks = detect_section_breaks(sentences)

    # Build sections
    sections = build_sections(sentences, breaks)

    # Build markdown content
    md_lines = []
    md_lines.append('---')
    md_lines.append(f'title: "{clean_title}"')
    md_lines.append(f'date: {upload_date}')
    md_lines.append('tags: [podcast, church-history, cht]')
    md_lines.append(f'url: "https://www.youtube.com/watch?v={video_id}"')
    md_lines.append('type: solo')
    md_lines.append('series: "1st Century"')
    md_lines.append(f'episode: "{episode_code}"')
    md_lines.append('---')
    md_lines.append('')
    md_lines.append(f'# {clean_title}')
    md_lines.append('')

    # Introduction section
    md_lines.append('## Introduction')
    md_lines.append('')

    for heading, section_sentences in sections:
        if heading:
            md_lines.append('')
            md_lines.append(heading)
            md_lines.append('')
        paragraphs = format_paragraphs(section_sentences)
        for para in paragraphs:
            md_lines.append(para)
            md_lines.append('')

    # Closing section
    md_lines.append('## Closing')
    md_lines.append('')

    return '\n'.join(md_lines), generate_filename(episode_code, clean_title)


def main():
    """Process all _clean.txt files."""
    clean_files = sorted(glob.glob(os.path.join(WORK_DIR, "*_clean.txt")))
    print(f"Found {len(clean_files)} _clean.txt files")

    results = []
    for filepath in clean_files:
        result = process_episode(filepath)
        if result:
            md_content, md_filename = result
            output_path = os.path.join(WORK_DIR, md_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            results.append((md_filename, output_path))
            print(f"  -> Created {md_filename}")

    print(f"\nSuccessfully created {len(results)} markdown files")
    return results


if __name__ == '__main__':
    main()
