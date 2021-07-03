from webapp import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60))

    def __repr__(self):
        return f"User('{self.email_address}', '{self.password}')"

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()
