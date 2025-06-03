from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from api.db.database import Base

class Vote(Base):
    __tablename__ = "votes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    question = Column(String, nullable=False)
    options = Column(String, nullable=False)  # CSV ou JSON simple
    end_date = Column(DateTime(timezone=True), nullable=False)  # <-- Ajout timezone=True
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    responses = relationship("VoteResponse", back_populates="vote")

class VoteResponse(Base):
    __tablename__ = "vote_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    vote_id = Column(UUID(as_uuid=True), ForeignKey("votes.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    selected_option = Column(String)

    vote = relationship("Vote", back_populates="responses")
    user = relationship("User", back_populates="vote_responses")
