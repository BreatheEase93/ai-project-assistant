from pathlib import Path


def load_gitignore_rules(project_path: Path) -> list[str] | None:
    """Функция ищет .gitignore, и возврващяет список строк"""
    try:
        p = project_path / ".gitignore"
        if not p.is_file():
            return None
        my_list = p.read_text(encoding="utf-8").splitlines()
        rezult = []

        for a in my_list:
            a = a.strip()
            if a != "" and a[0] != "#":
                rezult.append(a)
        return rezult
    except Exception as e:
        print(f"Ошибка при чтении {p}: {type(e).__name__}: {e}")
        return None


def collect_all_ignores(ignore: list[str] | None) -> list[str]:
    """Функция котроая выдет игнорируемые файлы"""
    default_ignore = [
        ".venv/",
        "venv/",
        "env/",
        "ENV/",
        "active_env/",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache/",
        ".ruff_cache/",
        ".mypy_cache/",
        ".ipynb_checkpoints/",
        "*.sqlite3",
        "*.db",
        "*.local.db",
        ".env",
        ".env.local",
        "*.env",
        ".DS_Store",
        "Thumbs.db",
        ".ai_tasks.json",
    ]
    return default_ignore + (ignore or [])
