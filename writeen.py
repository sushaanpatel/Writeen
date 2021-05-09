#Made by Sushaan Patel
import mysql.connector
import random
import time
from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)
con = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password",
  database="writeen"
)

global a
a = 0
global b
b = 0
global name

@app.route('/', methods=["POST", "GET"])
def index():
  global a
  global name
  a = 0
  if b == 0:
    return render_template('index.html', b=b)
  if b == 1:
    return render_template('index.html', b=b, name=name)

@app.route('/signup', methods=["POST","GET"])
def signup():
  global a
  global b
  global name
  name = 0
  b = 0
  if request.method == "POST":
    new_name = request.form['new_name'].lower()
    new_pass = request.form['new_password']
    birth_date = request.form['birth_date']
    con.reconnect()
    db = con.cursor()
    db.execute("SELECT username FROM users")
    x = db.fetchall()
    for i in x:
      if new_name == i[0]:
        a = 1
        return redirect('/signup')
    db.execute(f"INSERT INTO users(username, pass, birth_date) VALUES('{new_name}','{new_pass}','{birth_date}')")
    con.commit()
    db.execute(f"""CREATE TABLE posts_{new_name}(
      post_id int auto_increment,
      post_title varchar(500),
      post_genre varchar(20),
      post_content text(60000),
      post_medialinks varchar(1000),
      post_citation varchar(1000),
      post_anonymity varchar(10),
      primary key(post_id)
    )""")
    con.commit()
    return redirect('/login')
  else:
    return render_template('signup.html', a=a)

@app.route('/login', methods=["POST", "GET"])
def login():
  global a
  global b
  global name
  name = 0
  b = 0
  if request.method == "POST":
    name = request.form['acc_username'].lower()
    password = request.form['acc_password']
    con.reconnect()
    db = con.cursor()
    db.execute(f"SELECT * from users WHERE username = '{name}'")
    x = db.fetchall()
    if x[0][2] == password:
      b = 1
      return redirect('/')
    else:
      a = 2
      return redirect('/login')
  else:
    return render_template('login.html', a=a)

#add get route for art
@app.route('/create', methods=["POST", "GET"])
def create():
  if request.method == "POST":
    title = request.form["post_title"]
    genre = request.form.get("post_genre")
    content = request.form["post_content"]
    media = request.form["post_media"]
    citation = request.form["post_citation"]
    anonymity = request.form.get("anonymous")
    creator = name
    con.reconnect()
    db = con.cursor()
    db.execute(f"""INSERT INTO posts(post_title, post_genre, post_content, post_medialinks, post_citation, post_anonymity, post_creator) VALUES("{title}","{genre}","{content}","{media}","{citation}","{anonymity}","{creator}")""")
    con.commit()
    return redirect('/acc')

@app.route('/acc')
def acc():
  if b == 0:
    return render_template('account.html', b=b)
  if b == 1:
    return render_template('account.html', b=b, name=name)


if __name__ == "__main__":
  app.run(debug=True)

# db = con.cursor()
# # db.execute(f"INSERT INTO posts(post_title) VALUES('abcd')")
# # con.commit()
# db.execute("DELETE from posts WHERE post_title = 'acbd'")
# con.commit()
# db.execute("SELECT * FROM posts")
# x = db.fetchall()
# print(x)