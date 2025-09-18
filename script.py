from flask import Flask
from models import db
from schemas import ma
from routes import all_blueprints  # ⬅️ import all at once

# Start virtual environment for Mac
# python3 -m venv venv
# source venv/bin/activate
# pip install Flask Flask-SQLAlchemy Flask-Marshmallow mysql-connector-python marshmallow-sqlalchemy alembic
# pip freeze > requirements.txt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+mysqlconnector://root:Gocolts44@localhost/E_commerce_api"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
ma.init_app(app)

import click

# flask --app script reset-db


@app.cli.command("reset-db")
def reset_db():
    """Drops and recreates all tables."""
    click.confirm("This will erase the database, continue?", abort=True)
    db.drop_all()
    db.create_all()
    click.echo("Database has been reset ✅")


# Register all blueprints in a loop
for bp in all_blueprints:
    app.register_blueprint(bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
