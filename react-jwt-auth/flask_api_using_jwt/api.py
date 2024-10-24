# from flask import Flask, request, jsonify, make_response
# from flask_sqlalchemy import SQLAlchemy
# import uuid
# from werkzeug.security import generate_password_hash, check_password_hash
# import jwt
# import datetime
# from functools import wraps

# app = Flask(__name__)

# # this is my secret key
# app.config['SECRET_KEY'] = 'thisissecretkey'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'

# db = SQLAlchemy(app)


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     public_id = db.Column(db.String(50), unique=True)
#     username = db.Column(db.String(50))
#     password = db.Column(db.String(80))
#     admin = db.Column(db.Boolean)


# class Todo(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     text = db.Column(db.String(50))
#     complete = db.Column(db.Boolean)
#     user_id = db.Column(db.Integer)


# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None

#         if 'x-access-token' in request.headers:
#             token = request.headers['x-access-token']

#         if not token:
#             return jsonify({'message': 'Token is missing! '}), 401

#         try:
#             data = jwt.decode(
#                 token, app.config['SECRET_KEY'], algorithms=['HS256'])
#             current_user = User.query.filter_by(
#                 public_id=data['public_id']).first()
#         except:
#             return jsonify({'message': 'Token is invalid! '}), 401

#         return f(current_user, *args, **kwargs)
#     return decorated


# @app.route('/user', methods=['GET'])
# @token_required
# def get_all_users(current_user):

#     if not current_user.admin:
#         return jsonify({'message': 'Cannot perform that function'})

#     users = User.query.all()
#     output = []
#     for user in users:
#         user_data = {}
#         user_data['public_id'] = user.public_id
#         user_data['username'] = user.username
#         user_data['password'] = user.password
#         user_data['admin'] = user.admin
#         output.append(user_data)
#     return jsonify({"users": output})


# @app.route('/user/<public_id>', methods=['GET'])
# @token_required
# def get_one_user(current_user, public_id):
#     if not current_user.admin:
#         return jsonify({'message': 'Cannot perform that function'})

#     user = User.query.filter_by(public_id=public_id).first()
#     if not user:
#         return jsonify({"message": "No user found!"})
#     user_data = {}
#     user_data['public_id'] = user.public_id
#     user_data['username'] = user.username
#     user_data['password'] = user.password
#     user_data['admin'] = user.admin
#     return jsonify({"user": user_data})


# @app.route('/user', methods=['POST'])
# @token_required
# def create_user(current_user):
#     if not current_user.admin:
#         return jsonify({'message': 'Cannot perform that function'})

#     data = request.get_json()
#     hash_password = generate_password_hash(data['password'], method='sha256')

#     new_user = User(public_id=str(uuid.uuid4()),
#                     username=data['username'], password=hash_password, admin=False)
#     db.session.add(new_user)
#     db.session.commit()
#     return jsonify({"message": "new user created"})


# @app.route('/user/<public_id>', methods=['PUT'])
# @token_required
# def promote_user(public_id):
#     user = User.query.filter_by(public_id=public_id).first()
#     if not user:
#         return jsonify({"message": "No user found!"})
#     user.admin = True
#     db.session.commit()
#     return jsonify({"message": "The user has been promoted"})


# @app.route('/user/<public_id>', methods=['DELETE'])
# @token_required
# def delete_user(public_id):
#     user = User.query.filter_by(public_id=public_id).first()
#     if not user:
#         return jsonify({"message": "The id does not exist"})
#     db.session.delete(user)
#     db.session.commit()

#     return jsonify({"message": "The user id is been deleted"})


# @app.route('/login')
# def login():
#     auth = request.authorization
#     # check if username and password is given
#     if not auth or not auth.username or not auth.password:
#         return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic reaml= "Login required"'})

#     user = User.query.filter_by(username=auth.username).first()
#     # check if user is available or not
#     if not user:
#         return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic reaml= "Login required"'})

#     # check if password is correct
#     if check_password_hash(user.password, auth.password):
#         token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow(
#         ) + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

#         return jsonify({'token': token})
#     return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic reaml= "Login required"'})


# @app.route('/todo', methods=['GET'])
# @token_required
# def get_all_todos(current_user):
#     todos = Todo.query.filter_by(user_id=current_user.id).all()
#     output = []

#     for todo in todos:
#         todo_data = {}
#         todo_data['id'] = todo.id
#         todo_data['text'] = todo.text
#         todo_data['complete'] = todo.complete
#         output.append(todo_data)
#     return jsonify({'message': output})


# @app.route('/todo/<todo_id>', methods=['GET'])
# @token_required
# def get_one_todo(current_user, todo_id):
#     todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
#     if not todo:
#         return jsonify({'message': 'No todo found!'})
#     todo_data = {}
#     todo_data['id'] = todo.id
#     todo_data['text'] = todo.text
#     todo_data['complete'] = todo.complete
#     return jsonify(todo_data)


# @app.route('/todo', methods=['POST'])
# @token_required
# def create_todo(current_user):
#     data = request.get_json()
#     new_todo = Todo(text=data['text'], complete=False, user_id=current_user.id)
#     db.session.add(new_todo)
#     db.session.commit()
#     return jsonify({'message': 'Todo created! '})


# @app.route('/todo/<todo_id>', methods=['PUT'])
# @token_required
# def complete_todo(current_user, todo_id):
#     todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
#     if not todo:
#         return jsonify({'message': 'No todo found!'})
#     todo.complete = True
#     db.session.commit()
#     return jsonify({'message': 'task completed'})


# @app.route('/todo/<todo_id>', methods=['DELETE'])
# @token_required
# def delete_todo(current_user, todo_id):
#     todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
#     if not todo:
#         return jsonify({'message': 'No todo found!'})
#     db.session.delete(todo)
#     db.session.commit()
#     return jsonify({'message': 'Todo deleted'})


# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

# this is my secret key
app.config['SECRET_KEY'] = 'thisissecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing! '}), 401

        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid! '}), 401

        return f(current_user, *args, **kwargs)
    return decorated


def initialize_db():
    with app.app_context():
        db.create_all()
        # Check if default user exists, if not create it
        default_user = User.query.filter_by(username='xyz').first()
        if not default_user:
            hash_password = generate_password_hash(
                'xyz', method='pbkdf2:sha256')
            new_user = User(public_id=str(uuid.uuid4()),
                            username='xyz', password=hash_password, admin=True)
            db.session.add(new_user)
            db.session.commit()


@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):

    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function'})

    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['username'] = user.username
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)
    return jsonify({"users": output})


@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function'})

    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "No user found!"})
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['username'] = user.username
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    return jsonify({"user": user_data})


# Creating a new user
@app.route('/user', methods=['POST'])
# @token_required
def create_user():
    data = request.get_json()
    # hash_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id=str(uuid.uuid4()),
                    username=data['username'], password=data['password'], admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "new user created"})


@app.route('/user/<public_id>', methods=['PUT'])
@token_required
def promote_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "No user found!"})
    user.admin = True
    db.session.commit()
    return jsonify({"message": "The user has been promoted"})


@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "The id does not exist"})
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "The user id is been deleted"})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Username and password are required'}), 400

    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'Invalid username or password', "user": username}), 401

    if (user.password == password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


@app.route('/todo', methods=['GET'])
@token_required
def get_all_todos(current_user):
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    output = []

    for todo in todos:
        todo_data = {}
        todo_data['id'] = todo.id
        todo_data['text'] = todo.text
        todo_data['complete'] = todo.complete
        output.append(todo_data)
    return jsonify({'message': output})


@app.route('/todo/<todo_id>', methods=['GET'])
@token_required
def get_one_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if not todo:
        return jsonify({'message': 'No todo found!'})
    todo_data = {}
    todo_data['id'] = todo.id
    todo_data['text'] = todo.text
    todo_data['complete'] = todo.complete
    return jsonify(todo_data)


@app.route('/todo', methods=['POST'])
@token_required
def create_todo(current_user):
    data = request.get_json()
    new_todo = Todo(text=data['text'], complete=False, user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({'message': 'Todo created! '})


@app.route('/todo/<todo_id>', methods=['PUT'])
@token_required
def complete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if not todo:
        return jsonify({'message': 'No todo found!'})
    todo.complete = True
    db.session.commit()
    return jsonify({'message': 'task completed'})


@app.route('/todo/<todo_id>', methods=['DELETE'])
@token_required
def delete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if not todo:
        return jsonify({'message': 'No todo found!'})
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'Todo deleted'})


if __name__ == '__main__':
    initialize_db()  # Initialize the database with default user
    app.run(debug=True)
