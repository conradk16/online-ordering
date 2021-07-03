from flask import Flask
from .views.home import home
from .views.account import account
from .views.order import order
from .views.webhook import webhook

app = Flask(__name__)
app.register_blueprint(home)
app.register_blueprint(account)
app.register_blueprint(order)
app.register_blueprint(webhook)
