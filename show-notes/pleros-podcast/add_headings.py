import re

def add_headings_to_file(filepath, headings_map):
    """Add content-based headings at specific paragraph starts.
    headings_map: dict of search_text -> heading_text
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into paragraphs
    paragraphs = content.split('\n\n')
    new_paragraphs = []
    last_heading = None
    
    for para in paragraphs:
        # Skip if it's already a heading or frontmatter
        if para.startswith('#') or para.startswith('---'):
            new_paragraphs.append(para)
            continue
        
        # Check if paragraph starts with a topic marker
        para_start = para[:120].lower()
        added_heading = False
        
        for marker, heading in headings_map.items():
            if marker.lower() in para_start and heading != last_heading:
                new_paragraphs.append(f"## {heading}")
                new_paragraphs.append('')
                last_heading = heading
                added_heading = True
                break
        
        new_paragraphs.append(para)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(new_paragraphs))
    
    print(f"Updated {filepath}")

# Episode 132 headings
ep132_headings = {
    "we're looking at the subject matter, preservation": "Preservation in the Newness of Life",
    "we looked at healing first": "What Is Available in the Newness of Life",
    "there are those who always feel the concern": "A Word of Caution on Natural Benefits",
    "what is available to us relative to the state of the cosmos": "The Sick State of the Cosmos",
    "matthew chapter 21, the fig tree": "The Fig Tree and Authority Over Creation",
    "mark's account": "Faith and the Spoken Word",
    "this case is with paul": "Paul's Journey and Preservation",
    "matthew chapter 26": "The Ministry of Angels",
    "the temptation of the lord": "Temptation and Wrong Motives",
}

# Episode 133 headings  
ep133_headings = {
    "preservation in the newness of life": "Preservation in the Newness of Life",
    "psalm 91": "Psalm 91 and Divine Protection",
    "old testament": "Old Testament Examples of Preservation",
    "hezekiah": "Hezekiah's Preservation",
    "david": "David and Divine Protection",
    "elijah": "Elijah and the Prophets",
    "closing charge": "Closing Charge",
}

# Episode 134 headings
ep134_headings = {
    "preservation in the newness of life": "Preservation in the Newness of Life",
    "romans 8": "The Spirit of Life in Christ",
    "the flesh": "Walking in the Spirit vs the Flesh",
    "psalm 34": "The Lord Delivers the Righteous",
    "acts 12": "Peter's Deliverance from Prison",
    "acts 5": "The Apostles and Angelic Deliverance",
}

# Episode 135 headings
ep135_headings = {
    "preservation in the newness of life": "Preservation in the Newness of Life",
    "acts 16": "Paul and Silas in Prison",
    "the philippian jailer": "The Philippian Jailer",
    "acts 28": "Paul on Malta",
    "the snake": "The Snake and Preservation",
    "the shipwreck": "The Shipwreck",
}

# Episode 136 headings
ep136_headings = {
    "preservation in the newness of life": "Preservation in the Newness of Life",
    "the lord's prayer": "The Lord's Prayer and Preservation",
    "deliver us from evil": "Deliver Us from Evil",
    "john 17": "Jesus Prays for His Disciples",
    "the high priestly prayer": "The High Priestly Prayer",
    "closing": "Closing Charge",
}

all_headings = {
    'episode-132-preservation-in-the-newness-of-life-part-4.md': ep132_headings,
    'episode-133-preservation-in-the-newness-of-life-part-5.md': ep133_headings,
    'episode-134-preservation-in-the-newness-of-life-part-6.md': ep134_headings,
    'episode-135-preservation-in-the-newness-of-life-part-7.md': ep135_headings,
    'episode-136-preservation-in-the-newness-of-life-part-8.md': ep136_headings,
}

for filename, headings in all_headings.items():
    add_headings_to_file(filename, headings)
