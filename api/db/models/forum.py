import uuid
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from api.db.database import Base

class ForumPost(Base):
    __tablename__ = "forum_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    # Facultatif : catégorie du sujet
    category_id = Column(UUID(as_uuid=True), ForeignKey("forum_categories.id"), nullable=True)

    # Relations
    author = relationship("User", back_populates="posts")  # auteur du sujet
    post_replies = relationship("ForumReply", back_populates="post", cascade="all, delete-orphan")  # réponses associées à ce sujet
    category = relationship("ForumCategory", back_populates="posts")  # catégorie à laquelle appartient le sujet

class ForumReply(Base):
    __tablename__ = "forum_replies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    post_id = Column(UUID(as_uuid=True), ForeignKey("forum_posts.id"), nullable=False)

    # Relations
    author = relationship("User", back_populates="post_replies")  # auteur de la réponse
    post = relationship("ForumPost", back_populates="post_replies")  # post auquel la réponse appartient

class ForumCategory(Base):
    __tablename__ = "forum_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(200), nullable=True)

    # Relation
    posts = relationship("ForumPost", back_populates="category")  # sujets appartenant à cette catégorie
