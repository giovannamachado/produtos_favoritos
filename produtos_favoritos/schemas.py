from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ClientBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class ClientCreate(ClientBase):
    password: str = Field(min_length=6, max_length=128)


class ClientRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class ClientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProductRead(BaseModel):
    id: int
    title: str
    image: str
    price: float
    review: str | None = None

    class Config:
        from_attributes = True


class FavoriteRead(BaseModel):
    product: ProductRead
    created_at: datetime

    class Config:
        from_attributes = True
