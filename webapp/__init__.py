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

# SET TRUE IF UPLOADING TO test.m3orders.com (OnlineOrdering-Test)
uploading_to_test_env = False 
if uploading_to_test_env:
    env['uploading_to_AWS'] = True
    PROD = False
else:
    env['uploading_to_AWS'] = False

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
    env['stripe_yearly_with_website_price_id'] = 'price_1JHXzCLGQW192ovfxBn11KLn'
    env['stripe_yearly_without_website_price_id'] = 'price_1JHXxrLGQW192ovfVNFKCAad'

    env['stripe_account_link_refresh_url'] = 'https://m3orders.com/account/setup-stripe'
    env['stripe_account_link_return_url'] = 'https://m3orders.com/account'
    env['stripe_billing_portal_return_url'] = 'https://m3orders.com/account'
    env['stripe_checkout_session_success_url'] = 'https://m3orders.com/account/setup-account-details'
    env['stripe_checkout_session_cancel_url'] = 'https://m3orders.com/signup/select-setup-fee'
 
else:
    env['PROD'] = False
    env['stripe_secret_api_key'] = 'sk_test_51J8elwLGQW192ovfZdXa5R8KnXuzvceiy9kCV7wojYHBG3L4Y0H0W4MjpXFTgZhUEw9Qzn1naBr5mR2MXUCnczOo00nsenWbzL'
    env['stripe_publishable_api_key'] = 'pk_test_51J8elwLGQW192ovfOXJfdSNVRLnM2WeeTF0Mk1KaInlzDqvlXk8Em97iK5Xj3zvCGwhfDL7HQqk3Ur5MPdvUKSh5008yyI3tSj'
    env['stripe_webhook_account_signing_secret'] = 'whsec_676LYWw0BdfpPuddk3D85Pkp5IrezG9q'
    env['stripe_webhook_connect_signing_secret'] = 'whsec_bd5x6nD0fCoMlP9mm4EjUh8gjDuQcZax'

    env['stripe_hardware_product_price_id'] = 'price_1JGuEZLGQW192ovfvJ2Qdd0A'
    env['stripe_website_setup_product_price_id'] = 'price_1JGuEFLGQW192ovf5eA7COHk'
    env['stripe_monthly_with_website_price_id'] = 'price_1JGuDBLGQW192ovfLa5MkHvv'
    env['stripe_monthly_without_website_price_id'] = 'price_1JGuDmLGQW192ovf1keSpNrm'
    env['stripe_yearly_with_website_price_id'] = 'price_1JHXtfLGQW192ovf0TNYsZaL'
    env['stripe_yearly_without_website_price_id'] = 'price_1JHXqVLGQW192ovfi7ls2PeY'

    env['DEV_charges_enabled_status'] = True # set charges_enabled for connected accounts

    env['stripe_account_link_refresh_url'] = 'https://test.m3orders.com/account/setup-stripe'
    env['stripe_account_link_return_url'] = 'https://test.m3orders.com/account'
    env['stripe_billing_portal_return_url'] = 'https://test.m3orders.com/account'
    env['stripe_checkout_session_success_url'] = 'https://test.m3orders.com/account/setup-account-details'
    env['stripe_checkout_session_cancel_url'] = 'https://test.m3orders.com/signup/select-setup-fee'

if uploading_to_test_env:
    env['stripe_webhook_account_signing_secret'] = 'whsec_TNx0YjO2nwm6082XvjLXv9HLfS06LQgy'
    env['stripe_webhook_connect_signing_secret'] = 'whsec_Pjy6LIPe2iMbQCmcLvcqQZWym4IvN5w6'

stripe.api_version = '2020-08-27'
stripe.api_key = env['stripe_secret_api_key']
env['admin_username'] = 'kuklinskywork@gmail.com'
env['admin_password'] = "36e&'&4K`c4mp~#cjZZ.6q@!#3?APZ%*"
env['email_sender_address'] = 'no-reply@m3orders.com'
env['email_sender_password'] = 'YB\'S!#4GqUZPsP"6'
env['accepting_orders_autoshutoff_threshold_in_seconds'] = 300 # stop accepting orders if 300 seconds go by with no queries to view orders page
env['archived_orders_display_limit'] = 100 # Don't show more than 100 orders in the archived tab

    
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

if not env['PROD']:
    for user in User.query.all():
        user.stripe_charges_enabled = env['DEV_charges_enabled_status']
    db.session.commit()
