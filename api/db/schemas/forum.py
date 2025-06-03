from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

# Pour la création d’un post
class ForumPostCreate(BaseModel):
    title: str
    content: str
    author_id: UUID

# Pour la réponse d’un post
class ForumPostResponse(BaseModel):
    id: UUID
    title: str
    content: str
    author_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

