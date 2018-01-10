#!/usr/bin/env python

"""
Module "controllers" Flask webserver.
Runs nk-catalog App on a webserver and offers API services
"""
from flask import Flask, render_template, request, abort, g
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from app_config import db_path, client_secrets_path
from model_catalog import Base, Category, Item, User, secret_key, engine
from flask import session as login_session
from flask_httpauth import HTTPBasicAuth
from forms import SignupForm
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response
import requests
import random
import string
import httplib2
import json

CLIENT_ID = json.loads( open(client_secrets_path, 'r').read())['web']['client_id']
APPLICATION_NAME = "nk-catalog"

auth = HTTPBasicAuth()

app = Flask(__name__)

# Create database session ( engine is created in model_catalog )
DBSession = sessionmaker(bind=engine)
session = DBSession()

####################################################
# APIs for user signup and login
# verify_password call back function for login procedure


@auth.verify_password
def verify_password(username, password):
    if 'username' in login_session:
        user = session.query(User).filter_by(
            username=login_session['username']).first()
        g.user = user
        return True
    else:
        user = session.query(User).filter_by(username=username).first()
        if not user or not user.verify_password(password):
            return False
        g.user = user
        return True

####################################################
# APIs to create a new user data in JSON format
# /users? {'username':'', 'password':''}


@app.route('/users', methods=['POST'])
@auth.login_required
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        print "missing arguments"
        abort(400)
    if session.query(User).filter_by(username=username).first() is not None:
        print "existing user"
        user = session.query(User).filter_by(username=username).first()
        return jsonify({'message': 'user already exists'})
    newUser = User(
        username=username,
        email='',
        picture='',
        provider='local')
    newUser.hash_password(password)
    session.add(newUser)
    session.commit()
    return jsonify({'username': newUser.username})


@app.route('/api/users/<int:id>')
@auth.login_required
def get_user(id):
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    g.user = user
    return jsonify(
        {'id': g.user.id},
        {'username': g.user.username},
        {'email': g.user.email})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify(
        {'id': g.user.id},
        {'username': g.user.username},
        {'email': g.user.email})


####################################################
# Functions for user signup procedures


def createUser(login_session):
    newUser = User(
        username=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'],
        provider=login_session['provider'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    login_session['user_id'] = user.id
    return user


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(username):
    try:
        user = session.query(User).filter_by(username=username).one()
        return user.id
    except:
        return None

####################################################

# set login_session with g.user data


def set_login_session():
    login_session['username'] = g.user.username
    login_session['picture'] = g.user.picture
    login_session['email'] = g.user.email
    login_session['provider'] = g.user.provider
    login_session['user_id'] = g.user.id

####################################################

# get login user for CRUD control


def get_loginUser():
    if 'username' in login_session:
        loginUser = User(
            username=login_session['username'],
            id=login_session['user_id'],
            picture=login_session['picture'])
    else:
        loginUser = None
    return loginUser

####################################################
# Login endpoint
# /login


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    form = SignupForm()
    return render_template('login.html', STATE=state, form=form)

####################################################
# Logout endpoint
# /logout


@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'local':
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            flash("you are now successfully logged out")
            return redirect('/')
        else:
            return redirect('/gdisconnect')
    else:
        return redirect('/')

####################################################
# Google connect endpoint
# /gconnect


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
        oauth_flow = flow_from_clientsecrets(client_secrets_path, scope='')
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
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
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
    login_session['provider'] = 'google'

    # See if a user exists, if it doesn't make a new one
    login_session['user_id'] = getUserID(login_session['username'])
    if not login_session['user_id']:
        createUser(login_session)

    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']
    output += '!</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += """
' " style = "width: 300px; height: 300px;border-radius: 150px;
-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
"""
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

####################################################
# Google disconnect endpoint
# /gdisconnect


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    urlSource = 'https://accounts.google.com/o/oauth2/revoke?token=%s'
    url = urlSource % login_session['access_token']
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
        del login_session['user_id']
        response = make_response(
            json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("you are now successfully logged out")
        return redirect('/catalog')
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

####################################################
# Signup endpoint
# /signup


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    username = form.username.data
    if request.method == 'GET':
        return render_template('signup.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            if session.query(User).filter_by(username=username).first():
                flash("""
User with username %s already exists
""" % form.username.data)
                return redirect('/')
            else:
                newUser = User(
                    username=form.username.data,
                    email='',
                    provider='local',
                    picture='')
                newUser.hash_password(form.password.data)
                session.add(newUser)
                session.commit()
                flash('User "%s" successfully created' % username)
                login_session['username'] = newUser.username
                login_session['picture'] = newUser.picture
                login_session['email'] = newUser.email
                login_session['user_id'] = newUser.id
                login_session['provider'] = newUser.provider
                return redirect('/catalog')
        else:
            flash("Form didn't validate")
            return redirect('/')

####################################################
# Login with local user account endpoint
# /loginLocal


@app.route('/loginLocal', methods=['GET', 'POST'])
def loginLocal():
    form = SignupForm()
    if request.method == 'GET':
        return render_template('loginLocal.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user = session.query(User).filter_by(
                username=form.username.data).first()
            if user:
                if user.verify_password(form.password.data):
                    login_session['username'] = user.username
                    login_session['picture'] = user.picture
                    login_session['email'] = user.email
                    login_session['user_id'] = user.id
                    login_session['provider'] = 'local'
                    flash("You are now logged in as %s" % user.username)
                    return redirect('/catalog')
                else:
                    flash("Wrong password")
            else:
                flash("User doesn't exist")
        else:
            flash("Form didn't validate")
    return redirect('/')


####################################################

# API to read all categories in JSON format and
# to create a new Category
# GET /api/categories
# POST /api/categories?name=name


@app.route('/api/categories', methods=['GET', 'POST'])
@auth.login_required
def api_categories():
    set_login_session()
    categories = session.query(Category).all()
    if request.method == 'GET':
        return jsonify(Category=[r.serialize for r in categories])
    elif request.method == 'POST':
        # CREATE A NEW CATEGORY
        name = request.args.get('name', '')
        user_id = login_session['user_id']
        if name != '':
            newCategory = Category(name=name, user_id=user_id)
            session.add(newCategory)
            session.commit()
            return jsonify(Category=newCategory.serialize)
    abort(400)


# API to read  a specific category in JSON format and
# to update, delete  a  Category
# GET /api/category/<int:id>
# DELETE /api/category/<int:id>
# PUT /api/category/11?name=Triathlon


@app.route('/api/category/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def api_category(id):
    set_login_session()
    category = session.query(Category).filter_by(id=id).one()
    if not category:
        abort(400)
    # GET http://localhost:8000/api/category/11
    if request.method == 'GET':
        return jsonify(Category=category.serialize)
    if login_session['user_id'] != category.user_id:
        return jsonify(message="non authorized")
    if request.method == 'DELETE':
        # DELETE http://localhost:8000/api/category/11
        session.delete(category)
        session.commit()
        return jsonify(message="Category Deleted")
    elif request.method == 'PUT':
        # PUT http://localhost:8000/api/category/11?name=Triathlon
        name = request.args.get('name')
        if not name:
            abort(400)
        else:
            category.name = name
            session.add(category)
            session.commit()
            return jsonify(Category=category.serialize)

# API to read all items for a specific category in JSON format and
# to create a new Item
# GET /api/category/<int:id>/items
# POST /api/category/<int:id>/items?title=title&description=description


@app.route('/api/category/<int:id>/items', methods=['GET', 'POST'])
@auth.login_required
def api_category_items(id):
    set_login_session()
    category = session.query(Category).filter_by(id=id).one()
    if not category:
        abort(400)
    items = session.query(Item).filter_by(category_id=id).all()
    if request.method == 'GET':
        return jsonify(Items=[r.serialize for r in items])
    elif request.method == 'POST':
        # CREATE A NEW ITEM
        title = request.args.get('title', '')
        description = request.args.get('description', '')
        if not title:
            abort(400)
        else:
            newItem = Item(
                title=title,
                description=description,
                category=category,
                user_id=login_session['user_id'])
            session.add(newItem)
            session.commit()
            return jsonify(Item=newItem.serialize)
    abort(400)

# API to read  a specific item in JSON format and
# to update, delete  a  item
# GET //api/category/<int:id>/items/<int:item_id>
# DELETE /api/category/<int:id>/items/<int:item_id>
# PUT /api/category/<int:id>/items/<int:item_id>
# ?title=title&description=description


app_route_category_item = '/api/category/<int:id>/items/<int:item_id>'


@app.route(app_route_category_item, methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def api_category_item(id, item_id):
    set_login_session()
    category = session.query(Category).filter_by(id=id).one()
    if not category:
        abort(400)
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'GET':
        return jsonify(Item=editedItem.serialize)
    if login_session['user_id'] != editedItem.user_id:
        return jsonify(message="non authorized")
    if request.method == 'DELETE':
        # DELETE http://localhost:8000/api/category/11/items/1
        if not editedItem:
            abort(400)
        else:
            session.delete(editedItem)
            session.commit()
            return jsonify(message="Item Deleted")
    elif request.method == 'PUT':
        # PUT http://localhost:8000/api/category/11/items/1
        # ?title=Ceket&description=Iyi+bak
        title = request.args.get('title')
        description = request.args.get('description')
        if not title:
            abort(400)
        else:
            editedItem.title = title
            editedItem.description = description
            session.add(editedItem)
            session.commit()
            return jsonify(Item=editedItem.serialize)
    abort(400)

# APPLICATION CRUD Methods WITH HTML templates
# Show all Categories
# / or
# /catalog/


@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).order_by(Category.id.desc())
    loginUser = get_loginUser()
    return render_template(
        'catalog.html',
        categories=categories,
        loginUser=loginUser)

# APPLICATION CRUD Methods
# Create a new category
# /category/new/


@app.route('/category/new/', methods=['GET', 'POST'])
@auth.login_required
def newCategory():
    loginUser = get_loginUser()
    if request.method == 'POST':
        name = request.form['name']
        if name:
            newCategory = Category(
                name=name,
                user_id=login_session['user_id'])
            session.add(newCategory)
            flash(
                'New Category "%s" successfully created'
                % newCategory.name)
            session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'newCategory.html',
            loginUser=loginUser)

# APPLICATION CRUD Methods
# Show categoroy items
# /category/<int:category_id>/
# /category/<int:category_id>/items/


@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/items/')
@auth.login_required
def showItems(category_id):
    loginUser = get_loginUser()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template(
        'items.html',
        items=items,
        category=category,
        loginUser=loginUser)

# APPLICATION CRUD Methods
# Edit a category
# /category/<int:category_id>/edit/


@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
@auth.login_required
def editCategory(category_id):
    loginUser = get_loginUser()
    editedCategory = session.query(Category).filter_by(id=category_id).one()
    if loginUser.id != editedCategory.user.id:
        flash('Not authorized to edit "%s"' % (editedCategory.name))
        return redirect(
            url_for('showItems', category_id=category_id))
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category "%s" successfully edited' % editedCategory.name)
        return redirect(
            url_for('showItems', category_id=category_id))
    else:
        return render_template(
            'editCategory.html',
            category=editedCategory,
            loginUser=loginUser)

# APPLICATION CRUD Methods
# Delete a category
# /category/<int:category_id>/delete/


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
@auth.login_required
def deleteCategory(category_id):
    loginUser = get_loginUser()
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()
    if loginUser.id != categoryToDelete.user.id:
        flash('Not authorized to delete "%s"' % (categoryToDelete.name))
        return redirect(
            url_for('showItems', category_id=category_id))
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('Category "%s" successfully deleted' % categoryToDelete.name)
        session.commit()
        return redirect(
            url_for('showItems', category_id=category_id))
    else:
        return render_template(
            'deleteCategory.html',
            category=categoryToDelete,
            loginUser=loginUser)

# APPLICATION CRUD Methods
# Create a new category item
# /category/<int:category_id>/delete/


@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
@auth.login_required
def newItem(category_id):
    loginUser = get_loginUser()
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newItem = Item(
            title=request.form['title'],
            description=request.form['description'],
            category=category, user_id=loginUser.id)
        session.add(newItem)
        session.commit()
        flash('New Item "%s"  successfully created' % (newItem.title))
        return redirect(
            url_for('showItems', category_id=category_id))
    else:
        return render_template(
            'newItem.html',
            category=category,
            loginUser=loginUser)

# APPLICATION CRUD Methods
# Edit a category item
# /category/<int:category_id>/delete/


app_route_editItem = '/category/<int:category_id>/item/<int:item_id>/edit'


@app.route(app_route_editItem, methods=['GET', 'POST'])
@auth.login_required
def editItem(category_id, item_id):
    loginUser = get_loginUser()
    editedItem = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if loginUser.id != editedItem.user.id:
        flash('Not authorized to edit item "%s"' % (editedItem.title))
        return redirect(url_for('showItems', category_id=category_id))
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash('Item "%s" successfully edited' % (editedItem.title))
        return redirect(
            url_for('showItems', category_id=category_id))
    else:
        return render_template(
            'editItem.html',
            category=category,
            item=editedItem,
            loginUser=loginUser)

# APPLICATION CRUD Methods
# Delete a category item
# /category/<int:category_id>/item/<int:item_id>/delete'


app_route_deleteItem = '/category/<int:category_id>/item/<int:item_id>/delete'


@app.route(app_route_deleteItem, methods=['GET', 'POST'])
@auth.login_required
def deleteItem(category_id, item_id):
    loginUser = get_loginUser()
    category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if loginUser.id != itemToDelete.user.id:
        flash('Not authorized to delete item "%s"' % (itemToDelete.title))
        return redirect(url_for('showItems', category_id=category_id))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item "%s" successfully deleted' % (itemToDelete.title))
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template(
            'deleteItem.html',
            item=itemToDelete,
            loginUser=loginUser)

# SATR APPLICATION Catalog App Webserwer
# on http://localhost:8000
if __name__ == '__main__':
    app.secret_key = secret_key
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
