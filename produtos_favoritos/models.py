from datetime import datetime

from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    favorites = relationship(
        "Favorite", back_populates="client", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    image: Mapped[str] = mapped_column(String(500))
    price: Mapped[float] = mapped_column(Float)
    review: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    last_sync: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    favorites = relationship(
        "Favorite", back_populates="product", cascade="all, delete-orphan")


class Favorite(Base):
    __tablename__ = "favorites"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="favorites")
    product = relationship("Product", back_populates="favorites")

    __table_args__ = (UniqueConstraint(
        'client_id', 'product_id', name='uq_client_product'),)
