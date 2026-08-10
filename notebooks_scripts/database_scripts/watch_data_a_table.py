import sqlite3

# Путь к твоей базе данных
PATH = r"E:\projects\Benefit Harm\apps\PC\data\students.db"

def show_all_data():
    conn = sqlite3.connect(PATH)
    cursor = conn.cursor()

    # Получаем список всех таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if not tables:
        print("⚠️ В базе данных нет таблиц.")
        return

    for table_name in tables:
        table = table_name[0]
        print(f"\n📋 Таблица: {table}")
        print("-" * 40)

        # Получаем данные из таблицы
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()

        if not rows:
            print("⚠️ Таблица пуста.")
            continue

        # Получаем имена колонок
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        print("Колонки:", ", ".join(columns))

        # Выводим данные
        for row in rows:
            print(row)

    conn.close()

if __name__ == "__main__":
    show_all_data()