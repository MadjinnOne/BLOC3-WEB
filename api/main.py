from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from api.db.models.user import User
from api.db.models.forum import ForumPost
from api.db.database import engine, Base, SessionLocal
from starlette.middleware.sessions import SessionMiddleware
from api.db.models.evenement import Evenement
from datetime import date
from datetime import datetime, timezone
from api.endpoints import vote as vote_routes
from api.db.models.vote import Vote, VoteResponse



import os
import bcrypt

from api.endpoints import forum

today = datetime.today().date()

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="une_cle_secrete_bien_longue")

# Inclus seulement le router forum (plus besoin du router user ici)
app.include_router(forum.router)
app.include_router(vote_routes.router)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ❌ Ne pas utiliser create_all() car Alembic gère les migrations de schéma
# Cette ligne crée directement les tables dans la base, ce qui contourne Alembic
# => à désactiver dans les projets avec gestion des versions via Alembic
# Base.metadata.create_all(bind=engine)


# 🔧 Montre /frontend/static à l'URL /static
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "..", "frontend", "static")),
    name="static"
)

# 📁 Dossier des templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "frontend", "templates"))

@app.get("/ecole", response_class=HTMLResponse)
def ecole(request: Request):
    user_prenom = request.session.get("user_prenom")
    is_admin = request.session.get("is_admin")
    return templates.TemplateResponse("ecole.html", {
        "request": request,
        "user_prenom": user_prenom,
        "is_admin": is_admin
    })


@app.get("/association", response_class=HTMLResponse)
def association(request: Request):
    db = SessionLocal()
    votes = db.query(Vote).order_by(Vote.end_date.desc()).all()
    current_time = datetime.now(timezone.utc)

    votes_info = {}
    for vote in votes:
        options = [opt.strip() for opt in vote.options.split(",")]
        responses = db.query(VoteResponse).filter(VoteResponse.vote_id == vote.id).all()
        result_counts = {opt: 0 for opt in options}
        for r in responses:
            if r.selected_option.strip() in result_counts:
                result_counts[r.selected_option.strip()] += 1
        total = sum(result_counts.values())
        votes_info[vote.id] = {
            "results": result_counts,
            "total": total,
            "options": options
        }

    has_voted = {}
    user_id = request.session.get("user_id")
    for vote in votes:
        if user_id:
            response = db.query(VoteResponse).filter_by(user_id=user_id, vote_id=vote.id).first()
            has_voted[vote.id] = response is not None
        else:
            has_voted[vote.id] = False

    user_prenom = request.session.get("user_prenom")
    is_admin = request.session.get("is_admin")

    # UTC
    votes_en_cours = []
    votes_termines = []
    for vote in votes:
        # Si stocké naïf en DB, forcer .replace(tzinfo=timezone.utc)
        end = vote.end_date
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        if end > current_time:
            votes_en_cours.append(vote)
        else:
            votes_termines.append(vote)

    db.close()

    return templates.TemplateResponse("association.html", {
        "request": request,
        "user_prenom": user_prenom,
        "is_admin": is_admin,
        "votes_en_cours": votes_en_cours,
        "votes_termines": votes_termines,
        "votes_info": votes_info,
        "current_time": current_time,
        "has_voted": has_voted
    })


@app.get("/identification", response_class=HTMLResponse)
def identification(request: Request):
    success = request.query_params.get("success")
    error = request.query_params.get("error")
    user_prenom = request.session.get("user_prenom")
    is_admin = request.session.get("is_admin")
    return templates.TemplateResponse("identification.html", {
        "request": request,
        "success": success,
        "error": error,
        "user_prenom": user_prenom,
        "is_admin": is_admin
    })

@app.get("/forum", response_class=HTMLResponse)
def forum(request: Request):
    db: Session = SessionLocal()
    posts = db.query(ForumPost).order_by(ForumPost.created_at.desc()).all()
    db.close()
    user_prenom = request.session.get("user_prenom")
    is_admin = request.session.get("is_admin")
    return templates.TemplateResponse("forum.html", {
        "request": request,
        "posts": posts,
        "user_prenom": user_prenom,
        "is_admin": is_admin
    })


@app.post("/admin/promote")
def promote_user(request: Request, user_id: str = Form(...)):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.admin = True
        db.commit()
    db.close()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/update_admin")
def update_admin(request: Request, user_id: str = Form(...), admin: str = Form(...)):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.admin = True if admin == "True" else False
        db.commit()
    db.close()
    return RedirectResponse(url="/admin", status_code=303)



@app.post("/admin/delete")
def delete_user(request: Request, user_id: str = Form(...)):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    db.close()
    return RedirectResponse(url="/admin", status_code=303)


@app.get("/favicon.ico")
async def favicon():
    path = os.path.join(BASE_DIR, "..", "frontend", "static", "favicon.ico")
    return FileResponse(path, media_type="image/x-icon")

# --------------------
# ROUTES FORMULAIRES (POST)
# --------------------

@app.post("/forum", response_class=HTMLResponse)
def create_post(request: Request, title: str = Form(...), content: str = Form(...)):
    db: Session = SessionLocal()
    new_post = ForumPost(title=title, content=content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    db.close()
    return RedirectResponse(url="/forum", status_code=303)

@app.post("/register")
def register(
    request: Request,
    prenom: str = Form(...),
    nom: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    fonction: str = Form(...),
    rue_et_numero: str = Form(...),
    code_postal: str = Form(...),
    ville: str = Form(...),
    telephone: str = Form(...)
):
    db: Session = SessionLocal()

    # Vérifie si l'utilisateur existe déjà
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        db.close()
        return RedirectResponse(url="/identification?error=exists", status_code=303)

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    new_user = User(
        first_name=prenom,
        last_name=nom,
        email=email,
        hashed_password=hashed_password,
        fonction=fonction,
        admin=False,
        rue_et_numero=rue_et_numero,
        code_postal=code_postal,
        ville=ville,
        telephone=telephone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    return RedirectResponse(url="/identification?success=1", status_code=303)


@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    db: Session = SessionLocal()

    user = db.query(User).filter(User.email == email).first()

    if not user:
        db.close()
        return RedirectResponse(url="/identification?error=notfound", status_code=303)

    if not bcrypt.checkpw(password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        db.close()
        return RedirectResponse(url="/identification?error=invalid", status_code=303)

    request.session["user_id"] = str(user.id)
    request.session["user_prenom"] = user.first_name
    request.session["is_admin"] = user.admin

    db.close()
    return RedirectResponse(url="/", status_code=303)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

@app.get("/mon-compte", response_class=HTMLResponse)
def mon_compte(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/identification", status_code=303)

    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()

    if not user:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse("mon_compte.html", {
        "request": request,
        "user": user,
        "user_prenom": request.session.get("user_prenom"),
        "is_admin": request.session.get("is_admin")
    })


@app.post("/mon-compte")
def update_mon_compte(
    request: Request,
    prenom: str = Form(...),
    nom: str = Form(...),
    fonction: str = Form(...),
    ville: str = Form(...),
    code_postal: str = Form(...),
    rue_et_numero: str = Form(...),
    telephone: str = Form(...)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/identification", status_code=303)

    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.first_name = prenom
        user.last_name = nom
        user.fonction = fonction
        user.ville = ville
        user.code_postal = code_postal
        user.rue_et_numero = rue_et_numero
        user.telephone = telephone
        db.commit()
        request.session["user_prenom"] = prenom  # mise à jour du prénom dans la session
    db.close()

    return RedirectResponse(url="/mon-compte", status_code=303)


from datetime import datetime, timezone

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request, tab: str = "utilisateurs"):
    db: Session = SessionLocal()

    users = db.query(User).order_by(User.last_name).all()
    evenements_avenir = db.query(Evenement).filter(Evenement.date >= date.today()).order_by(Evenement.date).all()
    evenements_passes = db.query(Evenement).filter(Evenement.date < date.today()).order_by(Evenement.date.desc()).all()

    now = datetime.now(timezone.utc)
    votes_actifs = db.query(Vote).filter(Vote.end_date > now).order_by(Vote.end_date).all()
    votes_termines = db.query(Vote).filter(Vote.end_date <= now).order_by(Vote.end_date.desc()).all()

    db.close()

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "users": users,
        "evenements_avenir": evenements_avenir,
        "evenements_passes": evenements_passes,
        "votes_actifs": votes_actifs,
        "votes_termines": votes_termines,
        "tab": tab,
        "user_prenom": request.session.get("user_prenom"),
        "is_admin": request.session.get("is_admin")
    })



@app.post("/admin/evenement/create")
def create_evenement(request: Request, titre: str = Form(...), date: str = Form(...)):
    db: Session = SessionLocal()
    evenement = Evenement(titre=titre, date=date)
    db.add(evenement)
    db.commit()
    db.close()
    return RedirectResponse(url="/admin?tab=evenements", status_code=303)

@app.post("/admin/evenement/delete")
def delete_evenement(request: Request, evenement_id: str = Form(...)):
    db: Session = SessionLocal()
    evt = db.query(Evenement).filter(Evenement.id == evenement_id).first()
    if evt:
        db.delete(evt)
        db.commit()
    db.close()
    return RedirectResponse(url="/admin?tab=evenements", status_code=303)


@app.post("/admin/evenement/update")
def update_evenement(
    request: Request,
    evenement_id: str = Form(...),
    titre: str = Form(...),
    date: str = Form(...)
):
    db: Session = SessionLocal()
    evt = db.query(Evenement).filter(Evenement.id == evenement_id).first()
    if evt:
        evt.titre = titre
        evt.date = date
        db.commit()
    db.close()
    return RedirectResponse(url="/admin?tab=evenements", status_code=303)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    db: Session = SessionLocal()
    today = datetime.today().date()
    evenements = db.query(Evenement).filter(Evenement.date >= today).order_by(Evenement.date).all()
    db.close()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user_prenom": request.session.get("user_prenom"),
        "is_admin": request.session.get("is_admin"),
        "evenements": evenements
    })

@app.post("/admin/update_user")
def update_user(
    request: Request,
    user_id: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    fonction: str = Form(...),
    rue_et_numero: str = Form(...),
    ville: str = Form(...),
    code_postal: str = Form(...),
    telephone: str = Form(...),
    admin: str = Form(...)
):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.first_name = first_name
        user.last_name = last_name
        user.fonction = fonction
        user.rue_et_numero = rue_et_numero
        user.ville = ville
        user.code_postal = code_postal
        user.telephone = telephone
        user.admin = True if admin == "True" else False
        db.commit()
    db.close()
    return RedirectResponse(url="/admin?section=utilisateurs", status_code=303)


@app.get("/ping")
def ping():
    return {"status": "ok"}


