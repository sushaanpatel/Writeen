from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://bee0263bfc535e:f9f02f07@us-cdbr-east-03.cleardb.com/heroku_c02aad4223f7e7a'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECERT_KEY'] = 'writeenkeykavishiandsushaan'
app.config['UPLOAD_FOLDER'] = '../Writeen/static/'
db = SQLAlchemy(app)

class Users(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(30),  nullable = False)
  password = db.Column(db.String(300), nullable = False) 
  email = db.Column(db.String(50), nullable = False)

class Posts(db.Model):
  post_id = db.Column(db.Integer, primary_key = True)
  post_title = db.Column(db.String(500), nullable = False)
  post_genre = db.Column(db.String(30), nullable = False)
  post_content = db.Column(db.Text(60000), nullable = False)
  post_media = db.Column(db.String(1000), nullable = True)
  post_citation = db.Column(db.String(1000), nullable = True)
  post_anonymity = db.Column(db.String(5), nullable = False)
  post_creator = db.Column(db.String(30), nullable = False)
  post_publishtime = db.Column(db.String(50), nullable = False)
  post_likes = db.Column(db.Integer, nullable = False)
