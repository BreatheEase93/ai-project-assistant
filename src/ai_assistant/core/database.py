import sqlite3


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Функция для связи с базой данных получает на вход путь к базе,
    сортирует ответ как словарь, возвращает обект подключения"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    """Функция для создания таблицы, с проектами и задачами, а также отчетов"""
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
