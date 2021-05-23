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
  return redirect('/login')

global ypcond
ypcond = 0
global incond
incond = 0
global errmsg
errmsg = ""
global ermsg
ermsg =""
global posts_list
posts_list = []
global current_page
current_page = ""
global art_list
art_list = []
global yourposts_list
yourposts_list = []

@app.route('/home')
def home():
  global ypcond
  ypcond = 0
  global incond
  incond = 0
  global posts_list
  posts_list = []
  global yourposts_list
  yourposts_list = 0
  return redirect('/')

@app.route('/clearfilters')
def clear():
  global posts_list
  global yourposts_list
  global current_page
  global ypcond
  global incond
  Users.query.session.close()
  Posts.query.session.close()
  if current_page == "/yourposts":
    yourposts_list = []
    ypcond = 0
  else:
    posts_list = []
    incond = 0
  return redirect(current_page)

#try google login, comment, report post, profile pic
#add like button, add refeshed 
@app.route('/')
def index():
  global incond
  global current_page
  current_page = "/"
  global errmsg
  errmsg = ""
  global ermsg
  ermsg = ""
  global posts_list
  global art_list
  art_list = os.listdir("static")
  if incond == 0:
    Posts.query.session.close()
    max_id = Posts.query.all()
    random_list = list(range(0, len(max_id)))
    count = 0
    random.shuffle(random_list)
    while count < len(max_id):
      query = Posts.query.all()
      posts_list.append(query[random_list[count]])
      count += 1
  return render_template('index.html', current_user = current_user, posts=posts_list, len = len, art = art_list)

#add newest and oldest
@app.route('/search', methods=["POST", "GET"])
def filter():
  global posts_list
  global current_page
  global incond
  posts_list = []
  incond = 1
  if request.method == "POST":
    search = request.form['search_bar'].lower()
    filters = request.form['filter']
    Posts.query.session.close()
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

@app.route('/signup', methods=["POST","GET"])
def signup():
  global errmsg
  if request.method == "POST":
    new_name = request.form['new_username'].lower()
    new_pass = request.form['new_password']
    new_email = request.form['new_email']
    Users.query.session.close()
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
    if '~' in new_name:
      errmsg = "'~' is not allowed in username"
      return redirect('/signup')
    if new_name == "anonymous":
      errmsg = "'Anonymous' can not used as a username"
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
  global ermsg
  global current_page
  if request.method == "POST":
    name = request.form['acc_username'].lower()
    password = request.form['acc_password']
    remember = True if request.form.get('remember_me') else False
    Users.query.session.close()
    x = Users.query.all()
    if name == "" and password == "":
      ermsg = "Please enter your Credentails"
      return redirect('/login')
    if name != "" and password == "":
      ermsg = "Please enter your Credentails"
      return redirect('/login')
    if name == "" and password != "":
      ermsg = "Please enter your Credentails"
      return redirect('/login')
    for i in x:
      if name == i.username: #if exists
        if check_password_hash(i.password, password): #checks passwords
          user = Users.query.filter_by(username = name).first()
          login_user(user, remember=remember)
          return redirect(current_page)
        else:
          ermsg = "Password is incorret"
          return redirect('/login')
      else:
        ermsg = "Account not found"
        return redirect('/login')
  else:
    return render_template('login.html', errmsg=ermsg)

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect('/login')

#add markdown
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
      creator = "Anonymous~" + current_user.username 
    Posts.query.session.close()
    post = Posts(post_title = title, post_genre = genre, post_content = content, post_media = media, post_citation = citation, post_anonymity = anonymity, post_creator = creator, post_publishtime = x.date(), post_likes = 0)
    db.session.add(post)
    db.session.commit()
    return redirect('/yourposts')

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
      creator = "Anonymous~" + current_user.username
    y = content.filename.split('.')
    if y[1].lower() in allowed:
      filename = content.filename
      content.save(app.config['UPLOAD_FOLDER'] + secure_filename(current_user.username + "_" + str(filename).replace(" ", "_")))
    else:
      flash("File type not allowed")
      return redirect(current_page)
    Posts.query.session.close()
    post = Posts(post_title = title, post_genre = genre, post_content =current_user.username + "_" + str(content.filename).replace(" ", "_"), post_media = media, post_citation = citation, post_anonymity = anonymity, post_creator = creator, post_publishtime = x.date(), post_likes = 0)
    db.session.add(post)
    db.session.commit()
    return redirect('/yourposts')

#add change password route
@app.route('/account')
@login_required
def acc():
  global current_page
  global ypcond 
  ypcond = 0
  current_page = "/account"
  Users.query.session.close()
  Posts.query.session.close()
  return render_template('account.html', current_user = current_user)

# add the edit and delete besides title, add newest and oldest
@app.route('/searchyourposts', methods = ["POST"])
def searchposts():
  global ypcond
  global yourposts_list
  global current_page
  ypcond = 1
  yourposts_list = []
  if request.method == "POST":
    search = request.form['search_bar'].lower()
    filters = request.form['filter']
    Posts.query.session.close()
    if filters == "title":
      query = Posts.query.filter(Posts.post_title.like(f"%{search}%")).all()
      for post in query:
        if current_user.username in post.post_creator.split('~'):
          yourposts_list.append(post)
    if filters == "genre":
      query = Posts.query.filter_by(post_genre=search).all()
      for post in query:
        if current_user.username in post.post_creator.split('~'):
          yourposts_list.append(post)
    if filters == "all":
      query = Posts.query.filter_by(post_creator = current_user.username).all()
      for post in query:
        yourposts_list.append(post)
      query2 = Posts.query.filter_by(post_creator = "Anonymous~" + current_user.username).all()
      for post2 in query2:
        yourposts_list.append(post2)
    return redirect('/yourposts')

#add html, and code, add edit and delete
@app.route('/yourposts')
@login_required
def yourposts():
  global ypcond
  global current_page
  current_page = "/yourposts"
  global yourposts_list
  global art_list
  art_list = os.listdir("static")
  Posts.query.session.close()
  if ypcond == 0:
    query = Posts.query.filter_by(post_creator = current_user.username).all()
    for post in query:
      yourposts_list.append(post)
    query2 = Posts.query.filter_by(post_creator = "Anonymous~" + current_user.username).all()
    for post2 in query2:
      yourposts_list.append(post2)
  return render_template('posts.html', posts=yourposts_list, art = art_list,len = len)

@app.route('/deleteacc')
@login_required
def deleteacc():
  Users.query.session.close()
  delete = Users.query.filter_by(username = current_user.username).first()
  logout_user()
  db.session.delete(delete)
  db.session.commit()
  return redirect('/signup')

if __name__ == "__main__":
  app.run(debug=True)

# x = Users(username = "sushaan", password = "1234", email = "sushaanpatel@gmail.com")
# db.session.add(x)
# db.session.commit()
# y = Posts.query.filter(Posts.post_title.like("%winter%")).all()
# for i in y:
#   print(i.post_title)