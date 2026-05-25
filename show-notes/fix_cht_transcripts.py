#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path("/Users/letroot/Documents/notes/obsidian-vaults/letroot-md/show-notes")
TARGET_DIRS = [
    ROOT / "CHT-1st-Century",
    ROOT / "CHT-Deep-Dives",
    ROOT / "CHT-Modern-Church",
]

NOTE_PATTERNS = ["s2e*.md", "cht-s2e*.md", "dd*.md", "mc*.md"]

BOOK_NAMES = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth",
    "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah",
    "Esther", "Job", "Psalm", "Psalms", "Proverbs", "Ecclesiastes", "Isaiah", "Jeremiah", "Ezekiel",
    "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
    "Haggai", "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans",
    "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians",
    "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews",
    "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation",
]

BOOK_RE = re.compile(
    r"^(?:" + "|".join(re.escape(book) for book in BOOK_NAMES) + r")(?:\s+(?:Chapter\s+)?)?\s*\d+\b",
    re.IGNORECASE,
)

INTRO_NOISE = [
    "well good evening everyone",
    "good evening everyone",
    "well greetings everyone",
    "greetings everyone",
    "thank you for pointing that out",
    "let me check the audio",
    "i'm gonna go and turn off my fan",
    "my mic was still muted",
]

CHATTER_SNIPPETS = [
    "podcast",
    "fan",
    "audio",
    "sound",
    "live",
    "muted",
    "three-year-old",
    "description",
]

TOPIC_MARKERS = [
    "now",
    "well",
    "and so",
    "so",
    "but",
    "then",
    "the problem is",
    "one of the things",
    "this is where",
    "that brings us",
    "let's talk about",
    "let's go into",
    "here's the thing",
    "all that to say",
    "in addition to this",
    "on the other hand",
]

INTERNAL_SPLIT_RE = re.compile(
    r"\s+(?=(?:and so|on the other hand|all that to say|that brings us|now|but|then|so)\b)",
    re.IGNORECASE,
)


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return "", text
    return parts[0] + "\n---\n", parts[1]


def parse_note(path: Path) -> tuple[str, str, str, list[str]]:
    original = path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(original)
    lines = body.splitlines()
    title_block: list[str] = []
    i = 0
    while i < len(lines) and not lines[i].startswith("# "):
        if lines[i].strip():
            title_block.append(lines[i])
        i += 1
    title_line = lines[i] if i < len(lines) else "# Untitled"
    rest = lines[i + 1 :] if i < len(lines) else []
    return original, frontmatter, title_line, rest


def title_keywords(title_line: str) -> list[str]:
    title = title_line.removeprefix("# ").lower()
    title = re.sub(r"[^a-z0-9\s]", " ", title)
    words = [word for word in title.split() if len(word) > 3]
    stop = {"church", "history", "deep", "dive", "century", "modern"}
    return [word for word in words if word not in stop]


def title_phrase(title_line: str) -> str:
    title = title_line.removeprefix("# ").lower()
    title = re.sub(r"[^a-z0-9\s]", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def extract_video_id(frontmatter: str) -> str | None:
    match = re.search(r"youtube\.com/watch\?v=([A-Za-z0-9_-]{11})", frontmatter)
    return match.group(1) if match else None


def parse_time(value: str) -> float:
    h, m, s = value.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def clean_cue_text(text: str) -> str:
    text = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", " ", text)
    text = re.sub(r"</?c>", " ", text)
    text = text.replace("&gt;&gt;", "")
    text = text.replace("[Music]", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_vtt(vtt_path: Path) -> list[tuple[float, float, str]]:
    text = vtt_path.read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*\n", text)
    cues: list[tuple[float, float, str]] = []
    for block in blocks:
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        time_line = next((line for line in lines if "-->" in line), None)
        if not time_line:
            continue
        start_raw, end_raw = [part.strip().split()[0] for part in time_line.split("-->")]
        payload = [line for line in lines if line != time_line and line not in {"WEBVTT", "Kind: captions", "Language: en"}]
        if not payload:
            continue
        cue_text = clean_cue_text(payload[-1])
        if not cue_text:
            continue
        cues.append((parse_time(start_raw), parse_time(end_raw), cue_text))
    return cues


def overlap_suffix_prefix(existing: str, new: str, max_words: int = 12) -> int:
    existing_words = existing.split()
    new_words = new.split()
    limit = min(max_words, len(existing_words), len(new_words))
    for size in range(limit, 0, -1):
        if existing_words[-size:] == new_words[:size]:
            return size
    return 0


def merge_cues(cues: list[tuple[float, float, str]]) -> list[tuple[float, float, str]]:
    merged: list[tuple[float, float, str]] = []
    current_text = ""
    current_start = 0.0
    current_end = 0.0

    for cue_start, cue_end, cue_text in cues:
        if not current_text:
            current_text = cue_text
            current_start = cue_start
            current_end = cue_end
            continue

        overlap = overlap_suffix_prefix(current_text, cue_text)
        cue_words = cue_text.split()
        if overlap > 0:
            suffix = " ".join(cue_words[overlap:]).strip()
            if suffix:
                current_text = f"{current_text} {suffix}".strip()
            current_end = cue_end
            continue

        if cue_text == current_text:
            current_end = cue_end
            continue

        merged.append((current_start, current_end, normalize_text(current_text)))
        current_text = cue_text
        current_start = cue_start
        current_end = cue_end

    if current_text:
        merged.append((current_start, current_end, normalize_text(current_text)))
    return merged


def split_internal_segments(segments: list[tuple[float, float, str]]) -> list[tuple[float, float, str]]:
    expanded: list[tuple[float, float, str]] = []
    for start, end, text in segments:
        parts = [part.strip() for part in INTERNAL_SPLIT_RE.split(text) if part.strip()]
        if len(parts) == 1:
            expanded.append((start, end, text))
            continue
        for part in parts:
            expanded.append((start, end, normalize_text(part)))
    return expanded


def normalize_text(text: str) -> str:
    text = re.sub(r"\b(uh|um|ah|er|hmm)\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(\w+)\s+\1\b", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    text = text.strip(" ,")
    return text.strip()


def trim_intro(segments: list[tuple[float, float, str]], title_text: str, keywords: list[str]) -> list[tuple[float, float, str]]:
    trimmed = list(segments)
    while trimmed:
        lower = trimmed[0][2].lower()
        if any(lower.startswith(prefix) for prefix in INTRO_NOISE):
            trimmed.pop(0)
            continue
        break

    if keywords:
        anchor_idx = None
        for idx, (_start, _end, text) in enumerate(trimmed[:18]):
            lower = text.lower()
            if title_text and title_text in lower:
                anchor_idx = idx
                break
        if anchor_idx is None:
            for idx, (_start, _end, text) in enumerate(trimmed[:18]):
                lower = text.lower()
                if any(keyword in lower for keyword in keywords):
                    anchor_idx = idx
                    break
        if anchor_idx and anchor_idx > 0:
            trimmed = trimmed[anchor_idx:]

    # Strip front-loaded livestream chatter that survives the anchor match.
    while trimmed[:8]:
        lower = trimmed[0][2].lower()
        if any(snippet in lower for snippet in CHATTER_SNIPPETS):
            trimmed.pop(0)
            continue
        break
    return trimmed


def is_topic_shift(text: str) -> bool:
    lower = text.lower()
    return any(lower.startswith(marker + " ") or lower == marker for marker in TOPIC_MARKERS)


def build_paragraphs(segments: list[tuple[float, float, str]], title_text: str, keywords: list[str]) -> list[str]:
    paragraphs: list[str] = []
    bucket: list[str] = []
    word_count = 0
    last_end = None

    for start, end, text in trim_intro(segments, title_text, keywords):
        if not text:
            continue

        words = len(text.split())
        pause = (start - last_end) if last_end is not None else 0.0
        should_break = False
        if bucket:
            if pause > 1.6:
                should_break = True
            elif word_count >= 30 and is_topic_shift(text):
                should_break = True
            elif word_count + words > 56:
                should_break = True

        if should_break and bucket:
            paragraphs.append(normalize_text(" ".join(bucket)))
            bucket = []
            word_count = 0

        bucket.append(text)
        word_count += words
        last_end = end

    if bucket:
        paragraphs.append(normalize_text(" ".join(bucket)))

    return [paragraph for paragraph in paragraphs if paragraph]


def infer_heading(paragraph_text: str, used: set[str]) -> str:
    match = BOOK_RE.search(paragraph_text)
    if match:
        heading = re.sub(r"\s+", " ", match.group(0)).title()
        if heading not in used:
            return heading

    keyword_map = [
        ("Historical Background", ["century", "born", "city", "empire", "rome", "history", "background"]),
        ("Biblical Framework", ["scripture", "bible", "gospel", "acts", "matthew", "romans", "galatians", "ephesians"]),
        ("Key Developments", ["council", "movement", "persecution", "controversy", "reformation", "seminary", "revival"]),
        ("Theological Significance", ["theology", "doctrine", "church", "authority", "salvation", "christology"]),
        ("Legacy And Impact", ["legacy", "influence", "future", "modern", "impact"]),
        ("Main Discussion", []),
    ]
    lower = paragraph_text.lower()
    for heading, words in keyword_map:
        if heading in used:
            continue
        if not words or any(word in lower for word in words):
            return heading

    n = 2
    while f"Main Discussion {n}" in used:
        n += 1
    return f"Main Discussion {n}"


def build_sections_from_paragraphs(paragraphs: list[str]) -> list[tuple[str, list[str]]]:
    if not paragraphs:
        return [("Introduction", []), ("Closing", [])]

    def is_chatter_paragraph(text: str) -> bool:
        lower = text.lower()
        return any(snippet in lower for snippet in CHATTER_SNIPPETS) or any(prefix in lower for prefix in INTRO_NOISE)

    cleaned = list(paragraphs)
    while cleaned and is_chatter_paragraph(cleaned[0]):
        cleaned.pop(0)
    paragraphs = cleaned or paragraphs

    intro_count = 1 if len(paragraphs) < 6 else 2
    intro = paragraphs[:intro_count]
    body = paragraphs[intro_count:]
    if not body:
        return [("Introduction", intro), ("Closing", [])]

    target_sections = 3 if len(body) > 6 else 2
    chunk_size = max(1, len(body) // target_sections)
    grouped = [body[i : i + chunk_size] for i in range(0, len(body), chunk_size)]
    if len(grouped) > target_sections + 1:
        grouped[-2].extend(grouped[-1])
        grouped.pop()

    used: set[str] = set()
    result: list[tuple[str, list[str]]] = [("Introduction", intro)]
    for group in grouped:
        heading = infer_heading(" ".join(group), used)
        used.add(heading)
        result.append((heading, group))
    result.append(("Closing", []))
    return result


def rebuild_note(path: Path) -> bool:
    original, frontmatter, title_line, _rest = parse_note(path)
    title_text = title_phrase(title_line)
    keywords = title_keywords(title_line)
    video_id = extract_video_id(frontmatter)
    if not video_id:
        return False
    vtt_matches = [candidate for candidate in path.parent.glob("*.en.vtt") if f"[{video_id}]" in candidate.name]
    if not vtt_matches:
        return False
    cues = parse_vtt(vtt_matches[0])
    merged_segments = split_internal_segments(merge_cues(cues))
    paragraphs = build_paragraphs(merged_segments, title_text, keywords)
    sections = build_sections_from_paragraphs(paragraphs)

    out: list[str] = []
    if frontmatter:
        out.append(frontmatter.rstrip("\n"))
        out.append("")
    out.append(title_line)
    out.append("")
    for heading, paras in sections:
        out.append(f"## {heading}")
        out.append("")
        for para in paras:
            out.append(para)
            out.append("")
    new_text = "\n".join(out).rstrip() + "\n"
    if new_text != original:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def iter_note_files() -> list[Path]:
    files: list[Path] = []
    for folder in TARGET_DIRS:
        for pattern in NOTE_PATTERNS:
            files.extend(folder.glob(pattern))
    return sorted(set(files))


def main() -> None:
    changed = 0
    for note in iter_note_files():
        if rebuild_note(note):
            changed += 1
            print(f"updated {note}")
    print(f"changed {changed} files")


if __name__ == "__main__":
    main()
