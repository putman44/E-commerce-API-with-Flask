from flask import Flask
from models import db, Base
from schemas import ma
from routes import all_blueprints  # ⬅️ import all at once

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+mysqlconnector://root:Gocolts44@localhost/E_commerce_api"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
ma.init_app(app)

# Register all blueprints in a loop
for bp in all_blueprints:
    app.register_blueprint(bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
