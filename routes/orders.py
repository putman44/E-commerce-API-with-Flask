from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from models import db, Order, User, Product, OrderProduct
from schemas import OrderProductSchema, OrderSchema, order_schema, orders_schema
from sqlalchemy import select

orders_bp = Blueprint("orders", __name__)


# @orders_bp.route("/users/<int:user_id>/orders", methods=["POST"])
# def create_order_empty(user_id):
#     user = db.session.get(User, user_id)
#     if not user:
#         return jsonify({"message": "Invalid user id"}), 400

#     new_order = Order(user_id=user_id)
#     db.session.add(new_order)
#     db.session.commit()

#     return order_schema.jsonify(new_order), 201


@orders_bp.route("/users/<int:user_id>/orders", methods=["POST"])
def create_order_with_product(user_id):
    """
    Create a new order for a user with products.
    Expected JSON:
    {
        "products": [
            {"product_id": 5, "quantity": 2},
            {"product_id": 7, "quantity": 1}
        ]
    }
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "Invalid user id"}), 400

    # Validate and deserialize incoming data
    try:
        order_data = OrderSchema().load({"user_id": user_id, **request.json})
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Create new Order instance
    new_order = Order(user=user)
    db.session.add(new_order)

    # Attach OrderProducts to the new order
    for op in order_data.order_products:
        product = db.session.get(Product, op.product_id)
        if not product:
            return (
                jsonify({"message": f"Product id {op.product_id} does not exist"}),
                400,
            )

        op.order = new_order  # link each OrderProduct to the new order
        db.session.add(op)

    db.session.commit()

    # Return the new order with nested products, stripped values, and user info
    return order_schema.jsonify(new_order), 201


@orders_bp.route("/orders/<int:order_id>/products", methods=["PUT"])
def add_product_to_order(order_id):
    """
    Adds or updates a product in an order.
    Expected JSON:
    {
        "product_id": 5,
        "quantity": 2
    }
    """
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "Invalid order id"}), 400

    try:
        # Validate and deserialize input
        data = OrderProductSchema().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    product = db.session.get(Product, data.product_id)
    if not product:
        return jsonify({"message": f"Product id {data.product_id} does not exist"}), 400

    # Check if the product already exists in the order
    order_product = next(
        (op for op in order.order_products if op.product_id == data.product_id), None
    )

    if order_product:
        # Update quantity
        order_product.quantity = data.quantity
    else:
        # Create new OrderProduct
        order_product = OrderProduct(
            order=order, product=product, quantity=data.quantity
        )
        db.session.add(order_product)

    db.session.commit()

    return (
        jsonify(
            {
                "message": f"{order_product.quantity} {product.product_name}{'s' if order_product.quantity > 1 else ''} were added to order id {order.id}."
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


@orders_bp.route("/orders/<int:order_id>/products", methods=["DELETE"])
def delete_product_from_order(order_id):
    """
    Deletes a product from an order.
    Expected JSON:
    {
        "product_id": 5
    }
    """
    order = db.session.get(Order, order_id)

    if not order:
        return jsonify({"message": "Invalid order id"}), 400

    try:
        data = OrderProductSchema().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    order_product = next(
        (op for op in order.order_products if op.product_id == data.product_id), None
    )

    if not order_product:
        return (
            jsonify(
                {"message": f"Product id {data.product_id} is not in order {order.id}"}
            ),
            400,
        )

    db.session.delete(order_product)
    db.session.commit()

    # Return the updated order with nested products and user
    return order_schema.jsonify(order), 200


@orders_bp.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = db.session.get(Order, order_id)

    if not order:
        return jsonify({"message": "Order not found"}), 404

    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted order {order.id}"}), 200
