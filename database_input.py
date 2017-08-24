from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_db_setup import Author, Base, Categories

engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

category1 = Categories(category="Shirts", item="Express White shirt",
    item_description="3 way stretch, very stylish", author_id="1")

session.add(category1)
session.commit()

category2 = Categories(category="Pants", item="Express Gray slim",
    item_description="3 way stretch, very stylish", author_id="1")

session.add(category2)
session.commit()

category3 = Categories(category="Accessories", item="Belt",
    item_description="leather belt", author_id="1")

session.add(category3)
session.commit()

author1 = Author(name="Michael Ryden", user_id="mr935h")

session.add(author1)
session.commit()

session.close