import os
import flask
import sqlite3

from __init__ import *
from werkzeug import security
from datetime import timedelta
from flask_qrcode import QRcode
from flask import render_template, redirect, url_for, request, session


server = flask.Flask(__name__)
server.secret_key = '3d9efc4wa651728'
server.permanent_session_lifetime = timedelta(hours=6)

QRcode(server)

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
    session.pop("authQRcodePath", None)

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
    session['tempUserName'] = None
    return render_template('signup.html')

@server.route('/signup', methods=['POST'])
def signup():
    session['tempUserName'] = request.form.get('username')
    user = User(session['tempUserName'])
    user.email = request.form.get('email')
    user.password = security.generate_password_hash(request.form.get('pswd'), 'sha256')

    if user.signup():
        try: os.mkdir(f"Database/Chats/{session['tempUserName']}")
        except OSError: pass

        session['signupStatus'] = True
        if user.create_auth_qr():
            session["authQRcodePath"] = f"../static/images/archive/{session['tempUserName']}.png"
            return redirect(url_for('renderVerifyer'))
        else: pass

    else:
        return render_template('signup.html', 
            form_title='Username already taken')


# route for google authentication
@server.route('/verify-user')
def renderVerifyer():
    if (("signupStatus" in session) and (session["signupStatus"] is True)):
        return render_template('displayQR.html', 
            QRcode_path=session["authQRcodePath"])

@server.route('/verify-user', methods=['POST'])
def verifyUserAuth():
    verifyer = User()
    if verifyer.verify_user_auth(str(request.form.get('auth-key'))):
        try: os.remove(f'static/images/archive/{session["tempUserName"]}.png')
        except OSError: pass

        try: session.pop('tempUserName', None)
        except KeyError: pass

        return redirect(url_for('renderLogin', registration=True))

    else: return render_template('displayQR.html', 
            form_title="Incorrect Auth Key", 
            QRcode_path=session["authQRcodePath"])


# route for forgot credential login
@server.route('/login-through-email')
def renderEmailLogin():
    session["user"] = None
    session["userStatus"] = "Offline"

    return render_template('resetCredentials.html')

@server.route('/login-through-email', methods=['POST'])
def emailLogin():
    user = User()
    user.email = request.form.get('email')

    session['user'] = user.login_with_email()
    if session['user'][0]:
        if user.verify_user_auth(request.form.get('auth-key')):
            session['user'] = session['user'][-1]
            session["userStatus"] = "Online"
            return redirect(url_for('renderDashboard', 
                username=session["user"]))

    else: 
        session['user'] = None
        return render_template('index.html', 
            form_title='Email/Auth-Key is incorrect!')


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
    