import json

with open('frontend/src/translations.js', 'r', encoding='utf-8') as f:
    content = f.read()

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

missing_dict = []
for word in TRAINED_WORDS:
    if f'"{word}": {{ category:' not in content:
        missing_dict.append(word)

print('Missing dictionarySigns:', missing_dict)

missing_fr = []
for word in TRAINED_WORDS:
    if f'"{word}": "' not in content:
        missing_fr.append(word)
print('Missing fr signs:', missing_fr)
