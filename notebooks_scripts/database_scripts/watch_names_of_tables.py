from sqlite3 import connect

PATH = r"/data/students.db"

conn = connect(PATH)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())  # Должен вывести список, содержащий 'students'