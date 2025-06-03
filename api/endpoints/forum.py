from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from api.db.schemas.forum import ForumPostCreate, ForumPostResponse
from api.db.models.forum import ForumPost, ForumReply, ForumCategory
from api.db.database import SessionLocal, get_db
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/forum",
    tags=["forum"]
)

templates = Jinja2Templates(directory="frontend/templates")

# ==== ROUTES API REST ====

# GET /forum/posts → liste des posts (API REST)
@router.get("/posts", response_model=List[ForumPostResponse])
def get_all_posts(db: Session = Depends(get_db)):
    posts = db.query(ForumPost).all()
    return posts

# POST /forum/posts → créer un post (API REST)
@router.post("/posts", response_model=ForumPostResponse)
def create_post(post: ForumPostCreate, db: Session = Depends(get_db)):
    new_post = ForumPost(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# PUT /forum/posts/{post_id} → éditer un post (API REST)
@router.put("/posts/{post_id}", response_model=ForumPostResponse)
def update_post(post_id: UUID, updated_post: ForumPostCreate, db: Session = Depends(get_db)):
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.title = updated_post.title
    post.content = updated_post.content
    db.commit()
    db.refresh(post)
    return post

# DELETE /forum/posts/{post_id} → supprimer un post (API REST)
@router.delete("/posts/{post_id}")
def delete_post(post_id: UUID, db: Session = Depends(get_db)):
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"detail": "Post deleted"}

# ==== ROUTES HTML/Jinja2 ====

# GET /forum → page HTML (liste des sujets)
@router.get("", response_class=HTMLResponse)
def list_forum_posts(request: Request, db: Session = Depends(get_db)):
    categories = db.query(ForumCategory).order_by(ForumCategory.name).all()
    posts = db.query(ForumPost).order_by(ForumPost.created_at.desc()).all()
    user_prenom = request.session.get("user_prenom")
    is_admin = request.session.get("is_admin")

    # Regroupement des posts par catégorie
    posts_by_category = {}
    for category in categories:
        posts_by_category[category] = [
            p for p in posts if p.category_id and str(p.category_id) == str(category.id)
        ]
    # Gère les posts sans catégorie
    posts_by_category[None] = [p for p in posts if not p.category_id]


    return templates.TemplateResponse("forum.html", {
        "request": request,
        "categories": categories,
        "posts_by_category": posts_by_category,
        "user_prenom": user_prenom,
        "is_admin": is_admin
    })
@router.get("/nouveau", response_class=HTMLResponse)
def nouveau_post(request: Request, db: Session = Depends(get_db)):
    categories = db.query(ForumCategory).order_by(ForumCategory.name).all()
    user_prenom = request.session.get("user_prenom")
    is_admin = request.session.get("is_admin")
    return templates.TemplateResponse("forum_new_post.html", {
        "request": request,
        "categories": categories,
        "user_prenom": user_prenom,
        "is_admin": is_admin
    })



# GET /forum/{post_id} → détail d’un sujet (HTML)
@router.get("/{post_id}", response_class=HTMLResponse)
def show_post(post_id: str, request: Request, db: Session = Depends(get_db)):
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    replies = db.query(ForumReply).filter(ForumReply.post_id == post_id).order_by(ForumReply.created_at.asc()).all()
    user_prenom = request.session.get("user_prenom")
    is_admin = request.session.get("is_admin")
    return templates.TemplateResponse("forum_post.html", {
        "request": request,
        "post": post,
        "replies": replies,
        "user_prenom": user_prenom,
        "is_admin": is_admin
    })

# POST /forum → création d’un nouveau sujet (form HTML)
@router.post("")
def create_forum_post(
        request: Request,
        title: str = Form(...),
        category_id: str = Form(...),
        content: str = Form(...),
        db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/identification", status_code=303)
    post = ForumPost(
        title=title,
        content=content,
        author_id=user_id,
        category_id=category_id
    )
    db.add(post)
    db.commit()
    return RedirectResponse(url="/forum", status_code=303)



# POST /posts/{post_id}/delete → SUPPRIMER un sujet (form HTML)
@router.post("/posts/{post_id}/delete")
def delete_post_html(
        post_id: str,
        request: Request,
        db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    is_admin = request.session.get("is_admin")
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        return RedirectResponse("/forum?message=notfound", status_code=303)
    if not (is_admin or (user_id == str(post.author_id))):
        return RedirectResponse("/forum?message=forbidden", status_code=303)
    db.delete(post)
    db.commit()
    return RedirectResponse("/forum?message=postdeleted", status_code=303)



# POST /forum/{post_id}/reply → répondre à un sujet (form HTML)
@router.post("/{post_id}/reply")
def reply_to_post(
        post_id: str,
        request: Request,
        content: str = Form(...),
        db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/identification", status_code=303)
    reply = ForumReply(
        content=content,
        author_id=user_id,
        post_id=post_id
    )
    db.add(reply)
    db.commit()
    return RedirectResponse(url=f"/forum/{post_id}", status_code=303)


@router.post("/category/create")
def create_forum_category(
        request: Request,
        name: str = Form(...),
        db: Session = Depends(get_db)
):
    # Vérifie que l'utilisateur est admin
    is_admin = request.session.get("is_admin")
    if not is_admin:
        return RedirectResponse("/forum", status_code=303)
    exists = db.query(ForumCategory).filter(ForumCategory.name == name).first()
    if exists:
        return RedirectResponse("/forum?message=exists", status_code=303)
    category = ForumCategory(name=name)
    db.add(category)
    db.commit()
    return RedirectResponse("/forum", status_code=303)

@router.post("/category/delete")
def delete_category(
        request: Request,
        category_id: str = Form(...),
        db: Session = Depends(get_db)
):
    is_admin = request.session.get("is_admin")
    if not is_admin:
        return RedirectResponse("/forum", status_code=303)
    category = db.query(ForumCategory).filter(ForumCategory.id == category_id).first()
    if not category:
        return RedirectResponse("/forum?message=notfound", status_code=303)
    # (optionnel) Empêche la suppression si la catégorie a encore des posts
    posts_in_category = db.query(ForumPost).filter(ForumPost.category_id == category_id).count()
    if posts_in_category > 0:
        return RedirectResponse("/forum?message=notempty", status_code=303)
    db.delete(category)
    db.commit()
    return RedirectResponse("/forum?message=deleted", status_code=303)

#GET -- Édition d’un sujet principal (ForumPost)
@router.get("/posts/{post_id}/edit", response_class=HTMLResponse)
def edit_post_form(post_id: str, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    is_admin = request.session.get("is_admin")
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    categories = db.query(ForumCategory).all()
    if not post:
        return RedirectResponse("/forum?message=notfound", status_code=303)
    if not (is_admin or user_id == str(post.author_id)):
        return RedirectResponse(f"/forum/{post_id}?message=forbidden", status_code=303)
    user_prenom = request.session.get("user_prenom")
    return templates.TemplateResponse("forum_edit_post.html", {
        "request": request,
        "post": post,
        "categories": categories,
        "is_admin": is_admin,
        "user_id": user_id,
        "user_prenom": user_prenom,
    })

#POST - enregistre les modifications d'Édition d’un sujet principal
@router.post("/posts/{post_id}/edit")
def edit_post_submit(
        post_id: str,
        request: Request,
        title: str = Form(...),
        category_id: str = Form(...),
        content: str = Form(...),
        db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    is_admin = request.session.get("is_admin")
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        return RedirectResponse("/forum?message=notfound", status_code=303)
    if not (is_admin or user_id == str(post.author_id)):
        return RedirectResponse(f"/forum/{post_id}?message=forbidden", status_code=303)
    post.title = title
    post.category_id = category_id
    post.content = content
    db.commit()
    return RedirectResponse(f"/forum/{post_id}?message=edited", status_code=303)


#GET -- Édition d’une réponse (ForumReply)
@router.get("/reply/{reply_id}/edit", response_class=HTMLResponse)
def edit_reply_form(reply_id: str, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    is_admin = request.session.get("is_admin")
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
    if not reply:
        return RedirectResponse("/forum?message=notfound", status_code=303)
    if not (is_admin or user_id == str(reply.author_id)):
        return RedirectResponse(f"/forum/{reply.post_id}?message=forbidden", status_code=303)
    user_prenom = request.session.get("user_prenom")
    return templates.TemplateResponse("forum_edit_reply.html", {
        "request": request,
        "reply": reply,
        "is_admin": is_admin,
        "user_id": user_id,
        "user_prenom": user_prenom,
    })

#POST -- Édition d’une réponse  ENREGISTRER
@router.post("/reply/{reply_id}/edit")
def edit_reply_submit(
        reply_id: str,
        request: Request,
        content: str = Form(...),
        db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    is_admin = request.session.get("is_admin")
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
    if not reply:
        return RedirectResponse("/forum?message=notfound", status_code=303)
    if not (is_admin or user_id == str(reply.author_id)):
        return RedirectResponse(f"/forum/{reply.post_id}?message=forbidden", status_code=303)
    reply.content = content
    db.commit()
    return RedirectResponse(f"/forum/{reply.post_id}?message=replyedited", status_code=303)


#POST -- Suppression d’une réponse (ForumReply)
@router.post("/reply/{reply_id}/delete")
def delete_reply(
        reply_id: str,
        request: Request,
        db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    is_admin = request.session.get("is_admin")
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
    if not reply:
        return RedirectResponse("/forum?message=notfound", status_code=303)
    if not (is_admin or user_id == str(reply.author_id)):
        return RedirectResponse(f"/forum/{reply.post_id}?message=forbidden", status_code=303)
    post_id = reply.post_id
    db.delete(reply)
    db.commit()
    return RedirectResponse(f"/forum/{post_id}?message=replydeleted", status_code=303)
