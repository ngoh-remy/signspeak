import json
import re

with open('frontend/src/translations.js', 'r', encoding='utf-8') as f:
    content = f.read()

MISSING_EN_SIGNS = {
  "need": "Need", "wait": "Wait", "understand": "Understand", "again": "Again", 
  "finish": "Finish", "more": "More", "less": "Less", "sick": "Sick", "pain": "Pain", 
  "hospital": "Hospital", "home": "Home", "brother": "Brother", "sister": "Sister", 
  "man": "Man", "woman": "Woman", "child": "Child"
}

MISSING_FR_SIGNS = {
  "need": "Besoin", "wait": "Attendre", "understand": "Comprendre", "again": "Encore", 
  "finish": "Terminer", "more": "Plus", "less": "Moins", "sick": "Malade", "pain": "Douleur", 
  "hospital": "Hôpital", "home": "Maison", "brother": "Frère", "sister": "Sœur", 
  "man": "Homme", "woman": "Femme", "child": "Enfant"
}

MISSING_EN_DICT = {
  "need": '{ category: "Action", complexity: "Medium", description: "Form \\\'X\\\' handshape, bend wrist downward repeatedly." }',
  "wait": '{ category: "Action", complexity: "Medium", description: "Hold both hands up with fingers spread, wiggle fingers." }',
  "understand": '{ category: "Action", complexity: "Low", description: "Flick index finger up next to forehead, like a lightbulb turning on." }',
  "again": '{ category: "Action", complexity: "Medium", description: "Bend active hand into right angle, tap fingertips into flat inactive palm." }',
  "finish": '{ category: "Action", complexity: "Low", description: "Hold both hands open, palms facing in, then twist wrists so palms face out." }',
  "more": '{ category: "Description", complexity: "Low", description: "Pinch fingers of both hands together, tap them against each other repeatedly." }',
  "less": '{ category: "Description", complexity: "Low", description: "Hold flat hand over flat hand, then lower the top hand to shrink the gap." }',
  "sick": '{ category: "Description", complexity: "Medium", description: "Touch middle finger of active hand to forehead and inactive middle finger to stomach." }',
  "pain": '{ category: "Description", complexity: "Medium", description: "Point index fingers at each other, jab them inward without touching." }',
  "hospital": '{ category: "Noun", complexity: "Medium", description: "Trace a cross on upper arm with \\\'H\\\' handshape." }',
  "home": '{ category: "Noun", complexity: "Low", description: "Tap flat \\\'O\\\' handshape to chin, then to cheek near ear." }',
  "brother": '{ category: "Person", complexity: "High", description: "Pinch brim of imaginary cap with active \\\'L\\\' hand, then bring down to rest on inactive \\\'L\\\' hand." }',
  "sister": '{ category: "Person", complexity: "High", description: "Draw thumb of active \\\'L\\\' hand along jawline, then bring down to rest on inactive \\\'L\\\' hand." }',
  "man": '{ category: "Person", complexity: "Medium", description: "Touch thumb of open hand to forehead, then to chest." }',
  "woman": '{ category: "Person", complexity: "Medium", description: "Touch thumb of open hand to chin, then to chest." }',
  "child": '{ category: "Person", complexity: "Low", description: "Pat imaginary heads of children, moving hand downward and outward." }'
}

MISSING_FR_DICT = {
  "need": '{ category: "Action", complexity: "Moyenne", description: "Formez la forme \\\'X\\\', pliez le poignet vers le bas de manière répétée." }',
  "wait": '{ category: "Action", complexity: "Moyenne", description: "Tenez les deux mains levées avec les doigts écartés, remuez les doigts." }',
  "understand": '{ category: "Action", complexity: "Faible", description: "Pianotez l\\\'index vers le haut près du front, comme une ampoule qui s\\\'allume." }',
  "again": '{ category: "Action", complexity: "Moyenne", description: "Pliez la main active à angle droit, tapez le bout des doigts dans la paume inactive plate." }',
  "finish": '{ category: "Action", complexity: "Faible", description: "Tenez les deux mains ouvertes, paumes vers l\\\'intérieur, puis tournez les poignets pour que les paumes soient vers l\\\'extérieur." }',
  "more": '{ category: "Description", complexity: "Faible", description: "Pincez les doigts des deux mains ensemble, tapez-les l\\\'un contre l\\\'autre à plusieurs reprises." }',
  "less": '{ category: "Description", complexity: "Faible", description: "Tenez la main plate sur la main plate, puis abaissez la main du haut pour réduire l\\\'écart." }',
  "sick": '{ category: "Description", complexity: "Moyenne", description: "Touchez le majeur de la main active sur le front et le majeur inactif sur l\\\'estomac." }',
  "pain": '{ category: "Description", complexity: "Moyenne", description: "Pointez les index l\\\'un vers l\\\'autre, donnez des petits coups vers l\\\'intérieur sans les toucher." }',
  "hospital": '{ category: "Nom", complexity: "Moyenne", description: "Tracez une croix sur le bras supérieur avec la forme de main \\\'H\\\'." }',
  "home": '{ category: "Nom", complexity: "Faible", description: "Tapez la main plate en \\\'O\\\' sur le menton, puis sur la joue près de l\\\'oreille." }',
  "brother": '{ category: "Personne", complexity: "Élevée", description: "Pincez le bord d\\\'une casquette imaginaire avec la main active en \\\'L\\\', puis abaissez-la pour la poser sur la main inactive en \\\'L\\\'." }',
  "sister": '{ category: "Personne", complexity: "Élevée", description: "Tirez le pouce de la main active en \\\'L\\\' le long de la mâchoire, puis abaissez-la pour la poser sur la main inactive en \\\'L\\\'." }',
  "man": '{ category: "Personne", complexity: "Moyenne", description: "Touchez le pouce de la main ouverte sur le front, puis sur la poitrine." }',
  "woman": '{ category: "Personne", complexity: "Moyenne", description: "Touchez le pouce de la main ouverte sur le menton, puis sur la poitrine." }',
  "child": '{ category: "Personne", complexity: "Faible", description: "Caressez la tête d\\\'enfants imaginaires, en déplaçant la main vers le bas et vers l\\\'extérieur." }'
}

def get_injection_string(injection_dict):
    injection = ""
    for k, v in injection_dict.items():
        if isinstance(v, str) and not v.startswith("{"):
            injection += f'      "{k}": "{v}",\n'
        else:
            injection += f'      "{k}": {v},\n'
    return injection

# 1. en.signs
# Find the end of en.signs
idx1 = content.find("dictionarySigns: {")
if idx1 != -1:
    idx_en_signs_end = content.rfind("    },", 0, idx1)
    content = content[:idx_en_signs_end] + get_injection_string(MISSING_EN_SIGNS) + content[idx_en_signs_end:]

# 2. en.dictionarySigns
idx2 = content.find("  fr: {")
if idx2 != -1:
    idx_en_dict_end = content.rfind("    }", 0, idx2)
    content = content[:idx_en_dict_end] + get_injection_string(MISSING_EN_DICT) + content[idx_en_dict_end:]

# 3. fr.signs
idx3 = content.find("dictionarySigns: {", idx2)
if idx3 != -1:
    idx_fr_signs_end = content.rfind("    },", idx2, idx3)
    content = content[:idx_fr_signs_end] + get_injection_string(MISSING_FR_SIGNS) + content[idx_fr_signs_end:]

# 4. fr.dictionarySigns
idx_fr_dict_end = content.rfind("    }\n  }\n};")
if idx_fr_dict_end != -1:
    content = content[:idx_fr_dict_end] + get_injection_string(MISSING_FR_DICT) + content[idx_fr_dict_end:]

with open('frontend/src/translations.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Injected successfully!")
