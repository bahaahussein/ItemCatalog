from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
from flask import session as login_session
import random, string, json, httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response
from functools import wraps
import requests
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

engine = create_engine('sqlite:///categoryitems.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'username' not in login_session:
			flash('please login first')
			return redirect(url_for('showLogin', next=request.url))
		return f(*args, **kwargs)
	return decorated_function

# Create anti-forgery state token
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
					for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)
	
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

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        print login_session
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.to_json()
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
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    print access_token
    return output
	
@app.route('/gdisconnect')
def gdisconnect():
	access_token = login_session['credentials'].access_token
	if access_token is None:
		print 'Access Token is None'
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	print 'result is '
	print result
	if result['status'] == '200':
		del login_session['credentials'] 
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

@app.route('/')
@app.route('/categories')
def showCategories():
	categories = session.query(Category).all()
	isLoggedIn = 'username' in login_session
	return render_template('categories.html', categories=categories, isLoggedIn=isLoggedIn)

@app.route('/category/<int:category_id>')
def showItems(category_id):
	category = session.query(Category).filter_by(id=category_id).one()
	items = session.query(Item).filter_by(category_id=category_id).all()
	isLoggedIn = 'username' in login_session
	return render_template('items.html', category=category, items=items, isLoggedIn=isLoggedIn)
	
@app.route('/category/<int:category_id>/item/<int:item_id>')
def showDescription(category_id, item_id):
	item = items = session.query(Item).filter_by(id=item_id).one()
	isLoggedIn = 'username' in login_session
	return render_template('description.html', item=item, category_id=category_id, isLoggedIn=isLoggedIn)
	
@app.route('/newItem', methods=['GET', 'POST'])
@login_required
def addItem():
	if request.method == 'POST':
		if request.form['name'] and request.form['description']:
			newItem = Item()
			newItem.name = request.form['name']
			newItem.description = request.form['description']
			newItem.category = session.query(Category).filter_by(id=request.form['category']).one()
			session.add(newItem)
			session.commit()
			flash('new item added!')
			return redirect(url_for('showItems', category_id=request.form['category']))
	else:
		isLoggedIn = 'username' in login_session
		categories = session.query(Category).all()
		return render_template('newItem.html', categories=categories, isLoggedIn=isLoggedIn)
	
@app.route('/category/<int:category_id>/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def editItem(category_id, item_id):
	item = session.query(Item).filter_by(id=item_id).one()
	if request.method == 'POST':
		if request.form['name'] and request.form['description']:
			item.name = request.form['name']
			item.description = request.form['description']
			category = session.query(Category).filter_by(id=request.form['category']).one()
			item.category = category
			session.add(item)
			session.commit()
			flash('item edited!')
			return redirect(url_for('showItems', category_id=request.form['category']))
	else:
		categories = session.query(Category).all()
		isLoggedIn = 'username' in login_session
		return render_template('edit.html', categories=categories, item=item, category_id=category_id, isLoggedIn=isLoggedIn)
	
@app.route('/category/<int:category_id>/item/<int:item_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(category_id, item_id):
	if request.method == 'POST':
		item = session.query(Item).filter_by(id=item_id).one()
		session.delete(item)
		session.commit()
		flash('item deleted!')
		return redirect(url_for('showItems', category_id=category_id))
	else:
		isLoggedIn = 'username' in login_session
		return render_template('delete.html', category_id=category_id, item_id=item_id, isLoggedIn=isLoggedIn)
	
@app.route('/catalog.json')
def catalogJSON():
	output = []
	categories = session.query(Category).all()
	for c in categories:
		items = session.query(Item).filter_by(category_id=c.id).all()
		itemJSON = c.serialize
		itemJSON['items'] = [i.serialize for i in items]
		output.append(itemJSON)
	return jsonify(Category=output)
	
if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)