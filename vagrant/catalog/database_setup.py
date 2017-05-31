from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, func
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


"""
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    picture = Column(Text)
"""


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    # user_id = Column(Integer, ForeignKey('users.id'))
    # user = relationship(Users, cascade="save-update")


class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    cat_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Categories, cascade="all")
    # user_id = Column(Integer, ForeignKey('user.id'))
    # user = relationship(Users, cascade="save-update")


engine = create_engine('postgresql+psycopg2:///catalog')

Base.metadata.create_all(engine)
