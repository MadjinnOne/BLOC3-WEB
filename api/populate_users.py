import bcrypt
import uuid
from db.database import SessionLocal
from db.models.user import User
import random

prenoms = ["Marie", "Lucas", "Claire", "Hugo", "Emma", "Noah", "Léa", "Thomas", "Julie", "Antoine",
           "Sophie", "Nicolas", "Chloé", "Paul", "Camille", "Alexandre", "Laura", "Maxime", "Manon", "Julien"]

noms = ["Durand", "Martin", "Lemoine", "Petit", "Moreau", "Fabre", "Robert", "Lopez", "Masson", "Garcia",
        "Bernard", "Dubois", "Fontaine", "Giraud", "Leroux", "Perrot", "Renard", "Schmitt", "Vidal", "Zeller"]

rues = ["Rue des Écoles", "Avenue du Parc", "Chemin Vert", "Place de l'Église", "Rue de la Gare"]

villes = [
    ("Avernas-le-Bauduin", "4280"),
    ("Moxhe", "4280"),
    ("Villers-le-Peuplier", "4280"),
    ("Trognée", "4280"),
    ("Abolens", "4280"),
    ("Cras-Avernas", "4280"),
    ("Poucet", "4280"),
    ("Fallais", "4260"),
    ("Fumal", "4260"),
    ("Ville-en-Hesbaye", "4260"),
    ("Avennes", "4260"),
    ("Ciplet", "4260"),
    ("Hosdent", "4260"),
]

fonctions_possibles = ["maman", "papa", "prof", "directeur", "PO"]

db = SessionLocal()

for i in range(20):
    prenom = prenoms[i]
    nom = noms[i]
    email = f"{prenom.lower()}.{nom.lower()}@test.com"
    fonction = random.choice(fonctions_possibles)
    admin = fonction in ["directeur", "PO", "prof"]

    rue = random.choice(rues)
    numero = random.randint(1, 200)
    ville, code_postal = random.choice(villes)
    telephone = f"04{random.randint(10000000, 99999999)}"

    hashed_password = bcrypt.hashpw("test1234".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    existing = db.query(User).filter(User.email == email).first()
    if not existing:
        user = User(
            id=uuid.uuid4(),
            first_name=prenom,
            last_name=nom,
            email=email,
            hashed_password=hashed_password,
            fonction=fonction,
            admin=admin,
            rue_et_numero=f"{rue} {numero}",
            ville=ville,
            code_postal=code_postal,
            telephone=telephone
        )
        db.add(user)

db.commit()
db.close()
print("✅ 20 utilisateurs fictifs créés avec adresse locale et téléphone")
