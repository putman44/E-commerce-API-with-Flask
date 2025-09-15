from flask_marshmallow import Marshmallow
from models import User, Order, Product, OrderProduct

ma = Marshmallow()

# load_instance = True
# load_instance=True → “deserialize JSON/data into SQLAlchemy model objects, not dictionaries.”

# It’s mostly for convenience when building APIs, so you can skip the manual model construction.


class OrderProductSchema(ma.SQLAlchemyAutoSchema):
    product = ma.Nested("ProductSchema")

    class Meta:
        model = OrderProduct
        include_relationships = True
        load_instance = True


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True
        include_relationships = True
        load_instance = True

    # include related products
    order_products = ma.Nested(OrderProductSchema, many=True)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True

    orders = ma.Nested(OrderSchema, many=True)


# Schema instances
order_product_schema = OrderProductSchema()
order_products_schema = OrderProductSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
