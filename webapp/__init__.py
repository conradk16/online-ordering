from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c0a5be14fe3cb64fbfba58ec0a74897c83511fc15f6c267b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

from .views.home import home
from .views.account import account
from .views.order import order
from .views.webhook import webhook
from .models.user import User

db.create_all()
db.session.commit()

app.register_blueprint(home)
app.register_blueprint(account)
app.register_blueprint(order)
app.register_blueprint(webhook)
