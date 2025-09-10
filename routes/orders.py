# routes/orders.py
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from models import db, Order, User
from schemas import order_schema, orders_schema

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/<int:user_id>/orders", methods=["POST"])
def create_order(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "Invalid user id"}), 400

    try:
        # This validates request.json against OrderSchema
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Create new order
    new_order = Order(user_id=user_id)

    # Add to DB
    db.session.add(new_order)
    db.session.commit()

    return (
        jsonify(
            {"message": f"{user.name} has added a new order with id {new_order.id}!"}
        ),
        201,
    )
