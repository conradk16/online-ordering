from webapp.models.order import *
from webapp import db, env
from webapp.models.db_models import User
import json
import random, string
import os

def assign_order_url_to_demo_account(account_email):
    # DEMO MENU

    if env['uploading_to_AWS']:
        f = open('/var/app/current/webapp/utils/sample_menu.json')
    else:
        f = open('./webapp/utils/sample_menu.json')

    demo_menu = json.load(f)
    f.close()
    order_url = ''.join(random.choices(string.ascii_lowercase, k=10))
    demo_menu["order_url"] = order_url

    user = User.query.filter_by(email_address=account_email).first()
    user.order_url = order_url
    user.restaurant_display_name = "Demo Restaurant"
    user.tax_rate = "0.0875" # demo account has tax rate of 8.75%
    user.json_menu = json.dumps(demo_menu)
    db.session.commit()

def assign_order_url_to_live_account(account_email, order_url, json_menu, restaurant_display_name, tax_rate):
    user = User.query.filter_by(email_address=account_email).first()
    user.order_url = order_url
    user.restaurant_display_name = restaurant_display_name
    user.tax_rate = tax_rate
    user.json_menu = json_menu
    db.session.commit()
