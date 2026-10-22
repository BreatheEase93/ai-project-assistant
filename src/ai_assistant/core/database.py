import sqlite3
from pathlib import Path


def get_db_connection(db_path: str | Path) -> sqlite3.Connection:
    """Функция для связи с базой данных получает на вход путь к базе,
    сортирует ответ как словарь, возвращает обект подключения"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    """Функция для создания таблицы, с проектами и задачами, а также отчетов и т.д."""
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
            status TEXT NOT NULL DEFAULT 'todo' CHECK (status IN ('todo', 'done', 'backlog')),
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
                        """)

    # таблица с отчётом
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS completed_tasks_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
                        """)

    # таблица с идеями
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
                        """)

    # Таблица сесии
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                started_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            )
                            """)

    # Таблица сообшений сесии
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    original_content TEXT NOT NULL,
                    processed_content  TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                )
                                """)

    conn.commit()


def add_project(conn: sqlite3.Connection, name: str, path: str) -> int:
    """Функция для добавления проекта, возвращает id проекта или -1 при ошибке"""
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO projects (name, path) VALUES (?, ?)", (name, path))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        return -1
    return cursor.lastrowid


def add_task(
    conn: sqlite3.Connection,
    project_id: int,
    title: str,
    task_type: str,
    parent_id: int | None = None,
) -> int:
    """Функция для добавления задачи, возвращает id задачи"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO tasks (project_id, title, task_type, parent_id) VALUES (?, ?, ?, ?)",
            (project_id, title, task_type, parent_id),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        return -1
    return cursor.lastrowid


def add_completed_task_log(
    conn: sqlite3.Connection, task_id: int, project_id: int, title: str
) -> int:
    """Функция для добавления отчёта, возвращает id отчёта"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO completed_tasks_log (task_id, project_id, title) VALUES (?, ?, ?)",
            (task_id, project_id, title),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        return -1
    return cursor.lastrowid


def delete_project(conn: sqlite3.Connection, project_id: int) -> bool:
    """Удаляет проект. Возвращает True, если проект существовал и был удалён."""
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        return False
    return cursor.rowcount > 0


def delete_task(conn: sqlite3.Connection, task_id: int) -> bool:
    """Удаляет задачу. Возвращает True, если задача существовала и была удалена."""
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        return False
    return cursor.rowcount > 0


def add_idea(conn: sqlite3.Connection, project_id: int, text: str) -> int:
    """Функция для добавления идеи, возвращает id идеи"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO ideas (project_id, text) VALUES (?, ?)",
            (project_id, text),
        )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        return -1
    return cursor.lastrowid


def get_projects(conn: sqlite3.Connection) -> list[dict]:
    """Возвращает список проектов."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, path FROM projects")
    return [dict(row) for row in cursor.fetchall()]


def get_ideas(conn: sqlite3.Connection) -> list[dict]:
    """Возвращает список идей."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, created_at, project_id, text FROM ideas")
    return [dict(row) for row in cursor.fetchall()]


def start_session(conn: sqlite3.Connection, project_id: int) -> int:
    """Очишяет старую версию, сессии"""
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM sessions")
        cursor.execute(
            "INSERT INTO sessions (project_id) VALUES (?)",
            (project_id,),
        )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        return -1
    return cursor.lastrowid


def end_session(conn: sqlite3.Connection) -> bool:
    """Заканчивает сессию"""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions")
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        return False


def add_session_message(
    conn: sqlite3.Connection, session_id: int, original_content: str
) -> int:
    """Функция для сообщения сесии, возвращает id сообщения"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO session_messages (session_id, original_content) VALUES (?, ?)",
            (session_id, original_content),
        )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        return -1
    return cursor.lastrowid


def update_processed_content(
    conn: sqlite3.Connection, message_id: int, processed_content: str
) -> bool:
    """Функция добовления отредактированного сообщения для рефлексии"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE session_messages SET processed_content = ? WHERE id = ?",
            (
                processed_content,
                message_id,
            ),
        )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        return False


def get_session_messages(conn: sqlite3.Connection, session_id: int) -> list[dict]:
    """Выводит список всех сообшении за сессию"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, original_content, processed_content, created_at "
        "FROM session_messages "
        "WHERE session_id = ? "
        "ORDER BY created_at",
        (session_id,),
    )
    return [dict(row) for row in cursor.fetchall()]
