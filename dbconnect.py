import MySQLdb

# mysql --user=root -p
def connection():
    conn = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                      passwd="1234", # your password
                      db="Exam") # name of the data base
    c = conn.cursor()

    return c, conn
