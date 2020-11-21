from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from customerspy import DataAnalysis
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usersv2.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


class Usersv2(db.Model):
    __table_name__ = 'usersv2'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    isAdmin = db.Column(db.Boolean)
    customerId = db.Column(db.Integer)

    def __repr__(self):
        return 'Username: ' + str(self.username) + " Password: " + str(self.password_hash) + " Admin: " + str(self.isAdmin)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/addUser', methods=['POST'])
def add_user():
    jsonData = request.get_json()
    username = jsonData['username']
    password = jsonData['password']

    if username is None or password is None:
        return jsonify({'msg': 'No user or password provided'}), 400

    if db.session.query(Usersv2).filter_by(username=username).first() is not None:
        return jsonify({'msg': 'User already exists'}), 400

    user = Usersv2(username=username, password_hash=password, isAdmin=False, customerId=1)
    db.session.add(user)
    db.session.commit()
    return jsonify({"user": username, "password": password}), 200


@app.route('/getUsers', methods=['GET'])
def get_users():
    users = db.session.query(Usersv2).all()
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

    user = Usersv2(username=username, password_hash=password)
    user_db = db.session.query(Usersv2).filter_by(username=user.username)\
        .filter_by(password_hash=user.password_hash).first()
    if user_db is not None:
        return jsonify({
            'username': user_db.username,
            'password': user_db.password_hash,
            'isAdmin': user_db.isAdmin,
            'customerId': user_db.customerId
        }), 200
    else:
        return jsonify({'msg': 'Failed!'}), 403


@app.route('/top5buyers', methods=['GET'])
def buyers5():
    data_analyzer = DataAnalysis()
    the_buyers = data_analyzer.get_top_5_buying_customers()
    return the_buyers


@app.route("/avgtop5buyers",methods=['GET'])
def avg_buyers5():
    data_analyzer= DataAnalysis()
    the_buyers=data_analyzer.avg_invoice_spent_top_5_customers()
    return the_buyers


@app.route("/avgbyid/<int:user_id>", methods=['GET'])
def avg_spend_by_id(user_id):
    data_analyzer = DataAnalysis()
    the_buyers = data_analyzer.avg_spent_per_invoice_by_id(user_id)
    return the_buyers


@app.route("/lastinvoicesbyid/<int:user_id>", methods=['GET'])
def last_invoices_by_id(user_id):
    data_analyzer = DataAnalysis()
    the_buyers = data_analyzer.last_invoices_by_id(user_id)
    return the_buyers


if __name__ == '__main__':
    app.run(debug=True)