from enum import unique
from application.database import db


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_name = db.Column(db.String, unique=True, nullable=False)
    user_fullname = db.Column(db.String, nullable=False)
    user_email = db.Column(db.String, unique=True, nullable=False)
    user_password = db.Column(db.String, nullable=False)
    decks = db.relationship('UDecks', cascade='all,delete', backref='user')


class Card(db.Model):
    __tablename__ = 'card'
    c_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    c_front = db.Column(db.String, nullable=False)
    c_back = db.Column(db.String, nullable=False)
    c_rating = db.Column(db.Integer, db.ForeignKey('rating.r_id'), default=4)
    rate = db.relationship('Rating', backref='card')


class Deck(db.Model):
    __tablename__ = 'deck'
    d_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    d_name = db.Column(db.String, nullable=False)
    d_score = db.Column(db.Integer, default=0)
    d_review_time = db.Column(db.DateTime, default=None)
    cards = db.relationship('DCards', cascade='all,delete', backref='deck')


class UDecks(db.Model):
    __tablename__ = 'udecks'
    ud_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    d_id = db.Column(db.Integer, db.ForeignKey('deck.d_id'), nullable=False)
    u_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)


class DCards(db.Model):
    __tablename__ = 'dcards'
    dc_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    d_id = db.Column(db.Integer, db.ForeignKey('deck.d_id'), nullable=False)
    c_id = db.Column(db.Integer, db.ForeignKey('card.c_id'), nullable=False)


class Rating(db.Model):
    __tablename__ = 'rating'
    r_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    level = db.Column(db.String, unique=True, nullable=False)
    point = db.Column(db.Integer, unique=True, nullable=False)
