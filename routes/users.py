# routes/users.py
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from models import db, User
from schemas import user_schema, users_schema

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["POST"])
def create_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_user = User(
        name=user_data["name"], address=user_data["address"], email=user_data["email"]
    )
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 201


@users_bp.route("/users", methods=["GET"])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()
    return users_schema.jsonify(users), 200


@users_bp.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({"message": "Invalid user id"}), 404

    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    user.name = user_data["name"]
    user.email = user_data["email"]
    db.session.commit()
    return user_schema.jsonify(user), 200


@users_bp.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({"message": "Invalid user id"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted user {user.name}"}), 200
