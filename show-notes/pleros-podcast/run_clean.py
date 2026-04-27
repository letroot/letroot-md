from clean_vtt import clean_vtt

text115 = clean_vtt('ep115.en.vtt')
with open('ep115_clean.txt', 'w', encoding='utf-8') as f:
    f.write(text115)

text116 = clean_vtt('ep116.en.vtt')
with open('ep116_clean.txt', 'w', encoding='utf-8') as f:
    f.write(text116)
