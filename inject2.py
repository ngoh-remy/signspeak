import re

with open("c:\\Users\\lenovo\\Desktop\\SignSpeakL\\frontend\\src\\translations.js", "r", encoding="utf-8") as f:
    content = f.read()

# I will just insert before the child entry manually for all 4 spots.
en_signs = """
      "cousin": "Cousin",
      "give": "Give",
      "room": "Room",
      "take": "Take",
      "short": "Short",
      "environment": "Environment",
"""

en_dict = """
      "cousin": { category: "Family", complexity: "Medium", description: "Shake 'C' handshape by the side of the head." },
      "give": { category: "Action", complexity: "Medium", description: "Hold flattened 'O' hands palms up, move them forward and outward." },
      "room": { category: "Noun", complexity: "Medium", description: "Form a box shape with flat hands, moving them to show four walls." },
      "take": { category: "Action", complexity: "Medium", description: "Reach out with open hands, grab imaginary object, and pull it toward you." },
      "short": { category: "Description", complexity: "Low", description: "Hold flat hand palm down, lower it to indicate short height." },
      "environment": { category: "Noun", complexity: "High", description: "Hold inactive hand flat, circle active 'E' handshape around it." },
"""

fr_signs = """
      "cousin": "Cousin",
      "give": "Donner",
      "room": "Pièce",
      "take": "Prendre",
      "short": "Court",
      "environment": "Environnement",
"""

fr_dict = """
      "cousin": { category: "Famille", complexity: "Moyenne", description: "Secouez la forme de main 'C' sur le côté de la tête." },
      "give": { category: "Action", complexity: "Moyenne", description: "Tenez les mains en 'O' aplaties paumes vers le haut, déplacez-les vers l'avant et vers l'extérieur." },
      "room": { category: "Nom", complexity: "Moyenne", description: "Formez une boîte avec les mains plates, en les déplaçant pour montrer quatre murs." },
      "take": { category: "Action", complexity: "Moyenne", description: "Tendez les mains ouvertes, attrapez un objet imaginaire et tirez-le vers vous." },
      "short": { category: "Description", complexity: "Faible", description: "Tenez la main plate paume vers le bas, abaissez-la pour indiquer une petite taille." },
      "environment": { category: "Nom", complexity: "Élevée", description: "Tenez la main inactive plate, faites tourner la main active en forme de 'E' autour d'elle." },
"""

# Let's find occurrences of "child":
# 1. "child": "Child",
content = content.replace('"child": "Child",', en_signs + '      "child": "Child",')

# 2. "child": { category: "Person", ... }
# Look for child": { category: "Person"
content = re.sub(r'("child": \{ category: "Person".*?\})', en_dict + r'\1', content)

# 3. "child": "Enfant",
content = content.replace('"child": "Enfant",', fr_signs + '      "child": "Enfant",')

# 4. "child": { category: "Personne", ... }
content = re.sub(r'("child": \{ category: "Personne".*?\})', fr_dict + r'\1', content)

with open("c:\\Users\\lenovo\\Desktop\\SignSpeakL\\frontend\\src\\translations.js", "w", encoding="utf-8") as f:
    f.write(content)
print("Injected all correctly.")
