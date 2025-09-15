# E-Commerce API with Flask

A RESTful API for managing users, orders, and products built with Flask, SQLAlchemy, and MySQL.

---

## Table of Contents

1. [Features](#features)  
2. [Tech Stack](#tech-stack)  
3. [Installation](#installation)  
4. [Configuration](#configuration)  
5. [Database Models](#database-models)  
6. [API Endpoints](#api-endpoints)  
7. [Example Requests & Responses](#example-requests--responses)  
8. [Migrations](#migrations)  
9. [Running the App](#running-the-app)  
10. [Contributing](#contributing)  
11. [License](#license)  

---

## Features

- CRUD operations for users, products, and orders.  
- Add products to orders with configurable quantity.  
- One-to-many relationships (User → Order).  
- Many-to-many relationships with extra data (Order ↔ Product via OrderProduct).  
- Marshmallow schemas for serialization and validation.  
- Alembic migrations for database schema updates.  

---

## Tech Stack

- **Backend:** Python, Flask  
- **Database:** MySQL  
- **ORM:** SQLAlchemy  
- **Serialization:** Flask-Marshmallow, Marshmallow-SQLAlchemy  
- **Migrations:** Alembic  

---

## Installation

```bash
git clone https://github.com/putman44/e-commerce-api-with-flask.git
cd e-commerce-api-with-flask

python3 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

pip install Flask Flask-SQLAlchemy Flask-Marshmallow mysql-connector-python marshmallow-sqlalchemy alembic

### Users
POST   /users                    - Create a user
GET    /users                    - List all users
GET    /users/<id>               - Get a user
PUT    /users/<id>               - Update a user
DELETE /users/<id>               - Delete a user

### Products
POST   /products                 - Create a product
GET    /products                 - List all products
GET    /products/<id>            - Get a product
PUT    /products/<id>            - Update a product
DELETE /products/<id>            - Delete a product

### Orders
POST   /users/<user_id>/orders                                           - Create empty order
POST   /users/<user_id>/orders/products/<product_id>/quantity/<quantity> - Create order with product
PUT    /orders/<order_id>/products/<product_id>/quantity/<quantity>     - Add/update product quantity in order
GET    /orders                                                            - List all orders
GET    /orders/<order_id>                                                - Get order details
DELETE /orders/<order_id>                                                - Delete an order
DELETE /orders/<order_id>/products/<product_id>                          - Remove product from order

alembic init migrations
# Update alembic.ini with SQLAlchemy URL
# Set target_metadata in env.py
alembic revision --autogenerate -m "Add quantity column"
alembic upgrade head
