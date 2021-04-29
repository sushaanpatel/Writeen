import mysql.connector
from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)
con = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password",
  database="pass"
)

@app.route('/', methods = ["POST", "GET"])
def index():
    return render_template('index.html')

if __name__ == "__main__":
  app.run(debug=True)