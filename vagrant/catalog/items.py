import web_server
from database_setup import Base, Items, Categories, Users
from sqlalchemy import create_engine, asc, desc
from flask import flash


def getAllItems(category_id):
    """
    Method to get all the items in the given category
    params:
        category_id - ID of a category to return items
    """
    return web_server.session.query(Items, Categories).filter_by(
           cat_id=category_id).join(Categories).filter(
           Items.cat_id == Categories.id).order_by(
           desc(Items.timestamp)).all()


def getSerialItems(category_id):
    """
    Method to get all items in a particular category in serializeable form
    params:
        category_id - Id of the category to return items
    """
    return web_server.session.query(Items).filter_by(
           cat_id=category_id).join(Categories).filter(
           Items.cat_id == Categories.id).order_by(
           desc(Items.timestamp)).all()


def getSerialItem(category_id, item_id):
    """
    Method to get a particular item in a particular category
    in serializeable form
    params:
        category_id - Id of the category to return items
    """
    return web_server.session.query(Items).filter_by(
           cat_id=category_id).join(Categories).filter(
           Items.cat_id == Categories.id).filter(Items.id == item_id).one()


def getSingleItem(category_id, item_id):
    """
    Provided the category_id and item_id, this method will return
    a single item
    params:
        category_id - Unique identifier of a category
        item_id - Unique identifier of an item in given category
    """
    return web_server.session.query(Items).filter_by(
           cat_id=category_id).join(Categories).filter(
           Items.cat_id == Categories.id).filter(Items.id == item_id).one()


def deleteItem(item):
    """
    Method to delete an item from database
    params:
        item - An Item class object that is present in the database
    """
    try:
        web_server.session.delete(item)
        web_server.session.commit()
    except:
        flash("Failed", "danger")
        web_server.session.rollback()


def addUpdateItem(item):
    """
    Method to add a new item object/Update existing Item entry in the database
    params:
        item - An Item class object that may/maynot present in the database
    """
    try:
        web_server.session.add(item)
        web_server.session.commit()
    except:
        web_server.session.rollback()


def validateItemInfo(name, description):
    """
    Method to validate the inputs entered by the user
    params:
        name - Name of the item(String)
        description - Description of the item(String)
    """
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
    return err
