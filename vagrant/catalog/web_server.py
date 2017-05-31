from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash, abort
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items
from flask import session as login_session
import random
import string
import datetime


app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('postgresql+psycopg2:///catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/', methods=['POST', 'GET'])
def HomePage():
    if(request.method == 'GET'):
        categories = session.query(Categories).all()
        items = session.query(Items, Categories).join(Categories)
        items = items.filter(Items.cat_id == Categories.id).order_by(desc(Items.timestamp)).limit(10).all()
        return render_template('items.html',
                               categories=categories,
                               items=items)


@app.route('/newcategory', methods=['POST', 'GET'])
def createNewCategory():
    if request.method == 'GET':
        return render_template('newcategory.html')
    if request.method == 'POST':
        newCategory = Categories(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        flash('Successfully Created a new catalog - %s' % newCategory.name)
        return redirect(url_for('HomePage'))


@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/items/')
def showItems(category_id):
    try:
        category = session.query(Categories).filter_by(id=category_id).one()
        categories = session.query(Categories).all()
        items = session.query(Items, Categories).filter_by(
        cat_id=category_id).join(Categories).filter(
        Items.cat_id == Categories.id).order_by(desc(Items.timestamp)).all()

        return render_template('items.html',
                               categories=categories,
                               items=items,
                               category=category)
    except:
        abort(404)


@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def createNewItem(category_id):
    try:
        category = session.query(Categories).filter_by(id=category_id).one()
        if(request.method == 'GET'):
            return render_template('newitem.html', category=category)
        if request.method == 'POST':
            newItem = Items(name=request.form['name'],
                            description=request.form['description'],
                            cat_id=category_id)
            session.add(newItem)
            session.commit()
            flash('New Item %s Successfully Added to %s Category' %
                  (newItem.name, category.name))
            return redirect(url_for('showItems', category_id=category_id))
    except:
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
