from pydantic import BaseModel
from datetime import datetime
from typing import List

class VoteCreate(BaseModel):
    question: str
    options: List[str]
    end_date: datetime

class VoteResponseCreate(BaseModel):
    vote_id: str
    selected_option: str
