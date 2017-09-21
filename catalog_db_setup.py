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


# set up categories table for catalog database
class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    category = Column(String(80), nullable=False)
    item = Column(String(80))
    item_description = Column(String(250))
    image = Column(String(10000))
    author_id = Column(Integer, ForeignKey('authors.id'))

    @property
    def serialize(self):
        # Return object data in easily serializeable format
        return {
            'id': self.id,
            'category': self.category,
            'item': self.item,
            'item description': self.item_description
        }

engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)