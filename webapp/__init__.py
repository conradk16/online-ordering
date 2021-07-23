from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import stripe
import os

# PROD is None if environment variable not set. AWS environment value set to "true", so PROD will be True in AWS
PROD = os.getenv('PROD')
env = {}

# SET TRUE IF WANT TO USE DEV ENVIRONMENT WHILE DEPLOYED TO AWS
use_test_webhook_with_live_m3_url = True 
if use_test_webhook_with_live_m3_url:
    PROD = False
    env['stripe_webhook_account_signing_secret'] = 'whsec_aPIY1jxaG09Vy0UMfK0mVIDr5utNrUwU'
    env['stripe_webhook_connect_signing_secret'] = 'whsec_ou3eKzCLgsvLSM8CuYgirpXhatVsArlE'

if PROD:
    env['PROD'] = True
    env['stripe_secret_api_key'] = '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'
    env['stripe_publishable_api_key'] = 'pk_live_51J8elwLGQW192ovfb5ol6DcMIPKCqfF4WfXK292mR6tAxxFrDb66BTOHlf1qnBlCsrVGUedmcxDK2CBVY0oVP4zk003L136f2S'
    env['stripe_webhook_account_signing_secret'] = 'whsec_5fk3ps0nQqpEHiSRFIVTXMfunysdzOTg'
    env['stripe_webhook_connect_signing_secret'] = 'whsec_w90BqL9nSa8at3kwalBAmi7UUEa37WPt'

    env['stripe_hardware_product_price_id'] = 'price_1JFrYYLGQW192ovfqc3fdxV9'
    env['stripe_website_setup_product_price_id'] = 'price_1JG9U0LGQW192ovfwlmQmLSM'
    env['stripe_monthly_with_website_price_id'] = 'price_1JG9WaLGQW192ovfb3orKoLz'
    env['stripe_monthly_without_website_price_id'] = 'price_1JG9VULGQW192ovfVgZpHGIv'
    env['stripe_yearly_with_website_price_id'] = 'price_1JG9k8LGQW192ovfETjV1N4X'
    env['stripe_yearly_without_website_price_id'] = 'price_1JG9Y6LGQW192ovf9wEO8yby'
 
else:
    env['PROD'] = False
    env['stripe_secret_api_key'] = 'sk_test_51J8elwLGQW192ovfZdXa5R8KnXuzvceiy9kCV7wojYHBG3L4Y0H0W4MjpXFTgZhUEw9Qzn1naBr5mR2MXUCnczOo00nsenWbzL'
    env['stripe_publishable_api_key'] = 'pk_test_51J8elwLGQW192ovfOXJfdSNVRLnM2WeeTF0Mk1KaInlzDqvlXk8Em97iK5Xj3zvCGwhfDL7HQqk3Ur5MPdvUKSh5008yyI3tSj'
    env['stripe_webhook_account_signing_secret'] = 'whsec_XDeJeqt7NpBy9HfWB5qmd4iO9dCrtmap'
    env['stripe_webhook_connect_signing_secret'] = 'whsec_eKndjsZQ3ShaeMdqo5wp13gziZLI7as5'

    env['stripe_hardware_product_price_id'] = 'price_1JG9IzLGQW192ovfYtOVi098'
    env['stripe_website_setup_product_price_id'] = 'price_1JG9KKLGQW192ovfU9F9R2Id'
    env['stripe_monthly_with_website_price_id'] = 'price_1JG9MELGQW192ovf6LIOW1py'
    env['stripe_monthly_without_website_price_id'] = 'price_1JG9V9LGQW192ovfr3mdX0sX'
    env['stripe_yearly_with_website_price_id'] = 'price_1JG9jrLGQW192ovf9uACPHcm'
    env['stripe_yearly_without_website_price_id'] = 'price_1JG9Y1LGQW192ovfzqADppTZ'

    env['DEV_charges_enabled_status'] = False # set charges_enabled to be false for connected accounts

stripe.api_version = '2020-08-27'
stripe.api_key = env['stripe_secret_api_key']
env['admin_username'] = 'kuklinskywork@gmail.com'
env['admin_password'] = "36e&'&4K`c4mp~#cjZZ.6q@!#3?APZ%*"
env['stripe_account_link_refresh_url'] = 'https://m3orders.com/account/setup-stripe'
env['stripe_account_link_return_url'] = 'https://m3orders.com/account'
env['stripe_billing_portal_return_url'] = 'https://m3orders.com/account'
env['stripe_checkout_session_success_url'] = 'https://m3orders.com/account/setup-account-details'
env['stripe_checkout_session_cancel_url'] = 'https://m3orders.com/signup/select-setup-fee'
env['email_sender_address'] = 'no-reply@m3orders.com'
env['email_sender_password'] = 'YB\'S!#4GqUZPsP"6'
env['accepting_orders_autoshutoff_threshold_in_seconds'] = 300 # stop accepting orders if 300 seconds go by with no queries to view orders page

    
app = Flask(__name__)
app.config['SECRET_KEY'] = 'c0a5be14fe3cb64fbfba58ec0a74897c83511fc15f6c267b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['MAIL_SERVER'] = 'smtppro.zoho.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = env['email_sender_address']
app.config['MAIL_PASSWORD'] = env['email_sender_password']
mail = Mail(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from .views.home import home
from .views.account import account
from .views.order import order
from .views.webhook import webhook
from .models.db_models import User, Order

db.create_all()
db.session.commit()

if not User.query.filter_by(email_address="kuklinskywork@gmail.com").first():
    admin_user = User(email_address=env['admin_username'], password=bcrypt.generate_password_hash(env['admin_password']).decode('utf-8'))
    admin_user.add_to_db()
    db.session.commit()

app.register_blueprint(home)
app.register_blueprint(account)
app.register_blueprint(order)
app.register_blueprint(webhook)

# run webapp.static.menus.py to create the menus and add them to the database
import webapp.static.menus
