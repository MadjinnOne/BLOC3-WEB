import uuid
from sqlalchemy import Column, String, Boolean, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from api.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    fonction = Column(String, nullable=False)
    admin = Column(Boolean, default=False)
    rue_et_numero = Column(String, nullable=True)
    code_postal = Column(String, nullable=True)
    ville = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    date_naissance = Column(Date, nullable=True)
    posts = relationship("ForumPost", back_populates="author")
    post_replies = relationship("ForumReply", back_populates="author")
    vote_responses = relationship("VoteResponse", back_populates="user")

