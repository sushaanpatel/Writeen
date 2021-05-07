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

@app.route('/', methods=["POST", "GET"])
def index():
  global a
  a = 0
  return render_template('index.html')

@app.route('/signup', methods=["POST","GET"])
def signup():
  global a
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
  if request.method == "POST":
    global name
    name = request.form['acc_username'].lower()
    password = request.form['acc_password']
    con.reconnect()
    db = con.cursor()
    db.execute(f"SELECT * from users WHERE username = '{name}'")
    x = db.fetchall()
    if x[0][2] == password:
      return redirect('/')
    else:
      a = 2
      return redirect('/login')
  else:
    return render_template('login.html', a=a)

if __name__ == "__main__":
  app.run(debug=True)

# db = con.cursor()
# db.execute("SELECT * FROM users")
# x = db.fetchall()
# print(x)