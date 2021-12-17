import os
import random
from flask import Flask
from datetime import datetime
from sqlalchemy import or_, desc
from flask import render_template, request, redirect
from flask import current_app as app

from application import loginService, notification
from application.deckService import DeckService
from application.model import *


def get_details(u_id=0, d_id=0, c_id=0, ret=0):
    if ret == 1:
        u = User.query.filter_by(user_id=u_id).first()
        user_decks_ids = [i.d_id for i in u.decks]
        user_decks = {}
        for i in user_decks_ids:
            d = Deck.query.filter_by(d_id=i).first()
            user_decks[d.d_id] = [d.d_name, d.d_score,
                                  d.d_review_time.strftime('%c') if d.d_review_time is not None else '', len(d.cards)]
        return user_decks

    elif ret == 2:
        d = Deck.query.filter_by(d_id=d_id).first()
        deck_cards_ids = [i.c_id for i in d.cards]
        deck_cards = {}
        for i in deck_cards_ids:
            c = Card.query.filter_by(c_id=i).first()
            deck_cards[c.c_id] = [c.c_front, c.c_back, c.c_rating]
        return deck_cards


# LOGIN PAGE
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        un = request.form.get('login_username')
        up = request.form.get('login_password')
        u = User.query.filter_by(user_name=un, user_password=up).first()
        if u:
            loginService.LoginService.SESSION_ID = u.user_id
            return redirect("/dashboard/{}".format(u.user_id))
        else:
            return render_template("Error_page.html", message='''Username or password incorrect \n 
                                                                Please enter correct Credentials ''', back="/")
    return render_template("login_page.html")


# LOGOUT PAGE
@app.route("/logout", methods=["GET"])
def logout():
    loginService.LoginService.SESSION_ID = 0
    return redirect("/")


# SIGN UP PAGE
@app.route("/signup", methods=["GET", "POST"])
def user_signup():
    if request.method == "POST":
        uf = request.form.get('signup_fullname')
        un = request.form.get('signup_username')
        ue = request.form.get('signup_email')
        up = request.form.get('signup_password')

        # If Empty Fields
        if un == '' or ue == '' or up == '':
            return render_template("Error_page.html", message="Can't have empty fields", back="/signup")
        u = db.session.query(User).filter(or_(User.user_name == un, User.user_email == ue)).first()

        # If Username/Email Already Exists
        if u:
            return render_template("Error_page.html", message="Username or Email ID already exists !", back="/signup")

        # Adding new user
        u = User(user_name=un, user_fullname=uf,
                 user_email=ue, user_password=up)
        db.session.add(u)
        db.session.commit()

        return redirect('/')

    return render_template("signup_page.html")


# RESET PASSWORD PAGE
@app.route("/reset_password", methods=["GET", "POST"])
def user_password_reset():
    if request.method == 'POST':
        user_email = request.form.get('signup_email')
        user_password = request.form.get('reset_pass')
        back = request.referrer
        if user_email == '' or user_password == '':
            return render_template('Error_page.html', message='Details Empty', back=back)
        u = User.query.filter_by(user_email=user_email).first()
        if u is None:
            return render_template('Error_page.html', message='User Not found with this email', back=back)
        if u.user_password == user_password:
            return render_template('Error_page.html', message='Cant have same password', back=back)
        else:
            u.user_password = user_password
            db.session.commit()
        return redirect('/')
    return render_template("reset_page.html")


# USER DASHBOARD
@app.route('/dashboard/<int:userId>', methods=["GET", "POST"])
def dashboard(userId):
    if loginService.LoginService().loggedin():
        return redirect('/')
    u1 = User.query.filter_by(user_id=userId).first()
    decks_name = get_details(u_id=userId, ret=1)
    return render_template("user_dashboard.html", u1=u1, decks_name=decks_name,
                           notification=notification.NService().getMessage())


# CREATE DECK
@app.route('/dashboard/<int:userId>/create_deck', methods=["GET", "POST"])
def create_deck(userId):
    if loginService.LoginService().loggedin():
        return redirect('/')

    u1 = User.query.filter_by(user_id=userId).first()

    if request.method == "POST":
        dn = request.form.get('deck_name')
        back = request.referrer
        if dn == '':
            return render_template("Error_page.html", message="Deck Name can't be empty", back=back)

        user_decks = [i.d_id for i in u1.decks]

        for i in user_decks:
            d = Deck.query.filter_by(d_id=i).first()
            if dn == d.d_name:
                return render_template("Error_page.html", message="Deck with same name already exists!", back=back)

        # Adding to DB
        d1 = Deck(d_name=dn)  # Deck Entry Created
        db.session.add(d1)
        db.session.commit()

        d = db.session.query(Deck).order_by(desc(Deck.d_id)).first()
        ud = UDecks(d_id=d.d_id, u_id=u1.user_id)
        u1.decks.append(ud)
        db.session.commit()  # Deck mapped to User
        notification.NService.M_TO_BE_SHOWN.append(notification.NService.M_DECK_CREATED)
        return redirect(f'/dashboard/{u1.user_id}')

    return render_template("create_deck.html", u1=u1)


# ADD CARDS PAGE
@app.route("/dashboard/<int:userId>/add_cards", methods=["GET", "POST"])
def add_card(userId):
    if loginService.LoginService().loggedin():
        return redirect('/')

    u1 = User.query.filter_by(user_id=userId).first()

    decks_name = get_details(u_id=userId, ret=1)

    if request.method == "POST":
        did = request.form.get('deck_id')
        cf = request.form.get('card_front')
        cb = request.form.get('card_back')
        back = request.referrer

        # Empty fields
        if cf == '' or cb == '':
            return render_template("Error_page.html", message="Card Details can't be empty", back=back)
        # Deck not selected
        if did == '-Select-':
            return render_template("Error_page.html", message="Enter a valid deck", back=back)

        d = Deck.query.filter_by(d_id=did).first()
        card = [i.c_id for i in d.cards]

        if len(card) == 10:  # Deck can have maximum 10 cards
            return render_template("Error_page.html", message="Deck can't have more than 10 cards", back=back)

        # Card already there in the selected deck
        for i in card:
            c = Card.query.filter_by(c_id=i).first()
            if c.c_front == cf:
                return render_template("Error_page.html", message="Card already exits!", back=back)

        # Adding to DB
        c = Card(c_front=cf, c_back=cb)  # Card Created
        db.session.add(c)
        db.session.commit()

        c = db.session.query(Card).order_by(desc(Card.c_id)).first()
        dc = DCards(d_id=d.d_id, c_id=c.c_id)
        d.cards.append(dc)  # Card mapped to Deck
        db.session.commit()
        notification.NService.M_TO_BE_SHOWN.append(notification.NService.M_CARD_ADDED)
        return redirect(f'/dashboard/{userId}')

    return render_template("add_card.html", u1=u1, decks_name=decks_name,
                           notification=notification.NService().getMessage())


# EDIT DECKS
@app.route("/dashboard/<int:userId>/edit_deck")
def edit_deck_page(userId):
    if loginService.LoginService().loggedin():
        return redirect('/')

    u1 = User.query.filter_by(user_id=userId).first()

    decks_name = get_details(u_id=userId, ret=1)
    return render_template("edit_deck_page.html", decks_name=decks_name, u1=u1,
                           notification=notification.NService().getMessage())


# EDIT DECK PAGE
@app.route("/dashboard/<int:userId>/edit_deck/<int:deckId>")
def edit_deck(userId, deckId):
    if loginService.LoginService().loggedin():
        return redirect('/')

    d = Deck.query.filter_by(d_id=deckId).first()
    u1 = User.query.filter_by(user_id=userId).first()

    cards_name = get_details(d_id=deckId, ret=2)
    return render_template("edit_deck.html", d=d, cards_name=cards_name, u1=u1,
                           notification=notification.NService().getMessage())


# DELETE CARD
@app.route("/edit_deck/<int:deckId>/delete_card/<int:cardId>")
def delete_card(deckId, cardId):
    if loginService.LoginService().loggedin():
        return redirect('/')

    back = request.referrer
    c = Card.query.filter_by(c_id=cardId).first()
    dc = DCards.query.filter_by(d_id=deckId, c_id=cardId).first()

    db.session.delete(c)  # Delete card table entry
    db.session.delete(dc)  # Delete DCards table entry
    db.session.commit()
    notification.NService.M_TO_BE_SHOWN.append(notification.NService.M_CARD_DELETED)
    return redirect(back)


# RENAME DECK
@app.route("/dashboard/<int:userId>/edit_deck/<int:deckId>/rename_deck", methods=["GET", "POST"])
def rename_deck(userId, deckId):
    if loginService.LoginService().loggedin():
        return redirect('/')

    d = Deck.query.filter_by(d_id=deckId).first()
    u1 = User.query.filter_by(user_id=userId).first()
    if request.method == "POST":
        u1 = User.query.filter_by(user_id=userId).first()
        dn = request.form.get('renamed_deck')
        back = request.referrer
        if dn == '':
            return render_template("Error_page.html", message="Deck Name can't be empty", back=back)

        user_decks = [i.d_id for i in u1.decks]

        for i in user_decks:
            d1 = Deck.query.filter_by(d_id=i).first()
            if dn == d1.d_name and d.d_id != d1.d_id:
                return render_template("Error_page.html", message="Deck with same name already exists!", back=back)

        d.d_name = dn
        db.session.commit()
        notification.NService.M_TO_BE_SHOWN.append(notification.NService.M_DECK_RENAMED)
        return redirect(f'/dashboard/{userId}/edit_deck')

    return render_template("rename_deck.html", d=d, u1=u1, )


# DELETE DECK
@app.route("/dashboard/<int:userId>/edit_deck/<int:deckId>/delete_deck")
def delete_deck(deckId, userId):
    if loginService.LoginService().loggedin():
        return redirect('/')

    d = Deck.query.filter_by(d_id=deckId).first()
    ud = UDecks.query.filter_by(d_id=deckId).first()

    u = DCards.query.filter_by(d_id=deckId)
    cardIds = [i.c_id for i in u]

    db.session.delete(d)  # Delete deck table entry
    db.session.delete(ud)  # Delete UDecks table entries
    for i in cardIds:
        c = Card.query.filter_by(c_id=i).first()  # Delete all cards related to deck
        db.session.delete(c)

    db.session.commit()
    notification.NService.M_TO_BE_SHOWN.append(notification.NService.M_DECK_DELETED)
    return redirect(f'/dashboard/{userId}/edit_deck')


# EDIT CARD
@app.route("/dashboard/<int:userId>/edit_deck/<int:deckId>/edit_card/<int:cardId>", methods=["GET", "POST"])
def edit_card(deckId, cardId, userId):
    if loginService.LoginService().loggedin():
        return redirect('/')

    c = Card.query.filter_by(c_id=cardId).first()
    u1 = User.query.filter_by(user_id=userId).first()

    back = request.referrer

    if request.method == 'POST':
        ucb = request.form.get('updated_card_back')
        ucf = request.form.get('updated_card_front')

        # Empty fields
        if ucb == '' or ucf == '':
            return render_template("Error_page.html", message="Card Details can't be empty", back=back)

        card_decks = get_details(d_id=deckId, ret=2)
        for i in card_decks.keys():
            c1 = Card.query.filter_by(c_id=i).first()
            if c1.c_front == ucf and c1.c_id != c.c_id:  # Condition for same card entry with same c_id
                return render_template('Error_page.html', message="Card already exists with same name", back=back)

        c.c_front = ucf
        c.c_back = ucb
        db.session.commit()
        notification.NService.M_TO_BE_SHOWN.append(notification.NService.M_CARD_EDITED)
        return redirect(f'/dashboard/{userId}/edit_deck/{deckId}')

    return render_template("edit_card.html", c=c, d=deckId, u1=u1)


# REVIEW DECK
@app.route("/dashboard/<int:userId>/review_deck/<int:deckId>/<int:index>", methods=["GET", "POST"])
def review_deck(userId, deckId, index):
    if loginService.LoginService().loggedin():
        return redirect('/')

    u1 = User.query.filter_by(user_id=userId).first()
    d = Deck.query.filter_by(d_id=deckId).first()
    if not ("dashboard" in request.referrer and "review_deck" in request.referrer):
        decks_card = [i.c_id for i in d.cards]
        cards_name = []  # Final List

        # Categories of cards
        unrated_cards, easy_cards, medium_cards, hard_cards = [], [], [], []
        for i in decks_card:
            c = Card.query.filter_by(c_id=i).first()
            if c.c_rating == 1:
                easy_cards.append([c.c_id, c.c_front, c.c_back, c.rate.level])
            elif c.c_rating == 2:
                medium_cards.append([c.c_id, c.c_front, c.c_back, c.rate.level])
            elif c.c_rating == 3:
                hard_cards.append([c.c_id, c.c_front, c.c_back, c.rate.level])
            else:
                unrated_cards.append([c.c_id, c.c_front, c.c_back, c.rate.level])
        random.shuffle(unrated_cards)
        random.shuffle(hard_cards)
        random.shuffle(medium_cards)
        random.shuffle(easy_cards)

        # Sequence in which cards will be displayed
        cards_name = unrated_cards + hard_cards + medium_cards + easy_cards

        DeckService.DATA = cards_name  # Preserving the deck

    if index < len(DeckService.DATA):
        return render_template("review_page.html", cards_name={DeckService.DATA[index][0]: DeckService.DATA[index]},
                               u1=u1, d=d)
    else:
        # Calculating score for the deck
        cards = get_details(d_id=d.d_id, ret=2)
        score = 0
        for i in cards:
            c = Card.query.filter_by(c_id=i).first()
            score += c.rate.point
        d = Deck.query.filter_by(d_id=deckId).first()
        d.d_score = score
        d.d_review_time = datetime.now()
        db.session.commit()

        DeckService.DATA = []  # Emptying the DATA
        return render_template("review_page.html", cards_name={}, u1=u1, d=d)


@app.route("/dashboard/<int:userId>/review_deck/<int:deckId>/rate_card/<int:cardId>/<int:rateId>",
           methods=["GET", "POST"])
def rate_card(userId, deckId, cardId, rateId):
    if loginService.LoginService().loggedin():
        return redirect('/')

    back = request.referrer
    c = Card.query.filter_by(c_id=cardId).first()
    d = Deck.query.filter_by(d_id=deckId).first()

    c.c_rating = rateId
    db.session.commit()
    return redirect(back[:-1] + str((int(back[-1]) + 1)))  # Directed to next card(/index+1)


# RATE CARDS


@app.errorhandler(404)
def page_not_found(e):
    return render_template("Error_page.html", message="404 Page Not Found", back="/")



