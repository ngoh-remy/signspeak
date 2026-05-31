import json
import re

# We already have 12 words. Let's define 88 more words to make exactly 100.
extra_words = [
    ("mother", "Mère", "Person", "Low", "Tap thumb of open hand on chin repeatedly."),
    ("father", "Père", "Person", "Low", "Tap thumb of open hand on forehead repeatedly."),
    ("boy", "Garçon", "Person", "Low", "Grasp an imaginary baseball cap brim at forehead."),
    ("girl", "Fille", "Person", "Low", "Trace thumb of A-handshape along the jawline."),
    ("baby", "Bébé", "Person", "Low", "Cradle imaginary baby in arms and rock gently."),
    ("friend", "Ami", "Person", "Medium", "Hook index fingers of both hands together, then switch."),
    ("family", "Famille", "Person", "Medium", "Form 'F' handshapes, touch index fingers, then bring around in a circle to touch pinkies."),
    ("today", "Aujourd'hui", "Time", "Medium", "Form 'Y' handshapes with both hands, bounce them downward twice."),
    ("tomorrow", "Demain", "Time", "Low", "Place 'A' handshape thumb on cheek, move it forward into future."),
    ("yesterday", "Hier", "Time", "Low", "Place 'A' handshape thumb on chin, move it backward to jawbone."),
    ("now", "Maintenant", "Time", "Low", "Form 'Y' handshapes with both hands, drop them sharply down once."),
    ("morning", "Matin", "Time", "Medium", "Place one flat hand in the crook of other arm, raise the active arm like the sun rising."),
    ("night", "Nuit", "Time", "Medium", "Rest wrists of bent hands on each other, active hand over inactive."),
    ("day", "Jour", "Time", "Medium", "Rest active elbow on back of inactive hand, lower active arm like sun setting."),
    ("week", "Semaine", "Time", "Medium", "Slide index finger of active hand across flat palm of inactive hand."),
    ("month", "Mois", "Time", "Medium", "Slide index finger of active hand down the back of index finger of inactive hand."),
    ("year", "Année", "Time", "Medium", "Revolve active fist completely around inactive fist, landing on top."),
    ("want", "Vouloir", "Action", "Low", "Hold hands open, palms up, then pull toward body while curving fingers."),
    ("like", "Aimer", "Action", "Low", "Place thumb and middle finger on chest, pull away while bringing them together."),
    ("go", "Aller", "Action", "Low", "Point index fingers away from body and move hands forward."),
    ("come", "Venir", "Action", "Low", "Point index fingers toward body and pull hands inward."),
    ("see", "Voir", "Action", "Low", "Form 'V' handshape at eyes, move hand forward."),
    ("know", "Savoir", "Action", "Low", "Tap side of forehead with bent flat hand."),
    ("think", "Penser", "Action", "Low", "Tap index finger on side of forehead."),
    ("learn", "Apprendre", "Action", "Medium", "Place flat active hand on inactive palm, pull up to forehead while closing fingers."),
    ("work", "Travail", "Action", "Medium", "Tap wrist of active 'S' handshape on top of wrist of inactive 'S' handshape."),
    ("play", "Jouer", "Action", "Low", "Form 'Y' handshapes with both hands, twist wrists back and forth."),
    ("sleep", "Dormir", "Action", "Low", "Draw hand down over face while closing fingers and eyes."),
    ("stop", "Arrêter", "Action", "Medium", "Chop active flat hand sharply into palm of inactive hand."),
    ("house", "Maison", "Noun", "Medium", "Form a roof shape with flat hands, then move hands down to form walls."),
    ("car", "Voiture", "Noun", "Low", "Hold imaginary steering wheel with both hands and move up and down."),
    ("book", "Livre", "Noun", "Low", "Hold hands together flat, open them like a book."),
    ("school", "École", "Noun", "Low", "Clap flat hands together twice horizontally."),
    ("money", "Argent", "Noun", "Medium", "Tap back of active flattened 'O' handshape against flat palm of inactive hand."),
    ("food", "Nourriture", "Noun", "Low", "Bring active hand in closed 'O' handshape to mouth repeatedly."),
    ("happy", "Heureux", "Emotion", "Medium", "Brush flat open hands upward on chest twice."),
    ("sad", "Triste", "Emotion", "Low", "Hold open hands in front of face, bring down while dropping facial expression."),
    ("angry", "En colère", "Emotion", "Medium", "Form claw handshape on chest and pull forcefully outward/upward."),
    ("beautiful", "Beau", "Emotion", "Medium", "Trace circle around face with open hand, closing into flat 'O' at chin."),
    ("ugly", "Laid", "Emotion", "Low", "Drag index finger across upper lip while contorting face."),
    ("big", "Grand", "Description", "Low", "Start with 'L' handshapes together, pull apart widely."),
    ("small", "Petit", "Description", "Low", "Hold flat hands facing each other, push them close together."),
    ("hot", "Chaud", "Description", "Low", "Form claw handshape at mouth, quickly turn and throw outward."),
    ("cold", "Froid", "Description", "Low", "Make fists with both hands and shake arms as if shivering."),
    ("who", "Qui", "Question", "Low", "Place thumb on chin, wiggle index finger up and down."),
    ("what", "Quoi", "Question", "Low", "Hold both open hands palms up, move side to side."),
    ("where", "Où", "Question", "Low", "Hold up index finger, shake back and forth rapidly."),
    ("when", "Quand", "Question", "Medium", "Hold inactive index finger up, circle active index finger around and touch it."),
    ("why", "Pourquoi", "Question", "Medium", "Touch forehead with flat hand, pull away into 'Y' handshape."),
    ("how", "Comment", "Question", "Medium", "Place curved hands back-to-back, roll them forward so palms face up."),
    ("red", "Rouge", "Color", "Low", "Stroke index finger down the lips."),
    ("blue", "Bleu", "Color", "Low", "Form 'B' handshape, twist wrist back and forth."),
    ("green", "Vert", "Color", "Low", "Form 'G' handshape, twist wrist back and forth."),
    ("yellow", "Jaune", "Color", "Low", "Form 'Y' handshape, twist wrist back and forth."),
    ("black", "Noir", "Color", "Low", "Draw side of index finger across forehead."),
    ("white", "Blanc", "Color", "Low", "Place flat hand on chest, pull away into flat 'O' handshape."),
    ("dog", "Chien", "Noun", "Medium", "Pat leg twice, then snap fingers."),
    ("cat", "Chat", "Noun", "Low", "Pinch thumb and index fingers at cheeks and pull outwards like whiskers."),
    ("bird", "Oiseau", "Noun", "Low", "Form 'L' handshape with index/thumb at mouth, mimic beak opening/closing."),
    ("fish", "Poisson", "Noun", "Medium", "Hold flat hand out, wiggle wrist while moving forward."),
    ("walk", "Marcher", "Action", "Medium", "Hold flat hands pointing down, swing alternately mimicking feet."),
    ("run", "Courir", "Action", "High", "Hook active index finger on inactive thumb, move both forward quickly."),
    ("jump", "Sauter", "Action", "Medium", "Stand active 'V' fingers on inactive palm, flip 'V' fingers up and down."),
    ("stand", "Se tenir debout", "Action", "Low", "Stand active 'V' fingers on flat inactive palm."),
    ("sit", "S'asseoir", "Action", "Low", "Hook active 'U' fingers over inactive horizontal 'U' fingers."),
    ("read", "Lire", "Action", "Medium", "Point active 'V' fingers at inactive flat palm, move up and down like scanning lines."),
    ("write", "Écrire", "Action", "Medium", "Mimic holding a pen with active hand, scribble across inactive flat palm."),
    ("talk", "Parler", "Action", "Medium", "Tap active index finger to lips repeatedly."),
    ("listen", "Écouter", "Action", "Low", "Cup hand behind ear."),
    ("deaf", "Sourd", "Description", "Low", "Touch index finger from ear to mouth."),
    ("hearing", "Entendant", "Description", "Low", "Place horizontal index finger at lips, roll in small forward circles."),
    ("name", "Nom", "Noun", "Medium", "Tap active 'H' fingers crosswise over inactive 'H' fingers twice."),
    ("age", "Âge", "Noun", "Low", "Pull 'O' handshape downward from chin while closing into 'S' shape."),
    ("number", "Nombre", "Noun", "Medium", "Touch flattened 'O' hands together, twist wrists, touch again."),
    ("time", "Temps", "Time", "Low", "Tap back of inactive wrist with active index finger, as if pointing to watch."),
    ("bathroom", "Toilettes", "Noun", "Low", "Form 'T' handshape, shake side to side."),
    ("drink", "Boire", "Action", "Low", "Mimic holding a cup and tipping it to mouth."),
    ("apple", "Pomme", "Noun", "Medium", "Twist knuckle of active 'X' handshape on cheek."),
    ("shoe", "Chaussure", "Noun", "Medium", "Tap sides of closed fists together twice."),
    ("shirt", "Chemise", "Noun", "Low", "Pinch shirt fabric near shoulder and tug slightly."),
    ("pants", "Pantalon", "Noun", "Medium", "Place both hands on thighs, pull upward into fists."),
    ("doctor", "Médecin", "Person", "Medium", "Tap active 'M' fingertips to inner wrist of inactive arm."),
    ("teacher", "Enseignant", "Person", "High", "Hold 'O' hands at forehead sides, pull forward, drop into 'person' suffix."),
    ("student", "Étudiant", "Person", "High", "Grab imaginary info from inactive palm, place in forehead, drop into 'person' suffix."),
    ("train", "Train", "Noun", "Medium", "Rub active 'H' fingers back and forth over inactive 'H' fingers."),
    ("airplane", "Avion", "Noun", "Low", "Form 'I-love-you' handshape, move forward and upward."),
    ("bicycle", "Vélo", "Noun", "Medium", "Move fists in alternating forward circles, like pedaling."),
    ("tree", "Arbre", "Noun", "Medium", "Stand active arm upright, twist hand like branches.")
]

# Ensure uniqueness and pad out to exactly 100 total
existing = ["hello", "thank you", "please", "yes", "no", "help", "sorry", "love", "good", "bad", "eat", "water"]
to_add = []
for w in extra_words:
    if w[0] not in existing:
        to_add.append(w)

to_add = to_add[:88] # truncate to exactly 88

# 1. Update Ai_model/inference.py
with open("Ai_model/inference.py", "r", encoding="utf-8") as f:
    inf_code = f.read()

all_labels = existing + [w[0] for w in to_add]
labels_str = "[\n" + ",\n".join([f'        "{l}"' for l in all_labels]) + "\n    ]"

inf_code = re.sub(
    r'self\.labels\s*=\s*\[.*?\]', 
    f'self.labels = {labels_str}', 
    inf_code, 
    flags=re.DOTALL
)

with open("Ai_model/inference.py", "w", encoding="utf-8") as f:
    f.write(inf_code)


# 2. Update frontend/src/translations.js
with open("frontend/src/translations.js", "r", encoding="utf-8") as f:
    trans_code = f.read()

def generate_signs_str(words, is_fr=False):
    s = ""
    for w in existing:
        # Keep existing words formatting or just leave them intact
        pass
    # We will just rewrite the entire signs block and dictionarySigns block
    return ""

# Actually, doing this with Python regex might break the JS file. 
# Let's generate the JSON strings and write them to a temp file, 
# then I can copy paste them via multi_replace_file_content.
en_signs = '    signs: {\n'
for w in existing:
    en_signs += f'      "{w}": "{w.title()}",\n'
for w in to_add:
    en_signs += f'      "{w[0]}": "{w[0].title()}",\n'
en_signs += '    },'

en_dict = '    dictionarySigns: {\n'
for w in to_add:
    en_dict += f'      "{w[0]}": {{ category: "{w[2]}", complexity: "{w[3]}", description: "{w[4]}" }},\n'

fr_signs = '    signs: {\n'
fr_dict = '    dictionarySigns: {\n'
for w in to_add:
    fr_signs += f'      "{w[0]}": "{w[1]}",\n'
    c_fr = "Faible" if w[3] == "Low" else "Moyenne" if w[3] == "Medium" else "Élevée"
    cat_fr = "Personne" if w[2] == "Person" else "Temps" if w[2] == "Time" else "Action" if w[2] == "Action" else "Nom" if w[2] == "Noun" else "Émotion" if w[2] == "Emotion" else "Description" if w[2] == "Description" else "Question" if w[2] == "Question" else "Couleur" if w[2] == "Color" else w[2]
    fr_dict += f'      "{w[0]}": {{ category: "{cat_fr}", complexity: "{c_fr}", description: "{w[4]}" }},\n'

with open("scratch_en_signs.txt", "w", encoding="utf-8") as f: f.write(en_signs)
with open("scratch_en_dict.txt", "w", encoding="utf-8") as f: f.write(en_dict)
with open("scratch_fr_signs.txt", "w", encoding="utf-8") as f: f.write(fr_signs)
with open("scratch_fr_dict.txt", "w", encoding="utf-8") as f: f.write(fr_dict)

# 3. Generate DEMO_SIGNS replacement for Dictionary.jsx
demo_str = "const DEMO_SIGNS = [\n"
for w in existing:
    # I'll just skip formatting existing, we will grab it.
    pass
for w in to_add:
    desc = w[4].replace("'", "\\'")
    demo_str += f"  {{ sign: '{w[0]}', category: '{w[2]}', complexity: '{w[3]}', description: '{desc}' }},\n"
demo_str += "];"

with open("scratch_demo_signs.txt", "w", encoding="utf-8") as f: f.write(demo_str)
