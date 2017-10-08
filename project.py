from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from catalog_db_setup import Base, Author, Categories
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
from sqlalchemy import update
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# show login screen
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
        string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# login using gmail account
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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['email']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['email'])
    print "done!"
    return output

# logout of webapp
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#JSON ENDPOINT
@app.route('/catalog/JSON')
def catalogJSON():
    catalog = session.query(Categories).all()
    return jsonify(catalog=[i.serialize for i in catalog])

# Show all categories
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Categories).group_by(Categories.category).all()
    items = session.query(Categories).all()
    return render_template('categories.html', categories=categories, items=items)

# Show specific selected item
@app.route('/catalog/<string:category>/<string:category_item>')
def showItem(category, category_item):
    cat = session.query(Categories).filter_by(category=category, item=category_item).one()
    if cat:
        item = session.query(Categories).filter_by(category=category, item=category_item).one()
        return render_template('item.html', item=item)
    else:
        return error

# edit class to change database for items
@app.route('/catalog/<string:category>/<string:category_item>/edit/', methods=('GET', 'POST'))
def editCatalogItem(category, category_item):
    editedItem = session.query(Categories).filter_by(category=category, item=category_item).one()
    category = session.query(Categories).filter_by(category=category, item=category_item).one()
    cat = category
    item = category_item
    user = session.query(Author).join(Categories).filter_by(item = editedItem.item).one()
    if 'email' not in login_session:
        return redirect('/login')
    if user.user_name != login_session['email']:
        return "<script>function myFunction() {alert('You are not authorized to edit this item. Please create your own listing in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['item'] and request.form['category'] and request.form['item_url'] and request.form['item_description']:
            editedItem.item = request.form['item']
            editedItem.category = request.form['category']
            editedItem.image = request.form['item_url']
            editedItem.item_description = request.form['item_description']
            flash('Item Successfully Edited %s' % editedItem.item)
        return redirect(url_for('showCatalog'))
    else:
        return render_template('edit_item.html', category=category, category_item=editedItem)

# delete item from catalog
@app.route('/catalog/<string:category>/<string:category_item>/delete/', methods=('GET', 'POST'))
def deleteCatalogItem(category, category_item):
    if 'email' not in login_session:
        return redirect('/login')
    deleteItem = session.query(Categories).filter_by(category=category, item=category_item).one()
    category = session.query(Categories).filter_by(category=category, item=category_item).one()
    user = session.query(Author).join(Categories).filter_by(item = deleteItem.item).one()
    if user.user_name != login_session['email']:
        return "<script>function myFunction() {alert('You are not authorized to delete this item. Please create your own listing in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(deleteItem)
        flash('%s Successfully Deleted' % deleteItem.item)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('delete_item.html', category=category, category_item=deleteItem)

# adding a new item to catalog
@app.route('/catalog/new/', methods=('GET', 'POST'))
def newItem():
    if 'email' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        print request.form['category']
        print request.form['item']
        print request.form['item_description']
        user = ''
        users = session.query(Author).all()
        for i in users:
            print i.user_name
            if i.user_name == login_session['email']:
                user = i
        if user == '':
            newItemuser=Author(name='Michael Ryden', user_name=login_session['email'])
            session.add(newItemuser)
            session.commit()
            user = session.query(Author).filter_by(user_name = login_session['email']).one()
        newItem=Categories(category=request.form['category'], item=request.form['item'],
            item_description=request.form['item_description'], image=request.form['item_url'],
            author_id=user.id)
        session.add(newItem)
        flash('New Item %s Successfully Created' % newItem.item)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newItem.html')

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
