from webapp import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    # login info
    email_address = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60))

    # stripe info
    stripe_customer_id = db.Column(db.String)
    stripe_connected_account_id = db.Column(db.String)
    stripe_connected_account_details_submitted = db.Column(db.Boolean, default=False)
    stripe_charges_enabled = db.Column(db.Boolean, default=False)
    active_subscription = db.Column(db.Boolean, nullable=False, default=False)

    # plan details
    paid_for_website = db.Column(db.Boolean, nullable=False, default=False)
    paid_for_hardware = db.Column(db.Boolean, nullable=False, default=False)

    # account status
    currently_accepting_orders = db.Column(db.Boolean, nullable=False, default=False)
    most_recent_time_orders_queried = db.Column(db.DateTime, default=datetime.datetime.min)

    # account details
    account_details = db.Column(db.String)
    closing_times = db.Column(db.String)
    closing_times_timezone = db.Column(db.String)
    next_closing_time = db.Column(db.DateTime, default=datetime.datetime.max)
    shipping_address = db.Column(db.String)

    menu_notes = db.Column(db.String)
    menu_file = db.Column(db.LargeBinary)
    menu_file_filename = db.Column(db.String)

    website_notes = db.Column(db.String)
    website_media = db.Column(db.LargeBinary)
    website_media_filename = db.Column(db.String)
    
    # fields assigned
    order_url = db.Column(db.String)
    website_url = db.Column(db.String)
    tax_rate = db.Column(db.Numeric)
    json_menu = db.Column(db.String)
    restaurant_display_name = db.Column(db.String)

    def serialize(self):
        d = {}
        d['email_address'] = self.email_address

        d['stripe_customer_id'] = self.stripe_customer_id
        d['stripe_connected_account_id'] = self.stripe_connected_account_id
        d['stripe_connected_account_details_submitted'] = self.stripe_connected_account_details_submitted
        d['stripe_charges_enabled'] = self.stripe_charges_enabled
        d['active_subscription'] = self.active_subscription

        d['paid_for_website'] = self.paid_for_website
        d['paid_for_hardware'] = self.paid_for_hardware

        d['account_details'] = self.account_details
        d['shipping_address'] = self.shipping_address
        d['currently_accepting_orders'] = self.currently_accepting_orders

        d['menu_notes'] = self.menu_notes
        d['website_notes'] = self.website_notes

        d['order_url'] = self.order_url
        d['website_url'] = self.website_url

        return d
    
 
    def get_reset_token(self, expires_sec=600):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.email_address}', '{self.password}')"

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # order details
    payment_intent_id = db.Column(db.String)
    order_url = db.Column(db.String)
    json_order = db.Column(db.String)

    paid = db.Column(db.Boolean, default=False)
    refunded = db.Column(db.Boolean, default=False)
    marked_as_complete_by_restaurant = db.Column(db.Boolean, default=False)
 
    customer_name = db.Column(db.String)
    customer_email = db.Column(db.String)
    datetime = db.Column(db.DateTime)

    def serialize(self):
        d = {}
        d['json_order'] = self.json_order
        d['refunded_status'] = self.refunded
        d['marked_as_complete_by_restaurant'] = self.marked_as_complete_by_restaurant
        d['datetime'] = self.datetime
        d['payment_intent_id'] = self.payment_intent_id
        d['customer_name'] = self.customer_name.split()[0][:20] # get first name, 20 characters max
        return d

    def __repr__(self):
        return f"Order('{self.json_order}')"

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()
