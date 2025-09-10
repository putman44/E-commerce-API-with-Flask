from flask import Blueprint

# Import each module’s blueprint
from .users import users_bp
from .orders import orders_bp
from .products import products_bp

# Collect them in a list (easy to expand later)
all_blueprints = [
    users_bp,
    orders_bp,
    products_bp
]
