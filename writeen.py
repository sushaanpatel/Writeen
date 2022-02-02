#Made by Sushaan Patel
import os
import time
import random
import pyimgur
import dotenv
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from db_init import db, app, Users, Posts, ask_us_form, Comments

dotenv.load_dotenv()
client_id = os.environ.get('IMGUR_ID')
client_secret = os.environ.get('IMGUR_SECRET')
db_pass = os.environ.get('DB')
client = pyimgur.Imgur(client_id, client_secret=client_secret)
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
  return Users.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
  return redirect('/login')

def check(key, val):
  if session.get(key) == None:
    session[key] = val

@app.before_first_request
def before():
  session.clear()
  check('errmsg', "")
  check('ermsg', "")
  check('errormsg', "")
  check('currentp',"")
  check('static_list', [])

@app.route('/like/<int:post_id>')
def like(post_id):
  try:
    if current_user.is_authenticated == True:
      Posts.query.session.close()
      post = Posts.query.get(post_id)
      liked_by = post.post_liked_by.split(',')
      usernames = []
      string = ""
      for i in liked_by:
        usernames.append(i)
      if current_user.username in usernames:
        for user in liked_by:
          if user == current_user.username:
            liked_by.remove(user)
        for x in liked_by:
          if string == "":
            string = string + x
          else:
            string = string + f",{x}"
        post.post_liked_by = string
        post.post_netlikes -= 1
        db.session.commit()
      else:
        post.post_liked_by = post.post_liked_by + f",{current_user.username}"
        post.post_netlikes += 1
        db.session.commit()
    else:
      flash('6')
    return redirect('/explore/l=1&filter=none')
  except:
    flash('err')
    return redirect(session['currentp'])

@app.route('/comment/<int:p_id>', methods=['POST'])
def comment_on_post(p_id):
  # try:
  if current_user.is_authenticated == True:
    if request.method == 'POST':
      comment = request.form['comment']
      date = datetime.now()
      new = Comments(comment = comment, user_id = current_user.id, username = current_user.username, p_id = p_id, date = date.date())
      db.session.add(new)
      db.session.commit()
      return redirect('/explore/l=1&filter=none')
  else:
    flash('6')
    return redirect('/explore/l=1&filter=none')

@app.route('/delete/comment/<int:com_id>')
def del_com(com_id):
  try:
    comment = Comments.query.get(com_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect('/explore/l=1&filter=none')
  except:
    flash('err')
    return redirect('/explore/l=1&filter=none')

@app.route('/')
def index():
  try:
    session['currentp'] = "/"
    return render_template("about_us.html")
  except:
    flash('err')
    return redirect(session['currentp'])

@app.route('/aboutus', methods = ["POST", "GET"])
def aboutus():
  try:
    if request.method == "POST":
      if current_user.is_authenticated == False:
        flash('6')
        return redirect('/aboutus')
      firstname = request.form["fname"]
      content1 = request.form["content"]
      uname = current_user.username
      entry =  ask_us_form(fname = firstname, content = content1, username = uname)
      db.session.add(entry)
      db.session.commit()
      flash('8')
      return redirect('/aboutus')
    else:
      return render_template('about_us2.html')
  except:
    flash('err')
    return redirect(session['currentp'])  

#add with paginate and upgraded UI

#try comment, report post, profile pic 
@app.route('/explore/', defaults={'l':0,'fil':None}, methods=["POST","GET"])
@app.route('/explore/l=<int:l>&filter=<string:fil>', methods=["POST","GET"])
def explore(l, fil):
  try:
    session['currentp'] = "/explore/"
    art_list = ["png", "jpg", "jpeg", "gif"]
    if request.method == "POST":
      posts_list = []
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
        query = Posts.query.all()
        for i in query:
          if search in i.post_creator.split('~')[0].lower():
            posts_list.append(i)
      if filters == "oldest":
        query = Posts.query.all()
        for i in query:
          posts_list.append(i)
      if filters == "editorial":
        query = Posts.query.all()
        for i in query:
          if "writeenblogs" in i.post_creator.split('~')[0].lower():
            posts_list.append(i)
      if filters == "random":
        max_id = Posts.query.all()
        random_list = []
        for i in max_id:
          random_list.append(i.post_id)
        count = 0
        random.shuffle(random_list)
        while count < len(max_id):
          post = Posts.query.filter_by(post_id = random_list[count]).first()
          posts_list.append(post)
          count += 1
      posts_list = posts_list[::-1]
      session['static_list'] = []
      for i in posts_list:
        session['static_list'].append(i.post_id)
      posts_list = posts_list[::-1]
      session['msg'] = "searched"
      return render_template('index.html', current_user = current_user, posts=posts_list, len = len, art = art_list, msg = session['msg'])
    else:
      if l == 1:
        posts_list = []
        count1 = 0
        while count1 < len(session['static_list']):
          post = Posts.query.filter_by(post_id = session['static_list'][count1]).first()
          posts_list.append(post)
          count1 += 1
        posts_list = posts_list[::-1]
        return render_template('index.html', current_user = current_user, posts=posts_list, len = len, art = art_list, msg = session['msg'])
      if l == 2:
        session['static_list'] = []
        posts_list = []
        query = Posts.query.filter_by(post_genre=fil).all()
        for post in query:
          posts_list.append(post)
        posts_list = posts_list[::-1]
        for i in posts_list:
          session['static_list'].append(i.post_id)
        session['msg'] = "searched"
        return render_template('index.html', current_user = current_user, posts=posts_list, len = len, art = art_list, msg = session['msg'])
      posts_list = []
      max_id = Posts.query.all()
      random_list = []
      for i in max_id:
        random_list.append(i.post_id)
      count = 0
      session['static_list'] = random_list
      while count < len(max_id):
        post = Posts.query.filter_by(post_id = random_list[count]).first()
        posts_list.append(post)
        count += 1
      posts_list = posts_list[::-1]
      session['msg'] = ""
      return render_template('index.html', current_user = current_user, posts=posts_list, len = len, art = art_list, msg = session['msg'])
  except:
    flash('err')
    return redirect(session['currentp'])

@app.route('/signup', methods=["POST","GET"])
def signup():
  try:
    if request.method == "POST":
      new_name = request.form['new_username'].lower()
      new_pass = request.form['new_password']
      new_email = request.form['new_email']
      Users.query.session.close()
      new_rememeber = True if request.form.get('new_remember_me') else False
      if new_name == "" and new_pass == "" and new_email == "":
        session['errmsg'] = "Please enter your Credentails"
        return redirect('/signup')
      if new_name != "" and new_pass == "" and new_email =="":
        session['errmsg'] = "Please enter your Credentails"
        return redirect('/signup')
      if new_name != "" and new_pass != "" and new_email == "":
        session['errmsg'] = "Please enter your Credentails"
        return redirect('/signup')
      if new_name == "" and new_pass == "" and new_email != "":
        session['errmsg'] = "Please enter your Credentails"
        return redirect('/signup')
      if new_name == "" and new_pass != "" and new_email != "":
        session['errmsg'] = "Please enter your Credentails"
        return redirect('/signup')
      if '~' in new_name:
        session['errmsg'] = "'~' is not allowed in username"
        return redirect('/signup')
      if new_name == "anonymous":
        session['errmsg'] = "'Anonymous' can not used as a username"
        return redirect('/signup')
      x = Users.query.all() 
      for i in x:
        if new_name == i.username:
          session['errmsg'] = "Username Already Taken"
          return redirect('/signup')
      y = Users(username = new_name, password = generate_password_hash(new_pass, method = "sha256"), email = new_email)
      db.session.add(y)
      db.session.commit()
      user = Users.query.filter_by(username = new_name).first()
      login_user(user, remember=new_rememeber)
      return redirect('/explore/')
    else:
      return render_template('signup.html', errmsg=session['errmsg'])
  except:
    flash('err')
    return redirect(session['currentp'])

@app.route('/login', methods=["POST", "GET"])
def login():
  try:
    if current_user.is_authenticated == True:
      return redirect('/explore')
    if request.method == "POST":
      name = request.form['acc_username'].lower()
      password = request.form['acc_password']
      remember = True if request.form.get('remember_me') else False
      Users.query.session.close()
      x = Users.query.all()
      if name == "" and password == "":
        session['ermsg'] = "Please enter your Credentails"
        return redirect('/login')
      if name != "" and password == "":
        session['ermsg'] = "Please enter your Credentails"
        return redirect('/login')
      if name == "" and password != "":
        session['ermsg'] = "Please enter your Credentails"
        return redirect('/login')
      user_list = []
      for i in x:
        user_list.append(i.username)
      if name in user_list:
        user = Users.query.filter_by(username = name).first()
        if check_password_hash(user.password, password): #checks passwords
          login_user(user, remember=remember)
          return redirect('/explore/')
        else:
          session['ermsg'] = "Password is incorret"
          return redirect('/login')
      else:
        session['ermsg'] = "Account not found"
        return redirect('/login')
    else:
      return render_template('login.html', errmsg=session['ermsg'])
  except Exception as e:
    flash('err')
    print(e)
    return redirect(session['currentp'])

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect('/login')

#add markdown
@app.route('/create/text', methods=["POST", "GET"])
@login_required
def create_text():
  try:
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
      post = Posts(post_title = title, post_genre = genre, post_content = content, post_media = media, post_citation = citation, post_anonymity = anonymity, post_creator = creator, post_publishtime = x.date(), post_liked_by = f"{current_user.username}", post_netlikes = 1)
      db.session.add(post)
      db.session.commit()
      return redirect('/yourposts')
  except:
    flash('err')
    return redirect(session['currentp'])

@app.route('/create/art', methods=["POST", "GET"])
@login_required
def create_art():
  try:
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
      filelink = None
      if anonymity == "yes":
        creator = "Anonymous~" + current_user.username
      y = content.filename.split('.')
      if y[1].lower() in allowed:
        filename = current_user.username + "_" + str(content.filename).replace(" ", "_")
        content.save(app.config['UPLOAD_FOLDER'] + filename)
        filelink = client.upload_image("static/" + filename, title=filename)
        if os.path.exists("static/" + filename):
          os.remove("static/" + filename)
      else:
        flash("2")
        return redirect(session['currentp'])
      Posts.query.session.close()
      post = Posts(post_title = title, post_genre = genre, post_content = filelink.link, post_media = media, post_citation = citation, post_anonymity = anonymity, post_creator = creator, post_publishtime = x.date(), post_liked_by = f"{current_user.username}", post_netlikes = 1)
      db.session.add(post)
      db.session.commit()
      return redirect('/yourposts')
  except:
    flash('err')
    return redirect(session['currentp'])

@app.route('/account')
@login_required
def acc():
  try:
    session['currentp'] = "/account"
    return render_template('account.html', current_user = current_user)
  except:
    flash('err')
    return redirect(session['currentp'])

@app.route('/change/username', methods = ["POST", "GET"])
@login_required
def changeusername():
  try:
    if request.method == "POST":
      Users.query.session.close()
      new_username = request.form['new_username'].lower()
      x = Users.query.all()
      for i in x:
        if new_username == i.username:
          flash("1")
          return redirect('/account')
      posts = Posts.query.filter_by(post_creator = current_user.username).all()
      for i in posts:
        i.post_creator = new_username
        db.session.commit()
      user = Users.query.filter_by(username = current_user.username).first()
      user.username = new_username
      db.session.commit()
      flash("3")
      return redirect('/account')
  except:
    flash('err')
    return redirect(session['currentp'])

@app.route('/change/password', methods = ["POST", "GET"])
@login_required
def changepassword():
  try:
    if request.method == "POST":
      Users.query.session.close()
      current_pass = request.form["current_pass"]
      new_pass = request.form["new_pass"]
      user = Users.query.filter_by(username = current_user.username).first()
      if check_password_hash(user.password, current_pass):
        flash("4")
        user.password = generate_password_hash(new_pass, method = "sha256")
        db.session.commit()
        return redirect('/account')
      else:
        flash("5")
        return redirect('/account')
  except:
    flash('err')
    return redirect(session['currentp'])

@app.route('/edit/text/<int:post_id>', methods = ["POST", "GET"])
@login_required
def edit_text(post_id):
  try:
    if request.method == "POST":
      Posts.query.session.close()
      title = request.form["post_title"]
      genre = request.form.get("post_genre")
      content = request.form["post_content"]
      media = request.form["post_media"]
      citation = request.form["post_citation"]
      anonymity = request.form.get("anonymous")
      creator = current_user.username
      x = datetime.now()
      if title == "" and content == "":
        session['errormsg'] = "Title and Content can't be empty"
        return redirect(f'/edit/text/{post_id}')
      if title != "" and content =="":
        session['errormsg'] = "Content can't be empty"
        return redirect(f'/edit/text/{post_id}')
      if title == "" and content != "":
        session['errormsg'] = "Title can't be empty"
        return redirect(f'/edit/text/{post_id}')
      if anonymity == "yes":
        creator = "Anonymous~" + current_user.username
      post = Posts.query.get(post_id)
      post.post_title = title
      post.post_genre = genre
      post.post_content = content
      post.post_media = media
      post.post_citation = citation
      post.post_anonymity = anonymity
      post.post_creator = creator
      post.post_publishtime = x.date()
      db.session.commit()
      return redirect('/yourposts')
    else:
      edit_post = Posts.query.get(post_id)
      if edit_post.post_creator == current_user.username:
        return render_template('edit_text.html', post = edit_post, err=session['errormsg'])
      else:
        return redirect('/yourposts')
  except:
    flash('err')
    return redirect(session['currentp'])

@app.route('/edit/art/<int:post_id>', methods = ["POST", "GET"])
@login_required
def edit_art(post_id):
  try:
      if request.method == "POST":
        Posts.query.session.close()
        title = request.form["post_title"]
        genre = request.form.get("post_genre")
        media = request.form["post_media"]
        citation = request.form["post_citation"]
        anonymity = request.form.get("anonymous")
        creator = current_user.username
        x = datetime.now()
        if title == "":
          session['errormsg'] = "Title can't be empty"
          return redirect(f'/edit/art/{post_id}')
        if anonymity == "yes":
          creator = "Anonymous~" + current_user.username
        post = Posts.query.get(post_id)
        post.post_title = title
        post.post_genre = genre
        post.post_media = media
        post.post_citation = citation
        post.post_anonymity = anonymity
        post.post_creator = creator
        post.post_publishtime = x.date()
        db.session.commit()
        return redirect('/yourposts')
      else:
        edit_post = Posts.query.get(post_id)
        if edit_post.post_creator == current_user.username:
          return render_template('edit_art.html', post = edit_post, err = session['errormsg'])
        else:
          return redirect('/yourposts')
  except:
    flash('err')
    return redirect(session['currentp'])

@app.route('/delete/post/<int:post_id>')
@login_required
def deletepost(post_id):
  try:
    delete_post = Posts.query.get(post_id)
    db.session.delete(delete_post)
    db.session.commit()
    return redirect('/yourposts')
  except:
    flash('err')
    return redirect(session['currentp'])

@app.route('/yourposts', methods = ["POST", "GET"])
@login_required
def yourposts():
  try:
    session['currentp'] = "/yourposts"
    art_list = ["png", "jpg", "jpeg", "gif"]
    if request.method == "POST":
      yourposts_list = []
      search = request.form['search_bar'].lower()
      filters = request.form['filter']
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
      yourposts_list = yourposts_list[::-1]
      msg = "searched"
      return render_template('posts.html', posts = yourposts_list, art = art_list, len = len, msg = msg)  
    else:
      yourposts_list = []
      query = Posts.query.filter_by(post_creator = current_user.username).all()
      for post in query:
        yourposts_list.append(post)
      query2 = Posts.query.filter_by(post_creator = "Anonymous~" + current_user.username).all()
      for post2 in query2:
        yourposts_list.append(post2)
      yourposts_list = yourposts_list[::-1]
      msg = ""
    return render_template('posts.html', posts = yourposts_list, art = art_list, len = len, msg = msg)
  except:
    flash('err')
    return redirect(session['currentp'])

@app.route('/delete/account')
@login_required
def deleteacc():
  try:
    delete = Users.query.filter_by(username = current_user.username).first()
    deletepost = Posts.query.filter_by(post_creator = current_user.username).all()
    logout_user()
    db.session.delete(delete)
    db.session.commit()
    for post in deletepost:
      db.session.delete(post)
      db.session.commit()
    return redirect('/signup')
  except:
    flash('err')
    return redirect(session['currentp'])

if __name__ == "__main__":
  app.run(debug=True)