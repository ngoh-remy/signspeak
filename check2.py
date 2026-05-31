import json

with open('frontend/src/translations.js', 'r', encoding='utf-8') as f:
    content = f.read()

idx_fr = content.find('  fr: {')
fr_signs_block = content[content.find('    signs: {', idx_fr):content.find('    dictionarySigns: {', idx_fr)]

TRAINED_WORDS = [
  'hello', 'thank you', 'please', 'sorry', 'yes', 'no', 'help',
  'love', 'good', 'bad', 'name', 'what', 'how', 'where', 'who',
  'want', 'need', 'like', 'eat', 'drink', 'go', 'come', 'stop',
  'wait', 'understand', 'again', 'finish', 'more', 'less', 'big',
  'small', 'happy', 'sad', 'angry', 'sick', 'pain', 'doctor',
  'hospital', 'school', 'home', 'family', 'mother', 'father',
  'brother', 'sister', 'friend', 'man', 'woman', 'child',
  'water'
]

missing = []
for w in TRAINED_WORDS:
    if f'"{w}":' not in fr_signs_block:
        missing.append(w)
print('Missing from fr.signs:', missing)
