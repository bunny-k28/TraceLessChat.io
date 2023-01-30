import os
import sqlite3

from werkzeug import security


class User:
    def __init__(self, username: str):
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


    def signup(self):
        self.signup_validity_flag = False
        self.db = sqlite3.connect('Database/TLC_database.db')
        self.sql = self.db.cursor()
        
        try:
            self.sql.execute("SELECT username FROM userLogins")
            self.usernames = self.sql.fetchall()
        except Exception: pass

        self.usernames = self.filter_data(self.usernames)
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


    def delete_account(self):...