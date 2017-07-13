from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'rF1iDxY6qlTmvyJl'

# Creates a database called blog
class Blog(db.Model):
    # Creates the table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120)) # creates a column that is a string only consisting of 120 characters
    body = db.Column(db.Text) # creates a text column 
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) # connects the user to their blog posts

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

# creates database of the users for blog posts
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True) # the user name needs to be unique 
    password = db.column(db.String(120))
    blog = db.relationship('Blog', backref='owner') # connects the user id to the blog posts

    def __init__(self, username, password):
        self.username = username
        self.password = password