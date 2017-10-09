Catalog App
-------------------------
Application used to display, update, delete, and add items to a online clothing store. You must sign in using your google account to either add, update, or delete items. All items are displayed without the need to sign in. 

Getting Started
-------------------------
This application is within the catalog directory and contains these files: catalog_db_setup.py, catalog.db, client_secrets.json, project.py, static/bootstrap.min.css, static/styles.css, templates/categories.html, templates/delete_item.html, templates/edit_item.html, templates/item.html, templates/login.html, templates/newitem.html.

SQLAlchemy ORM was used in python to query the web app database. This module may need to be installed in python before running this app.

Once the catalog directory is downloaded on your computer you can run the project.py file using python and view the web app at ‘http://localhost:5000/‘. 

A sqlite database has been created for this web application called ‘catalog.db’ and contains the following tables:

table - authors
	columns - id, name, user_name

table - categories
	columns - id, category, item, item_description, image, author_id

Once logged in using a gmail account the user will have the ability to add, update and delete items in the database to be displayed in the browser.

A JSON endpoint is located at ‘http://localhost:5000/catalog/JSON’. 

Prerequisites
-------------------------
Python
Web Browser

Authors
-------------------------
Michael Ryden