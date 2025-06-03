from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.db.models.user import User
from api.db.schemas.user import UserCreate, UserOut
from api.security import hash_password


router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.post("/users/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hash_password(user.password),
        admin=user.admin
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users/", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    """
    Récupère tous les utilisateurs de la base.
    """
    return db.query(User).all()



