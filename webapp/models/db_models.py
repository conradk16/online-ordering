from webapp import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

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
    client_secret = db.Column(db.String)
    json_order = db.Column(db.String)
    paid = db.Column(db.Boolean, default=False)
    order_url = db.Column(db.String)

    def __repr__(self):
        return f"Order('{self.json_order}')"

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()
