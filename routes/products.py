# routes/products.py
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from models import db, Order, User, Product
from schemas import product_schema, products_schema

products_bp = Blueprint("products", __name__)


@products_bp.route("/products", methods=["POST"])
def create_product():

    try:
        product_data = product_schema.load(request.json)  # returns Product instance
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 400

    db.session.add(product_data)
    db.session.commit()

    return product_schema.jsonify(product_data), 201


@products_bp.route("/products", methods=["GET"])
def get_products():
    products = db.session.execute(select(Product)).scalars().all()
    return products_schema.jsonify(products), 200


@products_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = db.session.get(Product, product_id)

    if not product:
        return jsonify({"message": "Invalid product id"}), 404
    return product_schema.jsonify(product), 200


@products_bp.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Invalid product id"}), 400

    try:
        # partial=True allows updating only some fields
        product_data = product_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Update only provided fields
    for field in ["product_name", "price"]:
        value = getattr(product_data, field, None)
        if value is not None:
            setattr(product, field, value)

    try:
        db.session.commit()
    except Exception as e:
        # rollback() resets the session to a clean state by:
        # Discarding all pending changes that weren’t committed.
        # Allowing you to continue using the session for other operations.
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return product_schema.jsonify(product), 200


@products_bp.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Invalid product id"}), 400

    db.session.delete(product)
    db.session.commit()
    return (
        jsonify(
            {
                "message": f"successfully deleted product id {product.id}: {product.product_name}"
            }
        ),
        200,
    )
