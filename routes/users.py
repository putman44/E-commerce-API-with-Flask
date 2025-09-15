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

    db.session.add(user_data)
    db.session.commit()
    return user_schema.jsonify(user_data), 201


@users_bp.route("/users", methods=["GET"])
def get_users():
    users = db.session.execute(select(User)).scalars().all()
    return users_schema.jsonify(users), 200


@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "Invalid user id"}), 404
    return user_schema.jsonify(user), 200


@users_bp.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    # 1️⃣ Fetch the existing user
    user = db.session.get(User, id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # 2️⃣ Load the incoming JSON into a User instance
    try:
        # partial=True allows sending only some fields
        user_data = user_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 400

    # 3️⃣ Update only the fields provided
    for field in ["name", "email", "address"]:
        value = getattr(user_data, field, None)
        if value is not None:
            setattr(user, field, value)

    # 4️⃣ Commit changes
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    # 5️⃣ Return the updated user
    return user_schema.jsonify(user), 200


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "Invalid user id"}), 404

    db.session.delete(user)
    db.session.commit()
    return (
        jsonify({"message": f"Successfully deleted user {user.id}: {user.name}"}),
        200,
    )
