from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from api.db.database import get_db
from api.db.models.vote import Vote, VoteResponse
import uuid

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/admin/votes/create")
def create_vote_form(request: Request):
    return templates.TemplateResponse("votes_create.html", {"request": request})

@router.post("/admin/votes/create")
def creer_vote(
        request: Request,
        question: str = Form(...),
        options: str = Form(...),
        end_date: str = Form(...),  # ISO format, UTC (attendu)
        db: Session = Depends(get_db)
):
    # DEBUG: print session infos
    print(f"[DEBUG] user_id: {request.session.get('user_id')}, is_admin: {request.session.get('is_admin')}")
    user_id = request.session.get("user_id")
    is_admin = request.session.get("is_admin")

    if not user_id or not is_admin:
        print("[DEBUG] Accès refusé - pas d'utilisateur ou non admin.")
        return RedirectResponse("/identification", status_code=303)

    print(f"[DEBUG] Reçu question: {question}")
    print(f"[DEBUG] Reçu options: {options}")
    print(f"[DEBUG] Reçu end_date (brut): {end_date}")

    # Try parsing date
    try:
        dt_exp = datetime.fromisoformat(end_date)
        print(f"[DEBUG] Parsed end_date: {dt_exp}, tzinfo: {dt_exp.tzinfo}")
        if dt_exp.tzinfo is None:
            print("[DEBUG] end_date est naïf, ajout UTC.")
            dt_exp = dt_exp.replace(tzinfo=timezone.utc)
        else:
            print("[DEBUG] end_date est aware, converti en UTC.")
            dt_exp = dt_exp.astimezone(timezone.utc)
        print(f"[DEBUG] Final end_date (UTC): {dt_exp}")
    except Exception as e:
        print(f"[ERREUR] Impossible de parser la date: {end_date} - Exception: {e}")
        return templates.TemplateResponse(
            "votes_create.html",
            {"request": request, "error": "Date invalide, veuillez réessayer."}
        )

    now_utc = datetime.now(timezone.utc)
    print(f"[DEBUG] Now (UTC): {now_utc}")

    if dt_exp < now_utc:
        print("[DEBUG] Date dans le passé.")
        return templates.TemplateResponse(
            "votes_create.html",
            {"request": request, "error": "La date d'expiration doit être dans le futur."}
        )

    vote = Vote(
        id=uuid.uuid4(),
        question=question.strip(),
        options=options.strip(),
        end_date=dt_exp,
        created_by=user_id
    )
    db.add(vote)
    db.commit()

    print(f"[DEBUG] Vote créé avec id: {vote.id}, end_date: {vote.end_date}")

    return RedirectResponse("/admin", status_code=303)


@router.post("/votes/{vote_id}")
def enregistrer_vote(
        request: Request,
        vote_id: str,
        option: str = Form(...),
        db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/identification", status_code=303)

    vote = db.query(Vote).filter(Vote.id == vote_id).first()
    if not vote:
        return RedirectResponse(f"/association?message=vote_not_found&voted_id={vote_id}", status_code=303)

    # Check si le vote est terminé (UTC only!)
    now = datetime.now(timezone.utc)
    if vote.end_date.replace(tzinfo=timezone.utc) < now:
        return RedirectResponse(f"/association?message=vote_expired&voted_id={vote_id}", status_code=303)

    existing = db.query(VoteResponse).filter_by(vote_id=vote_id, user_id=user_id).first()
    if existing:
        return RedirectResponse(f"/association?message=already_voted&voted_id={vote_id}", status_code=303)

    reponse = VoteResponse(
        vote_id=vote_id,
        user_id=user_id,
        selected_option=option
    )
    db.add(reponse)
    db.commit()

    return RedirectResponse(f"/association?message=success&voted_id={vote_id}", status_code=303)


@router.post("/admin/update_vote")
def update_vote(
        vote_id: str = Form(...),
        question: str = Form(...),
        options: str = Form(...),
        end_date: str = Form(...),
        db: Session = Depends(get_db)
):
    vote = db.query(Vote).filter(Vote.id == vote_id).first()
    if vote:
        vote.question = question.strip()
        vote.options = options.strip()
        vote.end_date = datetime.fromisoformat(end_date)
        db.commit()

    return RedirectResponse(url="/admin?tab=votes", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/admin/delete_vote")
def delete_vote(vote_id: str = Form(...), db: Session = Depends(get_db)):
    vote = db.query(Vote).filter(Vote.id == vote_id).first()
    if vote:
        db.delete(vote)
        db.commit()
    return RedirectResponse(url="/admin?tab=votes", status_code=status.HTTP_303_SEE_OTHER)

