import os
from sqlite3 import connect

# Путь к БД (абсолютный)
db_path = r"E:\projects\Benefit Harm\apps\PC\data\students.db"

conn = connect(db_path)
cursor = conn.cursor()

# Получаем список всех таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

if not tables:
    print("⚠️ В базе данных нет таблиц.")
else:
    for table in tables:
        table_name = table[0]
        print(f"\n📋 Таблица: {table_name}")
        print("-" * 40)

        # Получаем информацию о колонках
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        if not columns:
            print("  (нет колонок)")
            continue

        # Выводим колонки с их типами
        for col in columns:
            # col: (cid, name, type, notnull, dflt_value, pk)
            col_name = col[1]
            col_type = col[2]
            is_pk = col[5] == 1
            pk_mark = "🔑" if is_pk else "  "
            print(f"  {pk_mark} {col_name}: {col_type}")

conn.close()