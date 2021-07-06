from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import stripe

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c0a5be14fe3cb64fbfba58ec0a74897c83511fc15f6c267b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from .views.home import home
from .views.account import account
from .views.order import order
from .views.webhook import webhook
from .models.user import User

db.create_all()
db.session.commit()
if not User.query.filter_by(email_address="kuklinskywork@gmail.com").first():
    admin_user = User(email_address="kuklinskywork@gmail.com", password=bcrypt.generate_password_hash("36e&'&4K`c4mp~#cjZZ.6q@!#3?APZ%*").decode('utf-8'))
    admin_user.add_to_db()
    db.session.commit()

app.register_blueprint(home)
app.register_blueprint(account)
app.register_blueprint(order)
app.register_blueprint(webhook)

stripe.api_key = "sk_test_51J8elwLGQW192ovfZdXa5R8KnXuzvceiy9kCV7wojYHBG3L4Y0H0W4MjpXFTgZhUEw9Qzn1naBr5mR2MXUCnczOo00nsenWbzL"