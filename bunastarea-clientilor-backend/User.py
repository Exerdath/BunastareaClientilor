# from app import db
#
#
# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key = True)
#     username = db.Column(db.String(32), index = True)
#     password_hash = db.Column(db.String(128))
#
#     def __repr__(self):
#         return 'Username: ' + str(self.username) + " Password: " + str(self.password_hash)
