import sqlite3 as sql

# Connect to the SQLite database
con = sql.connect('db_web.db')

# Create a cursor object
cur = con.cursor()

# Drop the Dictionnaire table if it already exists
cur.execute("DROP TABLE IF EXISTS Dictionnaire")

# Create the Dictionnaire table with the specified columns
sql = '''CREATE TABLE Dictionnaire (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT(100) UNIQUE NOT NULL,
    definition TEXT NOT NULL
)'''
cur.execute(sql)

# Commit the changes to the database
con.commit()

# Close the database connection
con.close()
