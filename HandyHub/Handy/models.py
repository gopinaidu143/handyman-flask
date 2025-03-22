from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    address = db.Column(db.String(500), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    image = db.Column(db.String(255), nullable=True, default='default.png')  # Image field

    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.first_name} {self.last_name}>'


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Service {self.name}>'


class Provider(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    business_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), unique=True, nullable=False)
    service = db.relationship('Service', backref=db.backref('provider', uselist=False))
    service_price = db.Column(db.Float, nullable=True)  # Experience in years
    experience = db.Column(db.Integer, nullable=True)  # Experience in years
    image = db.Column(db.String(255), nullable=True, default='default.png')  # Image field
    location = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.Float, default=0.0)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Provider {self.name}, Service: {self.service.name}>'


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Customer who booked
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=False)  # Provider booked
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)  # Service selected
    
    booking_date = db.Column(db.Date, nullable=False)  # Date of booking
    booking_time = db.Column(db.Time, nullable=False)  # Time of booking
    status = db.Column(db.String(20), default="Pending")  # Status: Pending, Confirmed, Completed, Canceled
    
    feedback = db.Column(db.Text, nullable=True)  # Customer's feedback
    rating = db.Column(db.Float, nullable=True)  # Customer's rating (1-5)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When the booking was made

    # Relationships
    customer = db.relationship('User', backref=db.backref('bookings', lazy=True))
    provider = db.relationship('Provider', backref=db.backref('bookings', lazy=True))
    service = db.relationship('Service', backref=db.backref('bookings', lazy=True))

    def __repr__(self):
        return f"<Booking {self.id} - {self.customer.first_name} booked {self.provider.first_name}>"
