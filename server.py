import os
import flask
import sqlite3

from __init__ import *
from werkzeug import security
from datetime import timedelta
from flask import render_template, redirect, url_for, request, session


server = flask.Flask(__name__)
server.secret_key = '3d9efc4wa651728'
server.permanent_session_lifetime = timedelta(hours=6)


if "Chats" in os.listdir("Database"): pass
else: os.mkdir('Database/Chats')

db = sqlite3.connect('Database/TLC_database.db')
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS userLogins(username TEXT, email TEXT, password HASH)""")
db.commit()

sql.close()
db.close()


# route to redirect to login page
@server.route('/')
def loginRedirector():
    return redirect(url_for('renderLogin'))


# route for login page
@server.route('/login')
def renderLogin():
    session["user"] = None
    session["userStatus"] = "Offline"
    
    if (("signupStatus" in session) and (session["signupStatus"] is True)):
        return render_template('index.html', 
            form_title='Now Login to CHAT!')
    else: return render_template('index.html')

@server.route('/login', methods=['POST'])
def login():
    session["user"] = request.form.get('username')

    user = User(session["user"])
    user.password = request.form.get('pswd')
    if user.login():
        session["userStatus"] = "Online"
        return redirect(url_for('renderDashboard', 
            username=session["user"]))

    else: 
        session['user'] = None
        return render_template('index.html', 
            form_title='SSID/Password is incorrect!')


# route for signup page
@server.route('/signup')
def renderSignup():
    session['signupStatus'] = None
    return render_template('signup.html')

@server.route('/signup', methods=['POST'])
def signup():
    user = User(request.form.get('username'))
    user.email = request.form.get('email')
    user.password = security.generate_password_hash(request.form.get('pswd'), 'sha256')

    if user.signup():
        try: os.mkdir(f"Database/Chats/{request.form.get('username')}")
        except OSError: pass

        session['signupStatus'] = True
        return redirect(url_for('renderLogin', registration=True))

    else:
        return render_template('signup.html', 
            form_title='Username already taken')


# route for logout
@server.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('renderLogin'))


# route for dashboard
@server.route('/dashboard/user:<username>')
def renderDashboard(username):
    if (("user" in session) and (session["user"] is not None)):
        return render_template('dashboard.html', username=username)
    else: return redirect(url_for('logout'))


if __name__ == '__main__':
    server.run(port=8080, debug=True)
    