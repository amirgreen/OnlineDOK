import sqlite3


class DB_Query:

    def __init__(self, dbName):
        self.dbName = dbName
        self.db_connection = self.connect_db()

    def executeSelect(self, selectQuery):
        cursor = self.db_connection.execute(selectQuery)
        # data = [dict(email=row[0], firstName=row[1], lastName=row[2], password=row[3], admin=row[4], suspended=row[5]) for
        #          row in cursor.fetchall()]
        # print data
        return cursor

    def executeInserUpdateDelete(self, query):
        self.db_connection.execute(query)
        self.db_connection.commit()
        print 'Total changes: ' + str(self.db_connection.total_changes)

    def connect_db(self):
        return sqlite3.connect(self.dbName, check_same_thread=False)
