from DB_Query import DB_Query
import os


DBNAME = 'onlineDok.db'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, DBNAME)
DB = DB_Query(db_path)


def checkUser(inputEmail, inputPassword):
    query = 'SELECT * FROM Users WHERE email = "' + inputEmail + '";'
    cursor = DB.executeSelect(query)
    data = [dict(email=row[0], firstName=row[1], lastName=row[2], password=row[3], admin=row[4], suspended=row[5]) for
            row in cursor.fetchall()]
    print cursor
    for d in data:
        print d
    email = data[0]['email']
    password = data[0]['password']
    print email
    print password
    if password == inputPassword and inputEmail == email:
        return True
    return False


print checkUser('amir.grunfeld223@gmail.com', 'amiramir')
