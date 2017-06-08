import web_server
from database_setup import Base, Items, Categories, Users
from sqlalchemy import create_engine, asc, desc
from flask import flash


def getAllCategories():
    """
    This method will return all the categories details available in the
    database
    """
    return web_server.session.query(Categories, Users).join(Users).all()


def getSingleCategory(category_id):
    """
    This method return the information about single category available in
    the database.
    params:
        category_id - unique identifier of a category
    """
    return web_server.session.query(
           Categories).filter_by(id=category_id).one()


def deleteCategory(category):
    """
    Method to delete a category from database
    params:
        category - A Category class object that is present in the database
    """
    try:
        web_server.session.delete(category)
        web_server.session.commit()
    except:
        web_server.session.rollback()


def addUpdateCategory(category):
    """
    Method to add a new Category object/Update existing
    Category entry in the database
    params:
        category - An Category class object that may/maynot
                   present in the database
    """
    try:
        web_server.session.add(category)
        web_server.session.commit()
    except:
        web_server.session.rollback()


def validateCategoryInfo(name):
    """
    Method to validate the user input for Category name
    params:
        name - Category name entered by the user(String)
    """
    err = False
    if len(name) == 0:
        flash("Category name is required", "danger")
        err = True
    if len(name) > 30:
        flash("Length of category name can only be less than 30",
              "danger")
        err = True
    return err
