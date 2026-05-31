import re

# Inject into translations.js
with open("frontend/src/translations.js", "r", encoding="utf-8") as f:
    js_code = f.read()

with open("scratch_en_signs.txt", "r", encoding="utf-8") as f:
    en_signs = f.read()

with open("scratch_en_dict.txt", "r", encoding="utf-8") as f:
    en_dict = f.read()
    
with open("scratch_fr_signs.txt", "r", encoding="utf-8") as f:
    fr_signs = f.read()

with open("scratch_fr_dict.txt", "r", encoding="utf-8") as f:
    fr_dict = f.read()

# Replace en signs
js_code = re.sub(
    r'    signs: \{\n.*?    \},', 
    en_signs, 
    js_code, 
    count=1,
    flags=re.DOTALL
)

# Append to en dictionarySigns
js_code = re.sub(
    r'      "water": \{ category: "Noun", complexity: "Medium", description: "Form \'W\' shape with active hand \(index, middle, ring finger up\) and tap index finger against chin twice\." \}\n    \}',
    '      "water": { category: "Noun", complexity: "Medium", description: "Form \'W\' shape with active hand (index, middle, ring finger up) and tap index finger against chin twice." },\n' + en_dict.replace("    dictionarySigns: {\n", "") + "    }",
    js_code,
    count=1
)

# Replace fr signs
# (We need to replace the second occurrence of signs: {})
js_code = re.sub(
    r'    signs: \{\n.*?    \},', 
    lambda m: m.group(0) if "Bonjour" not in m.group(0) else fr_signs, # Only replace the french one? wait, simpler to just match 'fr: {'
    js_code, 
    flags=re.DOTALL
)
# Actually let's do a better replacement for fr_signs
parts = js_code.split("  fr: {")
if len(parts) == 2:
    en_part = parts[0]
    fr_part = parts[1]
    
    fr_part = re.sub(
        r'    signs: \{\n.*?    \},', 
        fr_signs.replace("    signs: {\n", "    signs: {\n      \"hello\": \"Bonjour\",\n      \"thank you\": \"Merci\",\n      \"please\": \"S'il vous plaît\",\n      \"yes\": \"Oui\",\n      \"no\": \"Non\",\n      \"help\": \"Aide\",\n      \"sorry\": \"Pardon\",\n      \"love\": \"Amour\",\n      \"good\": \"Bien\",\n      \"bad\": \"Mauvais\",\n      \"eat\": \"Manger\",\n      \"water\": \"Eau\",\n") + "    },", 
        fr_part, 
        count=1,
        flags=re.DOTALL
    )
    
    fr_part = re.sub(
        r'      "water": \{ category: "Nom", complexity: "Moyenne", description: "Formez la forme \'W\' avec la main active \(index, majeur, annulaire levés\) et tapez l\'index contre le menton deux fois\." \}\n    \}',
        '      "water": { category: "Nom", complexity: "Moyenne", description: "Formez la forme \'W\' avec la main active (index, majeur, annulaire levés) et tapez l\'index contre le menton deux fois." },\n' + fr_dict.replace("    dictionarySigns: {\n", "") + "    }",
        fr_part,
        count=1
    )
    
    js_code = en_part + "  fr: {" + fr_part

with open("frontend/src/translations.js", "w", encoding="utf-8") as f:
    f.write(js_code)


# Inject into Dictionary.jsx
with open("frontend/src/pages/Dictionary.jsx", "r", encoding="utf-8") as f:
    dict_code = f.read()

with open("scratch_demo_signs.txt", "r", encoding="utf-8") as f:
    demo_signs = f.read()
    
dict_code = re.sub(
    r'      \{ sign: \'water\'.*?\}\n\];',
    "{ sign: 'water', category: 'Noun', complexity: 'Medium', description: 'Form \"W\" shape with active hand (index, middle, ring finger up) and tap index finger against chin twice.' },\n" + demo_signs.replace("const DEMO_SIGNS = [\n", ""),
    dict_code,
    count=1,
    flags=re.DOTALL
)

with open("frontend/src/pages/Dictionary.jsx", "w", encoding="utf-8") as f:
    f.write(dict_code)
