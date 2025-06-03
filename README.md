# 2425\_IHDCB336\_GROUPE\_01

Projet réalisé dans le cadre du cours **Architecture du Web** – Université de Namur
Groupe 01 — 2024–2025

Homez Gilles  - Crotteux Mathieu - Mayon Raphael




---

## 🧩 Dépendances à installer

1. **Assure-toi d’avoir [Python 3.9+](https://www.python.org/downloads/) et [PostgreSQL](https://www.postgresql.org/download/) installés sur ta machine.**

---


2. **Crée et active un environnement virtuel** à la racine du projet :

   ```bash
   python -m venv venv
   # Windows :
   venv\Scripts\activate
   # Linux/macOS :
   source venv/bin/activate
   ```

3. **Installe toutes les dépendances du projet** à partir du fichier [`requirements.txt`](./requirements.txt) :

   ```bash
   pip install -r requirements.txt
   ```

   > 📦 Assure-toi d’avoir activé ton environnement virtuel avant l'installation.

---

## 🗄️ Base de données PostgreSQL

1. **Installe PostgreSQL et crée un utilisateur** (par défaut, `admin` est utilisé).
2. **Crée la base de données** (nom au choix, par ex. `projet_web`).
3. **Donne les droits sur le schéma `public` à l’utilisateur** :

   ```sql
   GRANT ALL PRIVILEGES ON SCHEMA public TO admin;
   ```

---

## 🔐 Configuration des variables d’environnement

* Un fichier `.env` doit être présent à la racine du projet.
* Un modèle `.env.example` est fourni.
* **Exemple de contenu** :

  ```
  DATABASE_URL=postgresql://admin:motdepasse@localhost:5432/projet_web
  SECRET_KEY=change_me
  ```

> ⚠️ **Ne versionne jamais ton fichier `.env` dans Github !** Utilise `.env.example` comme base à copier.

---

## 🚀 Démarrage du projet

### Sous **Windows**

Lance le serveur avec :

```bash
.\start
```

> Ce script configure le `PYTHONPATH` puis démarre FastAPI avec `uvicorn`.

---

### Sous **Linux/macOS**

Donne les droits d’exécution au script, puis lance-le :

```bash
chmod +x start.sh
./start
```

---

## 🛠️ Migrations de base de données avec Alembic

Alembic gère **toutes les évolutions du schéma** (création ou modification de tables).

* **Créer une migration** :

  ```bash
  alembic revision --autogenerate -m "Ajout table X"
  ```
* **Appliquer les migrations** :

  ```bash
  alembic upgrade head
  ```

> ⚠️ **Ne jamais utiliser** `Base.metadata.create_all(bind=engine)` dans `main.py`, car Alembic gère les tables !

---

## 📁 Structure du projet

```
projet_web/
|   .env
|   .env.example
|   .gitignore
|   alembic.ini
|   README.md
|   start.bat
|   start.sh
|   structure.txt
|   
+---.idea
|       .gitignore
|       misc.xml
|       modules.xml
|       Projet_WEB.iml
|       vcs.xml
|       workspace.xml
|       
+---alembic
|   |   env.py
|   |   README
|   |   script.py.mako
|   |   
|   +---versions
|   |   |   37b33ed47624_initial_schema.py
|   |   |   83855ee7f169_ajout_des_tables.py
|   |   |   
|   |          
|           
+---api
|   |   main.py
|   |   populate_users.py
|   |   security.py
|   |   test.py
|   |   
|   +---db
|   |   |   database.py
|   |   |   
|   |   +---models
|   |   |   |   evenement.py
|   |   |   |   forum.py
|   |   |   |   user.py
|   |   |   |   vote.py
|   |   |   |   __init__.py
|   |   |   |   
|   |   |           
|   |   +---schemas
|   |   |   |   forum.py
|   |   |   |   user.py
|   |   |   |   vote.py
|   |   |   |
|   |   |
|   |           
|   +---endpoints
|   |   |   forum.py
|   |   |   user.py
|   |   |   vote.py
|   |   |
|   |
|           
+---frontend
|   +---static
|   |   |   favicon.ico
|   |   |   
|   |   +---css
|   |   |       style_accueil.css
|   |   |       style_admin.css
|   |   |       style_association.css
|   |   |       style_ecole.css
|   |   |       style_footer.css
|   |   |       style_forum.css
|   |   |       style_header.css
|   |   |       style_identification.css
|   |   |       style_main.css
|   |   |       style_vote.css
|   |   |       
|   |   +---images
|   |   |       33045.jpg
|   |   |       ecole.jpg
|   |   |       urne_valide.png
|   |   |       
|   |   \---js
|   |           admin.js
|   |           autocomplete.js
|   |           countdown.js
|   |           footer_header.js
|   |           forum_accordion.js
|   |           
|   \---templates
|       |   admin.html
|       |   association.html
|       |   base.html
|       |   ecole.html
|       |   forum.html
|       |   forum_edit_post.html
|       |   forum_edit_reply.html
|       |   forum_new_post.html
|       |   forum_post.html
|       |   identification.html
|       |   index.html
|       |   mon_compte.html
|       |   votes_create.html
|       |   
|       \---modules
|               footer.html
|               gestion_evenements.html
|               gestion_utilisateurs.html
|               gestion_votes.html
|               header.html
```

---

## 👥 Équipe

* Homez Gilles  - Crotteux Mathieu - Mayon Raphael
* Université de Namur – Cours Architecture du Web

---
