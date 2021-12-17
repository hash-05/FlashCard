from flask_restful import Resource, Api
from flask_restful import fields, marshal_with, abort
from flask_restful import reqparse
from application.model import *
from application.database import db
from flask import current_app as app
from flask import make_response
from werkzeug.exceptions import HTTPException, InternalServerError
from sqlalchemy import or_, desc
import json
from application.controllers import get_details


# Validation
class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        data = {"error_code": error_code,
                "error_message": error_message}
        self.response = make_response(json.dumps(data), status_code)


class NotFoundError(HTTPException):
    def __init__(self, status_code, error_message):
        self.response = make_response(error_message, status_code)


# USER APIs

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('user_name')
create_user_parser.add_argument('user_fullname')
create_user_parser.add_argument('user_email')
create_user_parser.add_argument('user_password')


class UserAPI(Resource):

    def get(self, user_id):
        u = User.query.filter_by(user_id=user_id).first()
        if u is None:
            raise NotFoundError(status_code=404, error_message='User Not Found')
        elif u is not None:
            user_d = get_details(u_id=user_id, ret=1)
            data = {
                'user_name': u.user_name,
                'user_fullname': u.user_fullname,
                'user_email': u.user_email,
                'user_decks': [{i: user_d[i][0]} for i in user_d]
            }
            return make_response(json.dumps(data), 200)
        else:
            abort(500, message='Internal Server Error')

    def delete(self, user_id):
        pass

    def post(self):
        args = create_user_parser.parse_args()
        user_name = args.get('user_name', None)
        user_email = args.get('user_email', None)
        user_fullname = args.get('user_fullname', None)
        user_password = args.get('user_password', None)

        if user_name is None or user_name == '':
            raise BusinessValidationError(status_code=400, error_code='USER1002', error_message='username is required')
        if user_email is None or user_email == '':
            raise BusinessValidationError(status_code=400, error_code='USER1002',
                                          error_message='user_email is required')
        if user_fullname is None or user_fullname == '':
            raise BusinessValidationError(status_code=400, error_code='USER1002',
                                          error_message='User Fullname is required')
        if user_password is None or user_password == '':
            raise BusinessValidationError(status_code=400, error_code='USER1002',
                                          error_message='user_password is required')

        u = db.session.query(User).filter(or_(User.user_name == user_name, User.user_email == user_email)).first()
        if u is None:
            u1 = User(user_name=user_name, user_fullname=user_fullname,
                      user_email=user_email, user_password=user_password)
            db.session.add(u1)
            db.session.commit()

            return 'Successfully Created', 201
        elif u is not None:
            abort(409, message='User already exists with same username/email')
        else:
            abort(500, message='Internal Server Error')


# DECK APIs

deck_parser = reqparse.RequestParser()
deck_parser.add_argument('d_name')


class DeckAPI(Resource):

    def get(self, user_id, d_id):
        u = User.query.filter_by(user_id=user_id).first()
        d = Deck.query.filter_by(d_id=d_id).first()

        if u is None:
            raise NotFoundError(404, 'User Not Found')
        else:
            user_decks = get_details(u_id=user_id, ret=1)
            if d is None or d_id not in user_decks.keys():
                raise NotFoundError(404, 'Deck not found for given user')
            elif d is not None and d_id in user_decks.keys():
                deck_cards = get_details(d_id=d_id, ret=2)
                data = {
                    'user_id': user_id,
                    'd_id': d_id,
                    'd_name': d.d_name,
                    'd_cards': [[i, deck_cards[i][0], deck_cards[i][1]] for i in deck_cards]
                }
                return make_response(json.dumps(data), 200)
                # return data, 200
            else:
                abort(500, messgae='Internal Server Error')

    def put(self, user_id, d_id):
        args = deck_parser.parse_args()
        d_name = args.get("d_name", None)

        u = User.query.filter_by(user_id=user_id).first()
        d = Deck.query.filter_by(d_id=d_id).first()

        if d_name is None or d_name == '':
            raise BusinessValidationError(status_code=400, error_code='DECK0001', error_message='Deck name is required')
        else:
            if u is None:
                raise NotFoundError(404, 'User Not Found')
            else:
                user_decks = get_details(u_id=user_id, ret=1)
                if d is None or d_id not in user_decks.keys():
                    raise NotFoundError(404, 'Deck not found for given user')
                elif d is not None and d_id in user_decks.keys():
                    user_decks = [i.d_id for i in u.decks]
                    for i in user_decks:
                        d1 = Deck.query.filter_by(d_id=i).first()
                        if d_name == d1.d_name and d.d_id != d1.d_id:
                            raise BusinessValidationError(status_code=400, error_code="DECK002",
                                                          error_message="Deck with same name already exists!")
                    d.d_name = d_name
                    db.session.commit()

                    deck_cards = get_details(d_id=d_id, ret=2)
                    data = {
                        'user_id': user_id,
                        'd_id': d_id,
                        'd_name': d.d_name,
                        'd_cards': [[i, deck_cards[i][0], deck_cards[i][1]] for i in deck_cards]
                    }
                    return make_response(json.dumps(data), 201)
                    # return data, 200
                else:
                    abort(500, messgae='Internal Server Error')

    def delete(self, user_id, d_id):
        u = User.query.filter_by(user_id=user_id).first()
        d = Deck.query.filter_by(d_id=d_id).first()

        if u is None:
            raise NotFoundError(404, 'User Not Found')
        else:
            user_decks = get_details(u_id=user_id, ret=1)
            if d is None or d_id not in user_decks.keys():
                raise NotFoundError(404, 'Deck not found for given user')
            elif d is not None and d_id in user_decks.keys():
                ud = UDecks.query.filter_by(d_id=d_id).first()
                dc = DCards.query.filter_by(d_id=d_id)
                cardids = [i.c_id for i in dc]
                db.session.delete(d)  # Delete deck table entry
                db.session.delete(ud)  # Delete UDecks table entries
                for i in cardids:
                    c = Card.query.filter_by(c_id=i).first()  # Delete all cards related to deck
                    db.session.delete(c)
                db.session.commit()
                return 'Successfully Deleted'
            else:
                abort(500, messgae='Internal Server Error')

    def post(self, user_id):
        args = deck_parser.parse_args()
        d_name = args.get("d_name", None)
        u = User.query.filter_by(user_id=user_id).first()

        if d_name is None or d_name == '':
            raise BusinessValidationError(status_code=400, error_code='DECK0001', error_message='Deck name is required')

        if u is None:
            raise NotFoundError(404, 'User not found')
        elif u is not None:
            user_decks = [i.d_id for i in u.decks]
            for i in user_decks:
                d = Deck.query.filter_by(d_id=i).first()
                if d_name == d.d_name:
                    raise BusinessValidationError(status_code=400, error_code="DECK002",
                                                  error_message="Deck with same name already exists!")
            # Adding to DB
            d1 = Deck(d_name=d_name)  # Deck Entry Created
            db.session.add(d1)
            db.session.commit()

            d = db.session.query(Deck).order_by(desc(Deck.d_id)).first()
            ud = UDecks(d_id=d.d_id, u_id=u.user_id)
            u.decks.append(ud)
            db.session.commit()  # Deck mapped to User

            deck_cards = get_details(d_id=d.d_id, ret=2)
            data = {
                'user_id': user_id,
                'd_id': d.d_id,
                'd_name': d.d_name,
                'd_cards': [[i, deck_cards[i][0], deck_cards[i][1]] for i in deck_cards]
            }
            return make_response(json.dumps(data), 201)
        else:
            abort(500, messgae='Internal Server Error')


# CARD APIs
card_parser = reqparse.RequestParser()
card_parser.add_argument('c_front')
card_parser.add_argument('c_back')


class CardAPI(Resource):

    def get(self, user_id, d_id, c_id):
        u = User.query.filter_by(user_id=user_id).first()
        c = Card.query.filter_by(c_id=c_id).first()
        d = Deck.query.filter_by(d_id=d_id).first()

        if u is None:
            raise NotFoundError(404, 'User not found')
        else:
            user_decks = get_details(u_id=user_id, ret=1)
            if d is None or d_id not in user_decks:
                raise NotFoundError(404, 'Deck not found for the given user')
            else:
                deck_cards = get_details(d_id=d_id, ret=2)
                if c is None or c_id not in deck_cards.keys():
                    raise NotFoundError(404, 'Card not found for the given deck')
                elif c is not None and c_id in deck_cards.keys():
                    data = {'user_id': user_id,
                            'd_id': d_id,
                            'd_name': d.d_name,
                            'c_id': c.c_id,
                            'c_front': c.c_front,
                            'c_back': c.c_back}
                    # return make_response(json.dumps(data), 200)
                    return data, 200
                else:
                    abort(500, message='Internal Server Error')

    def delete(self, user_id, d_id, c_id):
        u = User.query.filter_by(user_id=user_id).first()
        c = Card.query.filter_by(c_id=c_id).first()
        d = Deck.query.filter_by(d_id=d_id).first()

        if u is None:
            raise NotFoundError(404, 'User not found')
        else:
            user_decks = get_details(u_id=user_id, ret=1)
            if d is None or d_id not in user_decks:
                raise NotFoundError(404, 'Deck not found for the given user')
            else:
                deck_cards = get_details(d_id=d_id, ret=2)
                if c is None or c_id not in deck_cards.keys():
                    raise NotFoundError(404, 'Card not found for the given deck')
                elif c is not None and c_id in deck_cards.keys():
                    dc = DCards.query.filter_by(d_id=d_id, c_id=c_id).first()
                    db.session.delete(c)  # Delete card table entry
                    db.session.delete(dc)  # Delete DCards table entry
                    db.session.commit()
                    return 'Successfully Deleted', 200
                else:
                    abort(500, message='Internal Server Error')

    def post(self, user_id, d_id):
        args = card_parser.parse_args()
        c_front = args.get('c_front', None)
        c_back = args.get('c_back', None)

        u = User.query.filter_by(user_id=user_id).first()
        d = Deck.query.filter_by(d_id=d_id).first()

        if c_front is None or c_front == '':
            raise BusinessValidationError(status_code=400, error_code='CARD0001',
                                          error_message='Card front name required')
        if c_back is None or c_back == '':
            raise BusinessValidationError(status_code=400, error_code='CARD0001',
                                          error_message='Card back required')

        if u is None:
            raise NotFoundError(404, 'User Not Found')
        else:
            user_decks = get_details(u_id=user_id, ret=1)
            if d is None or d_id not in user_decks.keys():
                raise NotFoundError(404, 'Deck not found for given user')
            elif d is not None and d_id in user_decks.keys():
                card = [i.c_id for i in d.cards]
                if len(card) == 10:  # Deck can have maximum 10 cards
                    raise BusinessValidationError(status_code=400, error_code='DECK0003',
                                                  error_message='Deck cant have more than 10 cards')

                # Card already there in the selected deck
                for i in card:
                    c = Card.query.filter_by(c_id=i).first()
                    if c.c_front == c_front:
                        raise BusinessValidationError(status_code=400, error_code='CARD0002',
                                                      error_message='Card with same name already exists in deck')
                # Adding to DB
                c = Card(c_front=c_front, c_back=c_back)  # Card Created
                db.session.add(c)
                db.session.commit()

                c = db.session.query(Card).order_by(desc(Card.c_id)).first()
                dc = DCards(d_id=d.d_id, c_id=c.c_id)
                d.cards.append(dc)  # Card mapped to Deck
                db.session.commit()
                data = {'user_id': user_id,
                        'd_id': d_id,
                        'd_name': d.d_name,
                        'c_id': c.c_id,
                        'c_front': c.c_front,
                        'c_back': c.c_back}
                return make_response(json.dumps(data), 201)

    def put(self, user_id, d_id, c_id):
        args = card_parser.parse_args()
        c_front = args.get('c_front', None)
        c_back = args.get('c_back', None)

        u = User.query.filter_by(user_id=user_id).first()
        c = Card.query.filter_by(c_id=c_id).first()
        d = Deck.query.filter_by(d_id=d_id).first()

        if c_front is None or c_front == '':
            raise BusinessValidationError(status_code=400, error_code='CARD0001',
                                          error_message='Card front name required')
        if c_back is None or c_back == '':
            raise BusinessValidationError(status_code=400, error_code='CARD0001',
                                          error_message='Card back required')
        if u is None:
            raise NotFoundError(404, 'User not found')
        else:
            user_decks = get_details(u_id=user_id, ret=1)
            if d is None or d_id not in user_decks:
                raise NotFoundError(404, 'Deck not found for the given user')
            else:
                deck_cards = get_details(d_id=d_id, ret=2)
                if c is None or c_id not in deck_cards.keys():
                    raise NotFoundError(404, 'Card not found for the given deck')
                elif c is not None and c_id in deck_cards.keys():
                    card_decks = get_details(d_id=d_id, ret=2)
                    for i in card_decks.keys():
                        c1 = Card.query.filter_by(c_id=i).first()
                        if c1.c_front == c_front and c1.c_id != c.c_id:
                            raise BusinessValidationError(status_code=400, error_code='CARD0002',
                                                          error_message='Card with same name already exists in deck')
                    c.c_front = c_front
                    c.c_back = c_back
                    db.session.commit()
                    data = {'user_id': user_id,
                            'd_id': d_id,
                            'd_name': d.d_name,
                            'c_id': c.c_id,
                            'c_front': c.c_front,
                            'c_back': c.c_back}
                    return make_response(json.dumps(data), 201)
                else:
                    abort(500, message="Internal Server Error")


# SCORE API
score_fields = {
    'd_id': fields.Integer,
    'd_name': fields.String,
    'd_score': fields.Integer
}


class ScoreAPI(Resource):
    @marshal_with(score_fields)
    def get(self, d_id):
        d = Deck.query.filter_by(d_id=d_id).first()
        if d is None:
            raise NotFoundError(404, error_message='Deck not found')
        elif d is not None:
            return d
        else:
            abort(500, message='Internal Server Error')


# Review API
review_fields = {
    'd_id': fields.Integer,
    'd_name': fields.String,
    'd_review_time': fields.DateTime
}


class ReviewAPI(Resource):
    @marshal_with(review_fields)
    def get(self, d_id):
        d = Deck.query.filter_by(d_id=d_id).first()
        if d is None:
            raise NotFoundError(404, error_message='Deck not found')
        elif d is not None:
            return d
        else:
            abort(500, message='Internal Server Error')


# Rating API
class RatingAPI(Resource):

    def get(self, c_id):
        c = Card.query.filter_by(c_id=c_id).first()
        if c is None:
            raise NotFoundError(404, error_message='Card not found')
        elif c is not None:
            data = {"c_id": c.c_id,
                    "c_front": c.c_front,
                    "c_rating": c.rate.level}

            return data, 200
        else:
            abort(500, message='Internal Server Error')
