from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserCreate(BaseModel):
    first_name: str
    last_name:str
    email: EmailStr
    password: str
    admin: bool = False

class UserOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    admin: bool = False

    class Config:
        from_attributes = True

#class UserUpdate(BaseModel):
    #TO DO 

#class UserDelete(BaseModel):
    #//TO DO

#class UserLogin(BaseModel):
    #//TO DO