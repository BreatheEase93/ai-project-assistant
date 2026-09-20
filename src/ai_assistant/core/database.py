import sqlite3


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Функция для связи с базой данных получает на вход путь к базе,
    сортирует ответ как словарь, возвращает обект подключения"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    return conn


def create_tables(conn: sqlite3.Connection):
    """Функция для создания таблицы, с проектами"""
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        path TEXT NOT NULL UNIQUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
                    """)
    conn.commit()
