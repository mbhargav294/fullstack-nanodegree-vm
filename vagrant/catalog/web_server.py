from flask import Flask, render_template, request, jsonify
from flask import redirect, jsonify, url_for, flash, abort
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items, Users
from flask import session as login_session
import random
import string
import datetime
import logging
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"


# Connect to Database and create database session
engine = create_engine('postgresql+psycopg2:///catalog')
Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/', methods=['POST', 'GET'])
def HomePage():
    if(request.method == 'GET'):
        categories = session.query(Categories, Users).join(Users).all()
        items = session.query(Items, Categories).join(Categories)
        items = items.filter(Items.cat_id == Categories.id).order_by(
                desc(Items.timestamp)).limit(10).all()
        if 'username' in login_session:
            return render_template('items.html',
                                   categories=categories,
                                   items=items,
                                   validuser=True,
                                   username=login_session['username'],
                                   userphoto=login_session['picture'])
        else:
            return render_template('items.html',
                                   categories=categories,
                                   items=items,
                                   validuser=False)
    if(request.method == 'POST'):
        search = request.form['search']
        if len(search) == 0:
            return redirect(url_for('HomePage'))
        else:
            likepat = "%%%s%%" % search
            categories = session.query(Categories).filter(
                         Categories.name.like(likepat)).all()
            items = session.query(Items, Categories).join(Categories).filter(
                    Items.cat_id == Categories.id).filter(
                    Items.name.ilike(likepat)).order_by(
                    desc(Items.timestamp)).all()
            return render_template('searchresults.html',
                                   search=search,
                                   categories=categories,
                                   items=items)


@app.route('/login')
def login():
    if(request.method == 'GET'):
        if 'username' in login_session:
            return redirect(url_for('HomePage'))
        state = ''.join(random.choice(
                string.ascii_uppercase + string.digits)
                for x in xrange(32))
        login_session['state'] = state
        return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                   'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one

    user_id = getUserID(data['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += """ " style = "width: 300px;
                    height: 300px;
                    border-radius: 150px;
                    -webkit-border-radius: 150px;
                    -moz-border-radius: 150px;"> """
    flash("You are now logged in as %s" % login_session['username'],
          "success")
    print "done!"
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        return render_template('logout.html')
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    newUser = Users(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(Users).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/newcategory', methods=['POST', 'GET'])
def createNewCategory():
    try:
        if request.method == 'GET':
            if 'username' in login_session:
                return render_template('newcategory.html',
                                       validuser=True,
                                       username=login_session['username'],
                                       userphoto=login_session['picture'])
            else:
                abort(405)
        if request.method == 'POST':
            if 'username' in login_session:
                name = request.form['name']
                err = False
                if len(name) == 0:
                    flash("Category name is required", "danger")
                    err = True
                if len(name) > 30:
                    flash("Length of category name can only be less than 30",
                          "danger")
                    err = True
                if err:
                    return render_template('newcategory.html', nametext=name)
                newCategory = Categories(name=name,
                                         user_id=login_session['user_id'])
                session.add(newCategory)
                session.commit()
                cname = newCategory.name
                flash('Successfully Created a new catalog - %s' % cname,
                      "success")
                return redirect(url_for('showItems',
                                category_id=newCategory.id))
            else:
                abort(405)
    except:
        session.rollback()
        abort(404)


@app.route('/category/<int:category_id>/edit', methods=['POST', 'GET'])
def editCategory(category_id):
    try:
        category = session.query(Categories).filter_by(id=category_id).one()
        if request.method == 'GET':
            if 'username' in login_session:
                if category.user_id != login_session['user_id']:
                    flash("Cannot edit/delete other's catalog!", "danger")
                    return redirect(url_for('HomePage'))

                return render_template('categoryedit.html',
                                       category=category,
                                       validuser=True,
                                       username=login_session['username'],
                                       userphoto=login_session['picture'])
            else:
                abort(405)
        if request.method == 'POST':
            if 'username' in login_session:
                if category.user_id != login_session['user_id']:
                    flash("Cannot edit/delete other's catalog!", "danger")
                    return redirect(url_for('HomePage'))

                name = request.form['name']
                err = False
                if len(name) == 0:
                    flash("Category name is required", "danger")
                    err = True
                if len(name) > 30:
                    flash("Length of category name can only be less than 30",
                          "danger")
                    err = True
                if err:
                    return render_template('categoryedit.html',
                                           category=category,
                                           validuser=True,
                                           username=login_session['username'],
                                           userphoto=login_session['picture'])
                category.name = name
                session.add(category)
                session.commit()
                flash('Successfully Updated catalog - %s' % category.name,
                      "success")
                return redirect(url_for('showItems',
                                        category_id=category.id))
            else:
                abort(405)
    except:
        session.rollback()
        abort(404)


@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/items/')
def showItems(category_id):
    try:
        category = session.query(Categories).filter_by(id=category_id).one()
        categories = session.query(Categories, Users).join(Users).all()
        items = session.query(Items, Categories).filter_by(
                cat_id=category_id).join(Categories).filter(
                Items.cat_id == Categories.id).order_by(
                desc(Items.timestamp)).all()

        if 'username' in login_session:
            return render_template('items.html',
                                   categories=categories,
                                   items=items,
                                   category=category,
                                   validuser=True,
                                   username=login_session['username'],
                                   userphoto=login_session['picture'],
                                   userid=login_session['user_id'])
        else:
            return render_template('items.html',
                                   categories=categories,
                                   items=items,
                                   category=category)
    except:
        abort(404)


@app.route('/category/<int:category_id>/JSON')
@app.route('/category/<int:category_id>/items/JSON')
def wholeCatalogJSON(category_id):
    try:
        category = session.query(Categories).filter_by(id=category_id).one()
        items = session.query(Items).filter_by(
                cat_id=category_id).join(Categories).filter(
                Items.cat_id == Categories.id).order_by(
                desc(Items.timestamp)).all()
        return jsonify(CatalogName=category.name,
                       CatalogItems=[i.serialize for i in items])
    except:
        abort(404)


@app.route('/category/<int:category_id>/item/<int:item_id>')
def showIndividualItem(category_id, item_id):
    try:
        category = session.query(Categories).filter_by(id=category_id).one()
        categories = session.query(Categories, Users).join(Users).all()
        item = session.query(Items).filter_by(
               cat_id=category_id).join(Categories).filter(
               Items.cat_id == Categories.id).filter(Items.id == item_id).one()

        if 'username' in login_session:
            return render_template('iteminfo.html',
                                   item=item,
                                   category=category,
                                   validuser=True,
                                   username=login_session['username'],
                                   userphoto=login_session['picture'],
                                   userid=login_session['user_id'])
        else:
            return render_template('iteminfo.html',
                                   item=item, category=category)
    except:
        abort(404)


@app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
def singleItemJSON(category_id, item_id):
    try:
        category = session.query(Categories).filter_by(id=category_id).one()
        item = session.query(Items).filter_by(
               cat_id=category_id).join(Categories).filter(
               Items.cat_id == Categories.id).filter(Items.id == item_id).one()
        return jsonify(CatalogName=category.name,
                       CatalogItem=item.serialize)
    except:
        abort(404)


@app.route('/category/<int:category_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteIndividualItem(category_id, item_id):
    try:
        category = session.query(Categories).filter_by(id=category_id).one()
        categories = session.query(Categories, Users).join(Users).all()
        item = session.query(Items).filter_by(
               cat_id=category_id).join(Categories).filter(
               Items.cat_id == Categories.id).filter(Items.id == item_id).one()
        if(request.method == 'GET'):
            if 'username' in login_session:
                if category.user_id != login_session['user_id'] and \
                   item.user_id != login_session['user_id']:
                    flash("Cannot edit/delete other's catalog!", "danger")
                    return redirect(url_for('HomePage'))

                return render_template('itemdelete.html',
                                       item=item,
                                       category=category,
                                       validuser=True,
                                       username=login_session['username'],
                                       userphoto=login_session['picture'],
                                       userid=login_session['user_id'])
            else:
                abort(404)
        if(request.method == 'POST'):
            if 'username' in login_session:
                if category.user_id != login_session['user_id']:
                    flash("Cannot edit/delete other's catalog!", "danger")
                    return redirect(url_for('HomePage'))

                session.delete(item)
                session.commit()
                flash("Successfully deleted %s Item" % (item.name), "success")
                return redirect(url_for('showItems', category_id=category_id))
            else:
                abort(404)
    except:
        session.rollback()
        abort(404)


@app.route('/category/<int:category_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editIndividualItem(category_id, item_id):
    try:
        category = session.query(Categories).filter_by(id=category_id).one()
        categories = session.query(Categories, Users).join(Users).all()
        item = session.query(Items).filter_by(
               cat_id=category_id).join(Categories).filter(
               Items.cat_id == Categories.id).filter(Items.id == item_id).one()
        if(request.method == 'GET'):
            if 'username' in login_session:
                if category.user_id != login_session['user_id'] and \
                   item.user_id != login_session['user_id']:
                    flash("Cannot edit/delete other's catalog!", "danger")
                    return redirect(url_for('HomePage'))

                return render_template('itemedit.html',
                                       item=item,
                                       category=category,
                                       validuser=True,
                                       username=login_session['username'],
                                       userphoto=login_session['picture'],
                                       userid=login_session['user_id'])
            else:
                flash("Cannot edit/delete other's catalog!", "danger")
                return redirect(url_for('HomePage'))
        if(request.method == 'POST'):
            if 'username' in login_session:
                if category.user_id != login_session['user_id']:
                    flash("Cannot edit/delete other's catalog!", "danger")
                    return redirect(url_for('HomePage'))

                name = request.form['name']
                description = request.form['description']
                err = False
                if len(name) == 0:
                    flash("Item name is required", "danger")
                    err = True
                if len(name) > 30:
                    flash("Length of item name can only be less than 30",
                          "danger")
                    err = True
                if len(description) == 0:
                    flash("Item description is required", "danger")
                    err = True
                if len(description) > 5000:
                    flash("Item description can only be less than 5000 chars.",
                          "danger")
                    err = True
                if err:
                    return render_template('itemedit.html',
                                           item=item,
                                           category=category,
                                           validuser=True,
                                           username=login_session['username'],
                                           userphoto=login_session['picture'],
                                           userid=login_session['user_id'])
                else:
                    item.name = name
                    item.description = description
                    session.add(item)
                    session.commit()
                    flash("Successfully edited %s Item" % (item.name),
                          "success")
                    return redirect(url_for('showIndividualItem',
                                    category_id=category_id,
                                    item_id=item_id))
            else:
                abort(404)
    except:
        session.rollback()
        abort(404)


@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteItems(category_id):
    try:
        category = session.query(Categories).filter_by(id=category_id).one()
        items = session.query(Items).filter_by(cat_id=category.id).all()
        if(request.method == 'GET'):
            if 'username' in login_session:
                if category.user_id != login_session['user_id']:
                    flash("Cannot edit/delete other's catalog!", "danger")
                    return redirect(url_for('HomePage'))

                return render_template('categorydelete.html',
                                       category=category,
                                       validuser=True,
                                       username=login_session['username'],
                                       userphoto=login_session['picture'],
                                       userid=login_session['user_id'])
        if(request.method == 'POST'):
            if 'username' in login_session:
                if category.user_id != login_session['user_id']:
                    flash("Cannot edit/delete other's catalog!", "danger")
                    return redirect(url_for('HomePage'))

                for item in items:
                    session.delete(item)
                session.delete(category)
                session.commit()
                flash("Successfully deleted %s Category" % (category.name),
                      "success")
                return redirect(url_for('HomePage'))
            else:
                abort(404)
    except:
        session.rollback()
        abort(404)


@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def createNewItem(category_id):
    try:
        category = session.query(Categories).filter_by(id=category_id).one()
        if(request.method == 'GET'):
            if 'username' in login_session:
                if category.user_id != login_session['user_id']:
                    flash("Cannot edit/delete other's catalog!", "danger")
                    return redirect(url_for('HomePage'))

                return render_template('newitem.html',
                                       category=category,
                                       validuser=True,
                                       username=login_session['username'],
                                       userphoto=login_session['picture'],
                                       userid=login_session['user_id'])
            else:
                flash("Cannot edit/delete other's catalog!", "danger")
                return redirect(url_for('HomePage'))
        if request.method == 'POST':
            if 'username' in login_session:
                if category.user_id != login_session['user_id']:
                    flash("Cannot edit/delete other's catalog!", "danger")
                    return redirect(url_for('HomePage'))

                name = request.form['name']
                description = request.form['description']
                err = False
                if len(name) == 0:
                    flash("Item name is required", "danger")
                    err = True
                if len(name) > 30:
                    flash("Length of item name can only be less than 30",
                          "danger")
                    err = True
                if len(description) == 0:
                    flash("Item description is required", "danger")
                    err = True
                if len(description) > 5000:
                    flash("Item description can only be less than 5000 chars.",
                          "danger")
                    err = True
                if err:
                    return render_template('newitem.html',
                                           category=category,
                                           itemname=name,
                                           itemdesc=description,
                                           validuser=True,
                                           username=login_session['username'],
                                           userphoto=login_session['picture'],
                                           userid=login_session['user_id'])
                newItem = Items(name=name,
                                description=description,
                                cat_id=category_id,
                                user_id=login_session['user_id'])
                session.add(newItem)
                session.commit()
                flash('New Item %s Successfully Added to %s Category' %
                      (newItem.name, category.name), "success")
                return redirect(url_for('showItems', category_id=category_id))
            else:
                flash("Cannot edit/delete other's catalog!", "danger")
                return redirect(url_for('HomePage'))
    except:
        session.rollback()
        abort(404)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def format_datetime(value, format='medium'):
    return value.strftime('%b %d, %H:%M')

app.jinja_env.filters['datetime'] = format_datetime


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
