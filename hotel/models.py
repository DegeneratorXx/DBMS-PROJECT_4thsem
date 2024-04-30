from hotel import db, login_manager
from hotel import bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    bookings = db.relationship('booking', backref='user', lazy=True)

    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]}$'
        else:
            return f"{self.budget}$"

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_purchase(self, item_obj):
        return self.budget >= item_obj.price

    def can_sell(self, item_obj):
        return item_obj in self.items  # If you want to keep this method, make sure it's updated to work without the 'items' relationship.

class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=False, unique=True)
    bookings = db.relationship('booking', backref='item', lazy=True)

    def __repr__(self):
        return f'Item {self.name}'

class booking(db.Model):
    no = db.Column(db.Integer(), primary_key=True)
    owner_id = db.Column(db.String(), db.ForeignKey('user.username'))
    number_of_people = db.Column(db.Integer())
    total_cost = db.Column(db.Integer())
    type_of_hotel = db.Column(db.String(), db.ForeignKey('item.name'))

    owner = db.relationship('User', back_populates='bookings')
    hotel = db.relationship('Item', back_populates='bookings')

    def make_booking(self, user, item_obj):
        self.owner = user
        self.hotel = item_obj
        self.total_cost = self.number_of_people * item_obj.price
        db.session.commit()

    def cancel_booking(self):
        db.session.delete(self)
        db.session.commit()


