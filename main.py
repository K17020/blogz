from flask import Flask, request, redirect, render_template, flash,session
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
    password = db.Column(db.String(120))
    blog = db.relationship('Blog', backref='owner') # connects the user id to the blog posts

    def __init__(self, username, password):
        self.username = username
        self.password = password

# Checks to see if the user has logged in before displaying the page
@app.before_request
def require_login():
    allowed_routes = ['login','signup','index','individual_post'] # the are the allowed app.route if the user is not logged in
    if request.endpoint not in allowed_routes and 'username' not in session: # if the user is not logged in redirect them to the login page
        return redirect('/login')

# route for logout of user
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

# This route displays the name of all users


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/blog')
def individual_post():
    return render_template('index.html')



@app.route('/newpost', methods=['POST','GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
    
        if title and body: # If title and body is true do what is below (This returns a falsely if length is 0)
            newpost = Blog(title, body, owner)
            db.session.add(newpost) # Stage the data for the database
            db.session.commit() # Commmit addtion to the database
            return redirect('/blog') # This should render tempate 
    
    return render_template("newpost.html")

# route that handles the sign-in for the user
@app.route('/signup', methods=['POST','GET'])
def signup():
    
    if request.method == 'POST': # if the request is a POST 
        username = request.form['username'] # Grab information from forms 
        password = request.form['password']
        verify_password = request.form['verify_password'] 

        # Error messages 
        error_User = 'Please enter a username'
        error_Exist = 'The username already exist'
        error_PW = 'Please enter a password'
        error_VPW = 'The password does not match'
        error_Length = 'The username and password need to be 3 or more characters'
        
        # Basic validation  
        if len(username) == 0 or len(password) == 0: # If nothing is entered into the Username or Password return page with error message
            return render_template('signup.html', error_PW=error_PW,error_User=error_User,username=username)
        
        elif len(username) <= 3 or len(password) <= 3: # If the length of the username or password is less then 3 return error message  
            return render_template('signup.html', username=username, error_PW=error_Length, error_User=error_Length)
       
        elif password != verify_password: # If the passwords do not match return the page and error message.
            return render_template('signup.html',username=username, error_PW=error_VPW) 
        
        else:
            request_username = User.query.filter_by(username=username).first() # Query the user table and checks to see if the username exists in the table
            if request_username: # will return a true if the user exist in table and false if the user doesn't exist
                return render_template('signup.html', username=username, error_User=error_Exist)
            else: # otherwise if it doesn't exist in the database commit new user to database
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username # keeps the user logged in once they register
                return redirect('/newpost')
    
    return render_template('signup.html')


# route for users to login to their own blog
@app.route('/login', methods=['POST','GET'])
def login():
    
    error_User = "That username does not exist" 
    error_PW = 'That password is incorrect'

    if request.method == 'POST': # If the user attempts to post data to the table
        username = request.form['username'] # grab the username from the login page
        password = request.form['password'] # grab the password from the login page

        compare_user_info = User.query.filter_by(username=username).first() # Checks to see if the user name is in the data base by query the table for the name from the form

        if compare_user_info: # if true
            if password != compare_user_info.password: # Compare the password from the one recored in the database
                return render_template('login.html', error_PW=error_PW)
            elif password == compare_user_info.password: # Compare to see if the passwords are correct
                session['username'] = username # keeps the user logged in once they enter the correct login information
                return redirect('/newpost')
        
        return render_template('login.html', error_User=error_User)

    return render_template("login.html") # renders the template for the user login page

if __name__ == '__main__':
    app.run()