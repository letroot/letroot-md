#!/usr/bin/env python3
"""Rebuild CHT transcripts with Pleros-quality formatting."""
import re
import os
import glob

BASE_DIR = "/Users/letroot/Documents/notes/obsidian-vaults/letroot-md/show-notes/CHT-1st-Century"


def clean_fillers(text):
    """Remove common speech fillers while preserving meaning."""
    # Standalone filler sounds
    text = re.sub(r'\b(uh+|um+|ah+|eh+|er+|hmm+|mmm+)\b[,\s]*', '', text, flags=re.IGNORECASE)

    # "you know" as filler
    text = re.sub(r'\byou know[,\s]+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[,\s]+you know\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\byou know\b', '', text, flags=re.IGNORECASE)

    # "I mean" as filler
    text = re.sub(r'\bI mean[,\s]+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[,\s]+I mean\b', '', text, flags=re.IGNORECASE)

    # "sort of" / "kind of"
    text = re.sub(r'\bsort of\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bkind of\b', '', text, flags=re.IGNORECASE)

    # Weak hedges
    text = re.sub(r'\bI guess\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bI suppose\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bif you will\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bif you like\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bin a way\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bin some ways?\b', '', text, flags=re.IGNORECASE)

    # Tag questions
    text = re.sub(r',\s*right\?', '?', text, flags=re.IGNORECASE)
    text = re.sub(r',\s*okay\?', '?', text, flags=re.IGNORECASE)

    # Repeated words
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text)
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text)

    # Common double words
    for word in ['and', 'the', 'to', 'of', 'in', 'a', 'is', 'it', 'that', 'this', 'we', 'you', 'he', 'she', 'they', 'them']:
        text = re.sub(rf'\b{word}\s+{word}\b', word, text, flags=re.IGNORECASE)

    # Broken words
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)

    # Contractions
    text = re.sub(r"(\w)\s+'\s*(\w)", r"\1'\2", text)

    # "gon na" -> "gonna"
    text = re.sub(r'\bgo\s+na\b', 'gonna', text)
    text = re.sub(r'\bwan\s+na\b', 'wanna', text)

    # Clean whitespace around punctuation
    text = re.sub(r'\s+([.,;!?])', r'\1', text)
    text = re.sub(r'([.,;!?])\s+', r'\1 ', text)

    # Double punctuation
    text = re.sub(r',\s*,', ',', text)
    text = re.sub(r'\.\s*\.', '.', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def remove_template(text):
    """Remove standard intro/outro template text."""
    intros = [
        r'Welcome to Church History and Theology,\s+a study where we glean wisdom from those who came before us\.\s*Come, lay aside today\'s concerns for a bit and join in a study of the church throughout the ages\.\s*Our forebears have shaped our faith in countless ways\.\s*Let\'s go look into one of those influences today upon Church History and Theology\.',
        r'Well, greetings\.\s*Welcome to Church History and Theology\.\s*My name is Timothy Easley.*?\b',
        r'My name is Timothy Easley as we jump into yet again another episode.*?\b',
        r'Today we have a really fun one\.\s*I enjoyed prepping this lesson.*?\b',
    ]
    for pattern in intros:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)

    outros = [
        r'Thank you for listening to Church History and Theology.*?\.\s*',
        r'Don\'t forget to subscribe to our podcast.*?\.\s*',
        r'We hope this episode has enriched your understanding.*?\.\s*',
        r'follow us on social media for more content.*?\.\s*',
    ]
    for pattern in outros:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)

    return text.strip()


def format_body(text):
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


def detect_heading(para_text, title):
    """Detect if paragraph starts a new topic section."""
    first_100 = para_text[:150].lower()

    # Biblical references
    bible_books = [
        'acts', 'matthew', 'mark', 'luke', 'john', 'romans', '1 corinthians', '2 corinthians',
        'galatians', 'ephesians', 'philippians', 'colossians', '1 thessalonians', '2 thessalonians',
        '1 timothy', '2 timothy', 'titus', 'philemon', 'hebrews', 'james', '1 peter', '2 peter',
        '1 john', '2 john', '3 john', 'jude', 'revelation', 'genesis', 'exodus', 'leviticus',
        'numbers', 'deuteronomy', 'joshua', 'judges', 'ruth', '1 samuel', '2 samuel', '1 kings',
        '2 kings', '1 chronicles', '2 chronicles', 'ezra', 'nehemiah', 'esther', 'job', 'psalms',
        'proverbs', 'ecclesiastes', 'song of solomon', 'isaiah', 'jeremiah', 'lamentations',
        'ezekiel', 'daniel', 'hosea', 'joel', 'amos', 'obadiah', 'jonah', 'micah', 'nahum',
        'habakkuk', 'zephaniah', 'haggai', 'zechariah', 'malachi'
    ]
    for book in bible_books:
        if book in first_100:
            # Extract chapter reference
            match = re.search(rf'{book}\s+(chapter\s+)?(\d+)', para_text, re.IGNORECASE)
            if match:
                ch = match.group(2)
                return f"{book.title()} {ch}"
            return book.title()

    # Church Fathers / Historical Figures
    figures = {
        'ignatius': "Ignatius of Antioch",
        'justin martyr': "Justin Martyr",
        'polycarp': "Polycarp",
        'clement': "Clement of Rome",
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
        'arian': "Arius",
        'nestorius': "Nestorius",
        'cyril': "Cyril",
        'gregory': "Gregory",
        'basil': "Basil",
        'ambrose': "Ambrose",
        'jerome': "Jerome",
        'hilary': "Hilary",
        'leo': "Leo the Great",
    }
    for key, heading in figures.items():
        if key in first_100:
            return heading

    # Topics
    topics = {
        'persecution': "Persecution",
        'martyrdom': "Martyrdom",
        'the canon': "The Canon",
        'canon of scripture': "The Canon of Scripture",
        'new testament canon': "The New Testament Canon",
        'old testament canon': "The Old Testament Canon",
        'eucharist': "The Eucharist",
        'baptism': "Baptism",
        "lord's supper": "The Lord's Supper",
        'communion': "Holy Communion",
        'worship': "Worship",
        'prayer': "Prayer",
        'preaching': "Preaching",
        'teaching': "Teaching",
        'gathering': "The Gathering",
        'house church': "House Churches",
        'synagogue': "The Synagogue",
        'temple': "The Temple",
        'gentiles': "The Gentile Mission",
        'great commission': "The Great Commission",
        'diaspora': "The Diaspora",
        'spiritual gifts': "Spiritual Gifts",
        'speaking in tongues': "Speaking in Tongues",
        'prophecy': "Prophecy",
        'leadership': "Leadership",
        'elders': "Elders",
        'deacons': "Deacons",
        'bishops': "Bishops",
        'apostles': "The Apostles",
        'apostolic fathers': "The Apostolic Fathers",
        'church fathers': "The Church Fathers",
        'monasticism': "Monasticism",
        'fasting': "Fasting",
        'liturgy': "Liturgy",
        'sacraments': "Sacraments",
        'tradition': "Tradition",
        'doctrine': "Doctrine",
        'theology': "Theology",
        'orthodoxy': "Orthodoxy",
        'heresy': "Heresy",
        'gnosticism': "Gnosticism",
        'trinity': "The Trinity",
        'christology': "Christology",
        'incarnation': "The Incarnation",
        'resurrection': "The Resurrection",
        'ascension': "The Ascension",
        'pentecost': "Pentecost",
        'holy spirit': "The Holy Spirit",
        'salvation': "Salvation",
        'justification': "Justification",
        'sanctification': "Sanctification",
        'faith': "Faith",
        'grace': "Grace",
        'gospel': "The Gospel",
        'kingdom of god': "The Kingdom of God",
        'kingdom of heaven': "The Kingdom of Heaven",
        'church': "The Church",
        'unity': "Unity",
        'diversity': "Diversity",
        'culture': "Culture",
        'context': "Context",
        'background': "Background",
        'setting': "Setting",
        'historical context': "Historical Context",
        'cultural context': "Cultural Context",
        'political context': "Political Context",
        'social context': "Social Context",
        'religious context': "Religious Context",
        'jewish background': "Jewish Background",
        'gentile background': "Gentile Background",
        'roman background': "Roman Background",
        'greek background': "Greek Background",
        'hellenistic': "Hellenistic Background",
        'mediterranean': "The Mediterranean World",
        'ancient world': "The Ancient World",
        'classical world': "The Classical World",
        'patristic': "The Patristic Period",
        'reformation': "The Reformation",
        'crusades': "The Crusades",
        'inquisition': "The Inquisition",
        'plague': "The Plague",
        'black death': "The Black Death",
        'renaissance': "The Renaissance",
        'enlightenment': "The Enlightenment",
        'great schism': "The Great Schism",
        'east-west schism': "The East-West Schism",
        'protestant reformation': "The Protestant Reformation",
        'luther': "Martin Luther",
        'calvin': "John Calvin",
        'zwingli': "Ulrich Zwingli",
        'wesley': "John Wesley",
        'whitefield': "George Whitefield",
        'spurgeon': "Charles Spurgeon",
        'edwards': "Jonathan Edwards",
        'puritans': "The Puritans",
        'pilgrims': "The Pilgrims",
        'american revolution': "The American Revolution",
        'french revolution': "The French Revolution",
        'industrial revolution': "The Industrial Revolution",
        'world war': "World War",
        'cold war': "The Cold War",
        'vatican': "The Vatican",
        'pope': "The Pope",
        'papacy': "The Papacy",
        'orthodox church': "The Orthodox Church",
        'eastern orthodox': "The Eastern Orthodox Church",
        'oriental orthodox': "The Oriental Orthodox Church",
        'anglican': "The Anglican Church",
        'episcopal': "The Episcopal Church",
        'methodist': "The Methodist Church",
        'baptist': "The Baptist Church",
        'presbyterian': "The Presbyterian Church",
        'lutheran': "The Lutheran Church",
        'reformed': "The Reformed Church",
        'congregational': "The Congregational Church",
        'pentecostal': "The Pentecostal Church",
        'charismatic': "The Charismatic Church",
        'evangelical': "The Evangelical Church",
        'fundamentalist': "The Fundamentalist Church",
        'liberal': "The Liberal Church",
        'conservative': "The Conservative Church",
        'progressive': "The Progressive Church",
        'emergent': "The Emergent Church",
    }
    for key, heading in topics.items():
        if key in first_100:
            return heading

    # Transition phrases indicating new section
    transitions = [
        (r'(?i)\bnow\s+let\'s\s+(look\s+at|turn\s+to|examine|consider)\b', None),
        (r'(?i)\blet\'s\s+(look\s+at|turn\s+to|examine|consider)\b', None),
        (r'(?i)\bmoving\s+on\s+to\b', None),
        (r'(?i)\bturning\s+now\s+to\b', None),
        (r'(?i)\bthis\s+brings\s+us\s+to\b', None),
        (r'(?i)\bwhich\s+brings\s+us\s+to\b', None),
        (r'(?i)\bnext\s+we\s+(have|see|look\s+at|turn\s+to)\b', None),
        (r'(?i)\bthe\s+next\s+(thing|point|topic|subject)\b', None),
        (r'(?i)\bgoing\s+back\s+to\b', None),
        (r'(?i)\bso\s+let\'s\s+(look\s+at|turn\s+to|examine|consider)\b', None),
    ]
    for pattern, _ in transitions:
        if re.search(pattern, para_text):
            # Extract what comes after the transition
            match = re.search(r'(?:look at|turn to|examine|consider)\s+(.{5,60})', para_text, re.IGNORECASE)
            if match:
                topic = match.group(1).strip().rstrip(',.;')
                if len(topic) > 3 and len(topic) < 60:
                    return topic.title()
            return "Continuing the Discussion"

    return None


def add_headings(text, title):
    """Add content-based headings at natural topic shifts."""
    paragraphs = text.split('\n\n')

    sections = []
    current_heading = title
    current_content = []

    for para in paragraphs:
        if not para.strip():
            continue

        # Check for new heading
        new_heading = detect_heading(para, title)

        if new_heading and new_heading != current_heading and len(current_content) > 0:
            # Save current section
            sections.append((current_heading, current_content))
            current_heading = new_heading
            current_content = [para]
        else:
            current_content.append(para)

    if current_content:
        sections.append((current_heading, current_content))

    # Build output
    lines = []
    for heading, paras in sections:
        lines.append(f"## {heading}")
        lines.append('')
        lines.extend(paras)
        lines.append('')

    return '\n'.join(lines)


def build_markdown(episode_code, title, date, video_id, body):
    """Build final markdown with Pleros-style formatting."""
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

{body}

## Closing

Thank you for listening to Church History and Theology. We hope this episode has enriched your understanding of the church's history and deepened your appreciation for the theological foundations of our faith.

Don't forget to subscribe to our podcast and follow us on social media for more content on church history and theology.
"""

    return filename, md


def main():
    txt_files = sorted(glob.glob(os.path.join(BASE_DIR, "*_clean.txt")))

    for txt_path in txt_files:
        basename = os.path.basename(txt_path)

        # Extract video ID
        match = re.search(r'\[([a-zA-Z0-9_-]+)\]', basename)
        if not match:
            continue
        video_id = match.group(1)

        # Extract episode code from filename
        ep_match = re.search(r'(S\d+E\d+)', basename)
        episode_code = ep_match.group(1) if ep_match else ""

        if not episode_code:
            continue

        # Skip if already exists
        expected = f"{episode_code.lower()}-*.md"
        existing = glob.glob(os.path.join(BASE_DIR, expected))
        if existing:
            print(f"Skipping {episode_code} - exists")
            continue

        # Read raw text
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # Process
        text = clean_fillers(text)
        text = remove_template(text)
        body = format_body(text)
        body = add_headings(body, episode_code)

        # Get metadata from filename/title patterns
        raw_title = basename.replace('_clean.txt', '').replace('[', '').replace(']', '')
        # Clean up the title
        title = re.sub(r'^CHT\s+\|\s+', '', raw_title)
        title = re.sub(r'^CHT\s+S\d+E\d+\s*[:\-]?\s*', '', title)
        title = re.sub(r'^S\d+E\d+[:\-]?\s*', '', title)
        title = re.sub(r'^Resource[:\-]?\s*', 'Resource: ', title)
        title = title.strip()

        # Extract date from video ID via yt-dlp or use placeholder
        date = "2024-01-01"  # Will be updated

        filename, md = build_markdown(episode_code, title, date, video_id, body)

        filepath = os.path.join(BASE_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md)

        print(f"Created: {filename}")


if __name__ == '__main__':
    main()
