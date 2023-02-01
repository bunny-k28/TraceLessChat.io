import os
import qrcode
import sqlite3
from pyotp import TOTP

from werkzeug import security


class User:
    def __init__(self, username: str=None):
        self.OTP = TOTP('base32secret3232')
        self.username = username
        self.password = str()
        self.email = str()

    def filter_data(self, data_pack):
        return [data[0] for data in data_pack]


    def login(self):
        self.login_validity_flag = False

        self.db = sqlite3.connect('Database/TLC_database.db')
        self.sql = self.db.cursor()

        try:
            self.sql.execute("SELECT username FROM userLogins")
            self.usernames = self.sql.fetchall()
        except Exception: pass

        self.usernames = self.filter_data(self.usernames)
        if self.username in self.usernames:
            try:
                self.sql.execute("SELECT password FROM userLogins WHERE username=?", (self.username,))
                self.PSWD = self.sql.fetchone()[0]
            except sqlite3.DataError: pass
            finally: self.sql.close(); self.db.close()

            try:
                if security.check_password_hash(self.PSWD, self.password): self.login_validity_flag = True
                else: pass
            except UnboundLocalError: pass

            return self.login_validity_flag
        else: return self.login_validity_flag


    def login_with_email(self):
        self.db = sqlite3.connect('Database/TLC_database.db')
        self.sql = self.db.cursor()

        try:
            self.sql.execute("SELECT email FROM userLogins")
            self.emails = self.sql.fetchall()
        except Exception: pass

        self.emails = self.filter_data(self.emails)
        try:
            self.sql.execute("SELECT username FROM userLogins WHERE email=?", (self.email,))
            self.username = self.sql.fetchone()[0]
        except Exception: pass
        finally: self.sql.close(); self.db.close();

        if self.email in self.emails: return True
        else: return False


    def signup(self):
        self.signup_validity_flag = False
        self.db = sqlite3.connect('Database/TLC_database.db')
        self.sql = self.db.cursor()
        
        try:
            self.sql.execute("SELECT username FROM userLogins")
            self.usernames = self.sql.fetchall()
        except Exception: pass

        try: self.usernames = self.filter_data(self.usernames)
        except Exception: self.usernames = []

        if self.username in self.usernames: return self.signup_validity_flag
        else:
            try:
                self.sql.execute("""INSERT INTO userLogins(username, email, password) 
                        VALUES(?, ?, ?)""", (self.username, self.email, self.password,))
                self.db.commit()
                self.signup_validity_flag = True
            except sqlite3.OperationalError: pass
            finally: self.sql.close(); self.db.close()

            return self.signup_validity_flag


    def create_auth_qr(self):
        self.qr_data = self.OTP.provisioning_uri(name=f'{self.username}', issuer_name=f'TLC.io')
        self.QR = qrcode.make(self.qr_data)

        self.QR.save(f'static/images/archive/{self.username}.png')
        return True


    def verify_user_auth(self, key):
        self.OTP.now()
        return self.OTP.verify(key)


    def delete_account(self):...