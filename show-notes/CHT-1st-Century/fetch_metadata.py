#!/usr/bin/env python3
import subprocess
import json

# Playlist ID for 1st Century
playlist = "PLTObO--DQlbCSjrFfC7nOl6dw7zoXQ-3S"

cmd = f'yt-dlp --flat-playlist --print "%(id)s|%(title)s|%(upload_date)s" "https://www.youtube.com/playlist?list={playlist}"'
result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)

metadata = {}
for line in result.stdout.strip().split('\n'):
    if '|' in line:
        parts = line.split('|')
        if len(parts) >= 3:
            vid = parts[0]
            title = parts[1]
            date = parts[2]
            metadata[vid] = {'title': title, 'date': date}

# Save to JSON
import json
with open('metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"Fetched metadata for {len(metadata)} videos")
