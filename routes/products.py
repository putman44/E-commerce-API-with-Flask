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
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Create new product
    new_product = Product(
        product_name=product_data["product_name"], price=product_data["price"]
    )

    # Add to DB
    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product), 201


@products_bp.route("/products", methods=["GET"])
def get_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()
    return products_schema.jsonify(products), 200


@products_bp.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"message": "Invalid product id"}), 400

    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    product.product_name = product_data["product_name"]
    product.price = product_data["price"]
    db.session.commit()
    return product_schema.jsonify(product), 200


@products_bp.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = db.session.get(Product, id)
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
