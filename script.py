# Start virtual environment for Mac
# python3 -m venv venv
# source venv/bin/activate
# pip install Flask Flask-SQLAlchemy Flask-Marshmallow mysql-connector-python marshmallow-sqlalchemy
# pip freeze > requirements.txt

from __future__ import annotations
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    ForeignKey,
    Table,
    Column,
    String,
    Integer,
    select,
    DateTime,
    func,
    Float,
)
from marshmallow import ValidationError
from typing import List, Optional
from datetime import datetime

# init flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+mysqlconnector://root:Gocolts44@localhost/E_commerce_api"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Create Base class
class Base(DeclarativeBase):
    pass


# Initialize extensions
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

# Create classes

# Junction Table
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
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    address: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)

    # One-to-Many
    orders: Mapped[List["Order"]] = relationship(back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # One-to-Many backref
    user: Mapped["User"] = relationship(back_populates="orders")

    # Many-to-Many
    products: Mapped[List["Product"]] = relationship(
        secondary=order_product, back_populates="orders"
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_name: Mapped[str] = mapped_column(String(30), nullable=False)
    price: Mapped[float] = mapped_column(Float)

    orders: Mapped[List["Order"]] = relationship(
        secondary=order_product, back_populates="products"
    )


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
