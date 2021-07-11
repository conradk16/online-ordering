from webapp import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60))
    stripe_customer_id = db.Column(db.String)
    stripe_connected_account_id = db.Column(db.String)
    stripe_charges_enabled = db.Column(db.Boolean, default=False)
    stripe_connected_account_details_submitted = db.Column(db.Boolean, default=False)
    active_subscription = db.Column(db.Boolean, nullable=False, default=False)
    order_url = db.Column(db.String)

    def __repr__(self):
        return f"User('{self.email_address}', '{self.password}')"

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()
