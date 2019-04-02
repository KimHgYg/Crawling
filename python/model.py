import mysql.connector
from mysql.connector import Error

class model:
    def __init__(self):
        self.conn = self.Connect()

    def Connect(self):
        try:
            conn = mysql.connector.connect(host='localhost',
                                           database='Crawling',
                                           user='root',
                                           password='tkfkdgody1!')
            if conn.is_connected():
                print('MySQL is connected...')
        except Error as e:
            print(e)
            return None

        return conn

    def insertForeground(self, data):
        query = "INSERT IGNORE INTO foregrounds(title, press, link, day, class) VALUES(%s, %s, %s, %s, %s)"
        cursor = self.conn.cursor()
        try:
            if type(data) is list:
                cursor.executemany(query, data)
            else:
                cursor.execute(query, data)
            self.conn.commit()
        except Error as e:
            print('Error : ', e)

        finally:
            cursor.close()

    def insertBackground(self, data):
        query = "INSERT IGNORE INTO backgrounds(id, tfidf1, tfidf2, tfidf3) VALUES (%s, %s, %s, %s)"
        cursor = self.conn.cursor()
        try:
            if type(data) is list:
                cursor.executemany(query, data)
            else:
                cursor.execute(query, data)
            self.conn.commit()
        except Error as e:
            print('Error : ', e)

        finally:
            cursor.close()

    def selectForeground(self, *args):
        query = "SELECT "
        for arg in args:
            query += arg + " ,"
        query = query[:-1]
        query += "FROM foregrounds"
        results = []
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)

            rows = cursor.fetchall()
            for row in rows:
                results.append(row)

        except Error as e:
            print('select foregorund error : ', e)

        finally:
            cursor.close()

        return results

    def selectBackgroudns(self, *args):
        query = "SELECT "
        for arg in args:
            query += arg + " ,"
        query = query[:-1]
        query += "FROM backgorunds"
        results = []
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)

            rows = cursor.fetchall()
            for row in rows:
                results.append(list(row))

        except Error as e:
            print('select backgorund error : ', e)

        finally:
            cursor.close()

        return results

    def arrangeForeground(self):
        try:
            query = "DELETE FROM foregrounds where id not in (SELECT id FROM backgrounds);"
            cursor = self.conn.cursor()
            cursor.excute(query)
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            cursor.close()

        try:
            query = "DELETE FROM backgrounds where id not in (SELECT id FROM foregrounds);"
            cursor = self.conn.cursor()
            cursor.excute(query)
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            cursor.close()



