import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# set up authors table for catalog database
class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_name = Column(String(250), nullable=False)


# set up catagories table for catalog database
class Catagories(Base):
    __tablename__ = 'catagories'

    id = Column(Integer, primary_key=True)
    catagory = Column(String(80), nullable=False)
    item = Column(String(80))
    item_description = Column(String(250))
    author_id = Column(Integer, ForeignKey('authors.id'))

engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)