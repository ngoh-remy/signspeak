import re
with open('src/translations.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"tree": "Arbre",\n\n    dictionarySigns: {', '"tree": "Arbre"\n    },\n    dictionarySigns: {')

with open('src/translations.js', 'w', encoding='utf-8') as f:
    f.write(content)
