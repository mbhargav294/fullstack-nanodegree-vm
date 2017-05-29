from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()

    return jsonify(Restaurant=restaurant.name,
                   MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    item = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).filter_by(id=menu_id).one()

    return jsonify(Restaurant=restaurant.name,
                   MenuItems=item.serialize)

@app.route('/')
@app.route('/index')
@app.route('/restaurants')
def listRestaurants():
    restaurants = session.query(Restaurant)
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menuitems = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)

    return render_template('menu.html',
                           restaurant=restaurant,
                           menuitems=menuitems)


# Task 1: Create route for newMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/newitem', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'],
                           description = request.form['desc'],
                           price = request.form['price'],
                           restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        flash("Successfully added a new item: %s" % newItem.name)
        return redirect(url_for('restaurantMenu',
                        restaurant_id = restaurant_id))

    else:
        return render_template('newitem.html', restaurant_id=restaurant_id)


# Task 2: Create route for editMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).filter_by(id=menu_id).one()
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['desc']
        item.price = request.form['price']
        session.add(item)
        session.commit()
        flash("Successfully Edited %s" % item.name)
        return redirect(url_for('restaurantMenu',
                        restaurant_id = restaurant_id))

    else:
        return render_template('edititem.html',
                               restaurant_id = restaurant_id, item = item)


# Task 3: Create a route for deleteMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/',
           methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Successfully deleted %s" % item.name)
        return redirect(url_for('restaurantMenu',
                        restaurant_id = restaurant_id))

    else:
        return render_template('deleteitem.html',
                               restaurant_id = restaurant_id, item = item)


if __name__ == '__main__':
    app.secret_key = 'madhu_vyshnavi_<3'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
