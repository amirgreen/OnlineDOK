from DB_Query import DB_Query
import os
from flask_login import UserMixin


class User(UserMixin):

    DBNAME = 'onlineDok.db'
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, DBNAME)
    DB = DB_Query(db_path)

    def __init__(self, email):
        self.id = email
        self.email = email
        query = 'SELECT * FROM Users WHERE email = "' + self.id + '";'
        cursor = self.DB.executeSelect(query)
        data = [dict(email=row[0], firstName=row[1], lastName=row[2], password=row[3], admin=row[4], suspended=row[5]) for
                 row in cursor.fetchall()]
        self.fisrtName = data[0]['firstName']
        self.lastName = data[0]['lastName']
        self.password = data[0]['password']
        self.admin = data[0]['admin']
        # self.is_active = data[0]['suspended']
        # self.is_anonymous = False
        # self.is_authenticated = True

    # def __init__(self, email, firstName, lastName, password, admin, suspended):
    #     self.email = email
    #     self.firstName = firstName
    #     self.lastName = lastName
    #     self.password = password
    #     self.admin = admin
    #     self.is_active = suspended
    #     self.is_anonymous = False
    #     self.is_authenticated = True

    def get_id(self):
        return unicode(self.id)



