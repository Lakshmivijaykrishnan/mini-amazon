from amazon.model import db
from bson.objectid import ObjectId


def search_by_userid(user_id):
    # lets search for the user here
    query = {'_id': ObjectId(user_id)}
    matching_user = db['users'].find(query)
    if matching_user.count() == 1:
        return matching_user.next()
    else:
        return None


def search_by_username(username):
    query={'username': username}
    matching_user = db['users'].find(query)
    if matching_user.count() > 0:
        return matching_user.next()
    else:
        return None


def signup_user(name, username, password):
    existing_user = search_by_username(username)
    if existing_user is not None:
        return False

    user ={
        'name': name,
        'username': username,
        'password': password,
        'cart': []
    }
    db['users'].insert_one(user)
    return True


def authenticate(username, password):

    if (username == 'admin') and (password == 'admin'):
        return 'admin'

    else:
        user = search_by_username(username)

        if user is None:
            # user does not exist
            return 'nobody'

        if user['password'] == password:
            # user exists and correct password
            return 'exist'
        else:
            # user exists but wrong password
            return 'nobody'


def add_to_cart(user_id, product_id):
    condition ={'_id': ObjectId(user_id)}

    cursor = db.users.find(condition)

    if cursor.count() == 1:
        user_data = cursor[0]
    else:
        return False

    if 'cart' not in user_data:
        user_data['cart'] = []

    if product_id not in user_data:
        user_data['cart'].append(product_id)
        db.users.update_one(filter=condition, update={'$set': user_data})

    return True


def delete_from_cart(user_id, product_id):
    condition = {'_id': ObjectId(user_id)}
    cursor = db.users.find(condition)

    if cursor.count() == 1:
        user_data = cursor[0]
    else:
        return False

    if product_id not in user_data['cart']:
        return False

    user_data['cart'].remove(product_id)
    db.users.update_one(filter=condition, update={'$set': user_data})
    return True


# return all products in a users cart
def retrieve_cart(user_id):
    condition = {'_id': ObjectId(user_id)}

    cursor = db.users.find(condition)

    if cursor.count() == 1:
        return cursor[0]['cart']
    else:
        return False
