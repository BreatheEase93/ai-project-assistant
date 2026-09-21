import os
from pathlib import Path

import pathspec


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
        ".git/",
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


def compile_ignore_spec(patterns: list[str]) -> pathspec.PathSpec:
    """Функция фильтрации списка, на основе игнорируесых файлов"""
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)


def build_project_tree(project_path: Path, spec: pathspec.PathSpec) -> list[Path]:
    """Функция фильтрации папок и файлов на основе игнорироемого файла"""

    result: list[Path] = []
    root_str = str(project_path)

    for dirpath, dirnames, filenames in os.walk(root_str, topdown=True):
        rel_dir = Path(dirpath).relative_to(project_path)

        dirnames[:] = [
            d for d in dirnames if not spec.match_file((rel_dir / d).as_posix() + "/")
        ]

        for name in filenames:
            rel_file = rel_dir / name
            if not spec.match_file(rel_file.as_posix()):
                result.append(project_path / rel_file)

    return result


from pathlib import Path


def format_tree_to_string(files: list[Path], project_path: Path) -> str:
    """Строит строковое представление дерева проекта в стиле команды tree."""
    tree: dict = {}
    for path in files:
        if path == project_path:
            continue
        rel = path.relative_to(project_path)
        node = tree
        parts = rel.parts
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                node.setdefault(part, None)
            else:
                node = node.setdefault(part, {})
                if node is None:
                    raise ValueError(f"Конфликт: {part} — и файл, и папка")

    lines: list[str] = [project_path.name + "/"]

    def sort_key(item: tuple[str, dict | None]) -> tuple[bool, str]:
        name, subtree = item
        return (subtree is None, name.lower())

    def render(node: dict, prefix: str = "") -> None:
        items = sorted(node.items(), key=sort_key)
        for i, (name, subtree) in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            suffix = "/" if subtree is not None else ""
            lines.append(prefix + connector + name + suffix)
            if subtree:
                extension = "    " if is_last else "│   "
                render(subtree, prefix + extension)

    render(tree)
    return "\n".join(lines)
