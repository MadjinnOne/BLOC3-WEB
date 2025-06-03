import uuid
from sqlalchemy import Column, String, Date
from sqlalchemy.dialects.postgresql import UUID
from api.db.database import Base

class Evenement(Base):
    __tablename__ = "evenements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titre = Column(String, nullable=False)
    date = Column(Date, nullable=False)
