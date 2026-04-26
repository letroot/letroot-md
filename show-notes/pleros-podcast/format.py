import re

with open("ep114_clean.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Make single string
text = " ".join(text.split())

replacements = [
    ("Welcome back to the Plleos podcast.", "\n\n## Introduction\n\nWelcome back to the Plleos podcast."),
    ("Now you remember what brought us to this juncture", "\n\n## Growing in the Newness of Life\n\nNow you remember what brought us to this juncture"),
    ("So next question we ask is what then is available to our body", "\n\nSo next question we ask is what then is available to our body"),
    ("So if you have that in mind", "\n\nSo if you have that in mind"),
    ("If the Bible is the revelation of God,", "\n\nIf the Bible is the revelation of God,"),
    ("Now we have had to make some clarification", "\n\n## Redemption Makes Healing Available\n\nNow we have had to make some clarification"),
    ("Now having said that we also took a look at the place of natural healing", "\n\n## Managing the Cosmos and Natural Healing\n\nNow having said that we also took a look at the place of natural healing"),
    ("First Corinthians chapter 3,", "\n\nFirst Corinthians chapter 3,"),
    ("All right. So this is a very important understanding", "\n\nAll right. So this is a very important understanding"),
    ("well I haven't said that we said healing is available", "\n\nwell I haven't said that we said healing is available"),
    ("But now, let's get into it. If our conclusion is this that healing is available in the newness of life.", "\n\n## Healing is Effected by Faith\n\nBut now, let's get into it. If our conclusion is this that healing is available in the newness of life."),
    ("So how is healing affected?", "\n\nSo how is healing affected?"),
    ("What I'm going to do is start with an account", "\n\n## Biblical Accounts of Healing by Faith\n\nWhat I'm going to do is start with an account"),
    ("Now what we think that faith is might be a debate", "\n\nNow what we think that faith is might be a debate"),
    ("In Mark chapter 9 and in verse two", "\n\nIn Mark chapter 9 and in verse two"),
    ("We trust you were blessed by today's episode.", "\n\n## Conclusion\n\nWe trust you were blessed by today's episode.")
]

for old, new in replacements:
    old_clean = " ".join(old.split())
    text = text.replace(old_clean, new)

with open("episode-114-healing-in-the-newness-of-life-part-10.md", "w", encoding="utf-8") as f:
    f.write(text.strip())
