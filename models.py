from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, Column, String, Integer, DateTime, func, Float
from typing import List
from datetime import datetime


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# User → Order (one-to-many).
# Order ↔ Product (many-to-many via a junction table).

order_product = Table(
    "order_product",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)

    # One-to-many
    orders: Mapped[List["Order"]] = relationship(back_populates="user")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # One-to-Many backref
    user: Mapped["User"] = relationship(back_populates="orders")

    # Many-to-many
    products: Mapped[List["Product"]] = relationship(
        secondary=order_product, back_populates="orders"
    )


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float)

    # Many-to-many
    orders: Mapped[List["Order"]] = relationship(
        secondary=order_product, back_populates="products"
    )
