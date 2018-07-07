from flask import request, render_template, send_from_directory,session
from amazon import app
from amazon.model import product as product_model
from amazon.model import user as user_model

@app.route('/', methods=['GET'])
def index():
    if 'user_id' in session:
        user_details = user_model.search_by_userid(session['user_id'])
        return render_template('home.html', name=user_details['name'])
    else:
        return render_template('index.html', message='welcome')

@app.route('/logout', methods=['GET'])
def logout():
    del session['user_id']
    return render_template('index.html', message='successfully logout')


@app.route('/api/product', methods=['GET', 'POST'])
def product():
    if request.method == 'GET':
        # lets search for the product here...
        query_name = request.args['name']
        matching_products = product_model.search_by_name(query_name)

        return render_template('results.html', query=query_name, products=matching_products)
    elif request.method == 'POST':
        op_type = request.form['op_type']

        # read data from request and store in a dict
        prod = {
            'name': request.form['name'],
            'desc': request.form['desc'],
            'price': int(request.form['price'])
        }

        if op_type == 'add':
            # insert to DB
            product_model.add_products(prod)

            # take user back to index page
            return render_template('admin.html', message='Product successfully added')
        elif op_type == 'update':  # update the product here
            # create filter and update dicts
            product_id = request.form['product_id']
            matching_products = product_model.get_details(product_id)
            new_name = request.form['name']
            new_desc = request.form['desc']
            new_price = request.form['price']
            if new_name == '':
                new_name = matching_products['name']
            if new_desc == '':
                new_desc = matching_products['desc']
            if new_price == '':
                new_price = matching_products['price']
            updated_product = {
                'name': new_name,
                'desc': new_desc,
                'price': int(new_price)
            }
            product_model.update_products(product_id, updated_product)

            # take user back to index page
            return render_template('admin.html', message='Product successfully updated')


@app.route('/api/user', methods=['POST'])
def user():
    op_type = request.form['op_type']
    if op_type == 'login':
        username = request.form['username']
        password = request.form['password']
        success = user_model.authenticate(username, password)
        if success == 'exist':
            user_details = user_model.search_by_username(username)
            session['user_id'] = str(user_details['_id'])
            name = user_details['name']
            return render_template('home.html', name=name)
        elif success == 'admin':
            user_details = user_model.search_by_username(username)
            session['user_id'] = str(user_details['_id'])
            return render_template('admin.html', message=username)
        else:
            return render_template('index.html', message='User not found')

    elif op_type == 'signup':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        success = user_model.signup_user(name, username, password)
        if success:
            user_details = user_model.search_by_username(username)
            session['user_id'] = str(user_details['_id'])
            return render_template('home.html', query=username)
        else:
            return render_template('index.html', message='Username already exist. Please use another name')
    else:
        # take user back to admin page
        return render_template('index.html', message='welcome')


@app.route('/api/cart', methods=['POST'])
def cart():
    op_type = request.form['op_type']
    if op_type == 'add':
        product_id = request.form['product_id']
        user_id = session['user_id']
        user_model.add_to_cart(user_id, product_id)
        user_details = user_model.search_by_userid(user_id)
        return render_template('home.html', name=user_details['name'])
    elif op_type == 'delete':
        product_id = request.form['product_id']
        user_id = session['user_id']
        user_model.delete_from_cart(user_id, product_id)
        user_details = user_model.search_by_userid(user_id)
        return render_template('home.html', name=user_details['name'])
    elif op_type == 'retrieve':
        cart_item_ids = user_model.retrieve_cart(session['user_id'])
        cart_items = []
        total = 0
        for p_id in cart_item_ids:
            cart_item = product_model.get_details(p_id)
            cart_items.append(cart_item)
            total += cart_item['price']

        user_details = user_model.search_by_userid(session['user_id'])
        return render_template('cart.html', products=cart_items, name=user_details['name'], total=total)


@app.route('/api/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        p_id = request.form['product_id']
        product_model.delete_products(p_id)
        return render_template('admin.html', message='Product successfully deleted')

    elif request.method == 'GET':
        # lets search for the product here...
        query_name = request.args['name']
        matching_products = product_model.search_by_name(query_name)

        return render_template('admin_results.html', query=query_name, products=matching_products)
