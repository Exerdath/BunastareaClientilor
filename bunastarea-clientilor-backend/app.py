from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import singledispatch
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return 'Username: ' + str(self.username) + " Password: " + str(self.password_hash)



@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/addUser', methods=['POST'])
def addUser():
    jsonData = request.get_json()
    username = jsonData['username']
    password = jsonData['password']

    if username is None or password is None:
        return jsonify({'msg': 'No user or password provided'}), 400

    if db.session.query(User).fitler_by(username=username).first() is not None:
        return jsonify({'msg': 'User already exists'}), 400

    user = User(username=username, password_hash=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"user": username, "password": password}), 200


@app.route('/getUsers', methods=['GET'])
def getUsers():
    users = db.session.query(User).all()
    all_users_json = [ob.__dict__ for ob in users]
    for user_json in all_users_json:
        user_json.pop("_sa_instance_state", None)
    return jsonify(all_users_json)

@app.route('/login', methods=['POST'])
def login():
    jsondata = request.get_json()
    username = jsondata['username']
    password = jsondata['password']

    if username is None or password is None:
        return jsonify({'msg': 'No user or password provided'}), 400

    user = User(username=username, password_hash=password)
    userDb=db.session.query(User).filter_by(username=user.username).filter_by(password_hash=user.password_hash).first()
    if userDb is not None:
        return jsonify({'msg': 'Got into Narnia, Good Job mate!'}), 200
    else:
        return jsonify({'msg': 'Failed!'}), 403


if __name__ == '__main__':
    app.run()
