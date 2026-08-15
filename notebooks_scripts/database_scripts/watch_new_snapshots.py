import sqlite3

# Путь к твоей базе данных
PATH = r"E:\projects\Benefit Harm\apps\PC\data\students.db"

def show_last_100_snapshots():
    conn = sqlite3.connect(PATH)
    cursor = conn.cursor()

    table_name = "game_snapshots_v1"  # или "snapshots" — проверь точное имя

    # Проверяем, существует ли таблица
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if not cursor.fetchone():
        print(f"⚠️ Таблица '{table_name}' не найдена.")
        conn.close()
        return

    print(f"\n📋 Таблица: {table_name}")
    print("-" * 40)

    # Получаем имена колонок
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    print("Колонки:", ", ".join(columns))

    # Получаем последние 100 строк (по ROWID или времени)
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY ROWID DESC LIMIT 100;")
    rows = cursor.fetchall()

    if not rows:
        print("⚠️ Таблица пуста.")
        conn.close()
        return

    print(f"\n📊 Последние {len(rows)} записей:")
    for row in rows:
        print(row)

    conn.close()

if __name__ == "__main__":
    show_last_100_snapshots()