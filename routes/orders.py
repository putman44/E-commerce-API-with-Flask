from flask import Blueprint, jsonify
from models import db, Order, User, Product, OrderProduct
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
    "/users/<int:user_id>/orders/products/<int:product_id>/quantity/<int:quantity>",
    methods=["POST"],
)
def create_order_with_product(user_id, product_id, quantity):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "Invalid user id"}), 400

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Invalid product id"}), 400

    new_order = Order(user_id=user_id)
    db.session.add(new_order)

    quantity = max(quantity, 1)
    order_product = OrderProduct(order=new_order, product=product, quantity=quantity)
    db.session.add(order_product)

    db.session.commit()

    return order_schema.jsonify(new_order), 201


@orders_bp.route(
    "/orders/<int:order_id>/products/<int:product_id>/quantity/<int:quantity>",
    methods=["PUT"],
)
def add_product_to_order(order_id, product_id, quantity):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)

    if not order:
        return jsonify({"message": "Invalid order id"}), 400
    if not product:
        return jsonify({"message": "Invalid product id"}), 400

    # Safely get existing OrderProduct or None
    order_product = next(
        # (op for op in order.order_products if op.product_id == product_id)
        # is a generator expression.
        # next() returns the first op that matches the condition.
        # If nothing matches, it returns None because of the second argument.
        (op for op in order.order_products if op.product_id == product_id),
        None,
    )

    if order_product:
        # Update quantity
        order_product.quantity = quantity
    else:
        # Create new association
        order_product = OrderProduct(order=order, product=product, quantity=quantity)
        db.session.add(order_product)

    db.session.commit()

    return (
        jsonify(
            {
                "message": f"{quantity} {product.product_name}{'s' if quantity > 1 else ''} are in order id {order.id}."
            }
        ),
        200,
    )


@orders_bp.route("/orders", methods=["GET"])
def get_orders():
    orders = db.session.execute(select(Order)).scalars().all()
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

    order_product = next(
        (op for op in order.order_products if op.product_id == product_id), None
    )

    if not order_product:
        return (
            jsonify(
                {
                    "message": f"Product {product.product_name} is not in order {order.id}"
                }
            ),
            400,
        )

    db.session.delete(order_product)
    db.session.commit()

    return (
        jsonify(
            {"message": f"Product {product.product_name} removed from order {order.id}"}
        ),
        200,
    )


@orders_bp.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = db.session.get(Order, order_id)

    if not order:
        return jsonify({"message": "Order not found"}), 404

    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted order {order.id}"}), 200
