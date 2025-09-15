from flask import Blueprint, request, jsonify
from models import db, Order, User, Product
from schemas import order_schema, orders_schema
from sqlalchemy import select

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/users/<int:user_id>/orders", methods=["POST"])
def create_order_empty(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "Invalid user id"}), 400

    new_order = Order(user_id=user_id)
    db.session.add(new_order)
    db.session.commit()

    return order_schema.jsonify(new_order), 201


@orders_bp.route(
    "/users/<int:user_id>/orders/products/<int:product_id>", methods=["POST"]
)
def create_order(user_id, product_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "Invalid user id"}), 400

    new_order = Order(user_id=user_id)

    product = db.session.get(Product, product_id)
    if product:
        new_order.products.append(product)

    db.session.add(new_order)
    db.session.commit()

    return order_schema.jsonify(new_order), 201


@orders_bp.route("/orders/<int:order_id>/products/<int:product_id>", methods=["PUT"])
def add_product_to_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)

    if not order:
        return jsonify({"message": "Invalid order id"}), 400
    if not product:
        return jsonify({"message": "Invalid product id"}), 400

    if product not in order.products:
        order.products.append(product)

    db.session.commit()

    return (
        jsonify({"message": f"{product.product_name} added to order id {order.id}!"}),
        200,
    )


@orders_bp.route("/orders", methods=["GET"])
def get_orders():
    query = select(Order)
    orders = db.session.execute(query).scalars().all()
    return orders_schema.jsonify(orders), 200


@orders_bp.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "Invalid order id"}), 400
    return order_schema.jsonify(order), 200


@orders_bp.route("/orders/<int:order_id>/products/<int:product_id>", methods=["DELETE"])
def delete_product_from_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)

    if not order:
        return jsonify({"message": "Invalid order id"}), 400
    if not product:
        return jsonify({"message": "Invalid product id"}), 400

    if product in order.products:
        order.products.remove(product)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": f"Product {product.product_name} removed from order {order.id}"
                }
            ),
            200,
        )
    else:
        return (
            jsonify(
                {
                    "message": f"Product {product.product_name} is not in order {order.id}"
                }
            ),
            400,
        )


@orders_bp.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = db.session.get(Order, order_id)

    if not order:
        return jsonify({"message": "Order not found"}), 404

    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted order {order.id}"}), 200
