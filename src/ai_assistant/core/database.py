import sqlite3


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Функция для связи с базой данных получает на вход путь к базе,
    сортирует ответ как словарь, возвращает обект подключения"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    """Функция для создания таблицы, с проектами"""
    cursor = conn.cursor()

    # таблица с проектми
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        path TEXT NOT NULL UNIQUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
                    """)

    # таблица с задачами
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            task_type TEXT NOT NULL CHECK (task_type IN ('big_block', 'subtask')),
            parent_id INTEGER,
            status TEXT NOT NULL DEFAULT 'todo',
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
                        """)
    conn.commit()
