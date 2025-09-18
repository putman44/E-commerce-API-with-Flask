from flask_marshmallow import Marshmallow
from marshmallow import ValidationError, validates, validates_schema, pre_load
from models import db, User, Order, Product, OrderProduct
import re

ma = Marshmallow()

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
session = db.session


def strip_strings(data):
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = value.strip()
    return data


class OrderProductSchema(ma.SQLAlchemyAutoSchema):
    product_id = ma.Int(required=True, load_only=True)
    quantity = ma.Int(load_default=1)
    product = ma.Nested(
        "ProductSchema", dump_only=True, only=("id", "product_name", "price")
    )

    class Meta:
        model = OrderProduct
        include_relationships = True
        load_instance = True
        exclude = ("order",)

    @validates("quantity")
    def validate_quantity(self, value, **kwargs):
        if value < 1:
            raise ValidationError("Quantity must be at least 1")


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True

    @pre_load
    def strip_input(self, data, **kwargs):
        return strip_strings(data)

    @validates("product_name")
    def validate_product_name(self, value, **kwargs):
        if not value:
            raise ValidationError("Product name cannot be blank")
        if value.isdigit():
            raise ValidationError("Product name cannot be only numbers")
        if len(value) < 2:
            raise ValidationError("Product name must be at least 2 characters long")
        return value

    @validates("price")
    def validate_price(self, value, **kwargs):
        if value is None or value < 0.01:
            raise ValidationError("Price must be at least 0.01")
        return value


class OrderSchema(ma.SQLAlchemyAutoSchema):
    order_products = ma.Nested(OrderProductSchema, many=True, data_key="products")
    user_id = ma.Int(required=True, load_only=True)
    user = ma.Nested(
        "UserSchema", dump_only=True, only=("id", "name", "email", "address")
    )

    class Meta:
        model = Order
        include_fk = True
        include_relationships = True
        load_instance = True

    @validates_schema
    def validate_order_products(self, data, **kwargs):
        products_list = data.get("order_products")
        if not products_list or len(products_list) == 0:
            raise ValidationError(
                {"products": ["Order must have at least one product"]}
            )

        for idx, op in enumerate(products_list):
            product_id = getattr(op, "product_id", None)
            if not product_id or not session.get(Product, product_id):
                raise ValidationError(
                    {
                        f"products.{idx}.product_id": [
                            f"Product id {product_id} does not exist"
                        ]
                    }
                )


class UserSchema(ma.SQLAlchemyAutoSchema):
    orders = ma.Nested(OrderSchema, many=True, exclude=("order_products",))

    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        exclude = ("orders",)

    @pre_load
    def strip_input(self, data, **kwargs):
        return strip_strings(data)

    @validates("name")
    def validate_name(self, value, **kwargs):
        if not value:
            raise ValidationError("Name cannot be blank")
        if len(value) < 2:
            raise ValidationError("Name must be at least 2 characters long")
        return value

    @validates("email")
    def validate_email(self, value, **kwargs):
        if not EMAIL_REGEX.match(value):
            raise ValidationError(
                "Invalid email address, email must be in the format 'example@domain.com'"
            )
        return value

    @validates("address")
    def validate_address(self, value, **kwargs):
        if not value:
            raise ValidationError("Address cannot be blank")
        if len(value) < 5 or len(value) > 100:
            raise ValidationError("Address length must be between 5 and 100 characters")
        pattern = r"^\d+\s+\w+.*"
        if not re.match(pattern, value):
            raise ValidationError("Address should start with a street number and name")
        return value


order_product_schema = OrderProductSchema()
order_products_schema = OrderProductSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)
