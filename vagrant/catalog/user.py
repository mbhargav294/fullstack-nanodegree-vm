import web_server
from database_setup import Base, Items, Categories, Users
from sqlalchemy import create_engine, asc, desc
from flask import flash

def createUser(login_session):
    """This method is invoked when the user logs in for the first time"""
    newUser = Users(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    web_server.session.add(newUser)
    web_server.session.commit()
    user = web_server.session.query(Users).filter_by(
           email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Method to retrieve user information based on their id"""
    user = web_server.session.query(Users).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Method to retrieve user id based on their email"""
    try:
        user = web_server.session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None
