#Made by Sushaan Patel
import random
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from db_init import db, app, Users, Posts

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
  return Users.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
  return render_template('unauthorized.html')

global errmsg
errmsg = ""
global posts_list
posts_list = []

@app.route('/clearfilters/index')
def clear():
  global posts_list
  posts_list = []
  return redirect('/')

@app.route('/clearfilters/post')
def clear1():
  global posts_list
  posts_list = []
  return redirect('/yourposts')

#try google login, comment, report post, profile pic
#add like button
@app.route('/', methods=["POST", "GET"])
def index():
  global errmsg
  errmsg = ""
  global posts_list
  if request.method == "POST":
    search = request.form['search_bar'].lower()
    filters = request.form['filter']
    if filters == "title":
      query = Posts.query.filter(Posts.post_title.like(f"%{search}%")).all()
      for post in query:
        posts_list.append(post)
    if filters == "genre":
      query = Posts.query.filter_by(post_genre=search).all()
      for post in query:
        posts_list.append(post)
    if filters == "author":
      query = Posts.query.filter(Posts.post_creator.like(f"%{search}%")).all()
      for post in query:
        posts_list.append(post)
    return redirect('/')
  else:
    return render_template('index.html', current_user = current_user, posts=posts_list)

@app.route('/signup', methods=["POST","GET"])
def signup():
  global errmsg
  if request.method == "POST":
    new_name = request.form['new_username'].lower()
    new_pass = request.form['new_password']
    new_email = request.form['new_email']
    new_rememeber = True if request.form.get('new_remember_me') else False
    if new_name == "" and new_pass == "" and new_email == "":
      errmsg = "Please enter your Credentails"
      return redirect('/signup')
    if new_name != "" and new_pass == "" and new_email =="":
      errmsg = "Please enter your Credentails"
      return redirect('/signup')
    if new_name != "" and new_pass != "" and new_email == "":
      errmsg = "Please enter your Credentails"
      return redirect('/signup')
    if new_name == "" and new_pass == "" and new_email != "":
      errmsg = "Please enter your Credentails"
      return redirect('/signup')
    if new_name == "" and new_pass != "" and new_email != "":
      errmsg = "Please enter your Credentails"
      return redirect('/signup')
    x = Users.query.all() 
    for i in x:
      if new_name == i.username:
        errmsg = "Username Already Taken"
        return redirect('/signup')
    y = Users(username = new_name, password = generate_password_hash(new_pass, method = "sha256"), email = new_email)
    db.session.add(y)
    db.session.commit()
    user = Users.query.filter_by(username = new_name).first()
    login_user(user, remember=new_rememeber)
    return redirect('/')
  else:
    return render_template('signup.html', errmsg=errmsg)

@app.route('/login', methods=["POST", "GET"])
def login():
  global errmsg
  if request.method == "POST":
    name = request.form['acc_username'].lower()
    password = request.form['acc_password']
    remember = True if request.form.get('remember_me') else False
    x = Users.query.all()
    if name == "" and password == "":
      errmsg = "Please enter your Credentails"
      return redirect('/login')
    if name != "" and password == "":
      errmsg = "Please enter your Credentails"
      return redirect('/login')
    if name == "" and password != "":
      errmsg = "Please enter your Credentails"
      return redirect('/login')
    for i in x:
      if name == i.username: #if exists
        if check_password_hash(i.password, password): #checks passwords
          user = Users.query.filter_by(username = name).first()
          login_user(user, remember=remember)
          return redirect('/')
        else:
          errmsg = "Password is incorret"
          return redirect('/login')
      else:
        errmsg = "Account not found"
        return redirect('/login')
  else:
    return render_template('login.html', errmsg=errmsg)

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect('/login')

@app.route('/create/text', methods=["POST", "GET"])
@login_required
def create_text():
  global errmsg
  if request.method == "POST":
    title = request.form["post_title"]
    genre = request.form.get("post_genre")
    content = request.form["post_content"]
    media = request.form["post_media"]
    citation = request.form["post_citation"]
    anonymity = request.form.get("anonymous")
    creator = current_user.username
    x = datetime.now()
    if anonymity == "yes":
      creator = "Anonymous" 
    post = Posts(post_title = title, post_genre = genre, post_content = content, post_media = media, post_citation = citation, post_anonymity = anonymity, post_creator = creator, post_publishtime = x.date())
    db.session.add(post)
    db.session.commit()
    return redirect('/account')

@app.route('/create/art', methods=["POST", "GET"])
@login_required
def create_art():
  global errmsg
  if request.method == "POST":
    title = request.form["post_title"]
    genre = request.form.get("post_genre")
    content = request.files["post_content"]
    media = request.form["post_media"]
    citation = request.form["post_citation"]
    anonymity = request.form.get("anonymous")
    creator = current_user.username
    x = datetime.now()
    allowed = ['png','jpg','jpeg','gif']
    if anonymity == "yes":
      creator = ["Anonymous", current_user.username]
    y = content.filename.split('.')
    if y[1].lower() in allowed:
      content.save(app.config['UPLOAD_FOLDER'] + secure_filename(current_user.username + "_" + content.filename))
    post = Posts(post_title = title, post_genre = genre, post_content =current_user.username + "_" + content.filename, post_media = media, post_citation = citation, post_anonymity = anonymity, post_creator = creator, post_publishtime = x.date())
    db.session.add(post)
    db.session.commit()
    return redirect('/account')

#add change password route, also add no login page
@app.route('/account')
@login_required
def acc():
  return render_template('account.html', current_user = current_user)

#add html, and code
@app.route('/yourposts')
def yourposts():
  return render_template("posts.html")

#add code
@app.route('/deleteacc')
def deleteacc():
  ""

if __name__ == "__main__":
  app.secret_key = 'writeenkeykavishiandsushaan'
  app.run(debug=True)

# x = Users(username = "sushaan", password = "1234", email = "sushaanpatel@gmail.com")
# db.session.add(x)
# db.session.commit()
# y = Posts.query.filter(Posts.post_title.like("%winter%")).all()
# for i in y:
#   print(i.post_title)