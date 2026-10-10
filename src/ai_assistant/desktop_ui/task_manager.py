import subprocess
from pathlib import Path


def get_git_status(project_path: Path) -> list[str]:
    """Функция возврашае все изминения в гит статусе"""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=project_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ["Git не инициализирован"]
    output = result.stdout.strip()
    if not output:
        return []
    return output.split("\n")


def get_current_branch(project_path: Path) -> str:
    """Функция возврашает текущию ветку в гит"""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=project_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def can_close_task(project_path: Path) -> tuple[bool, str]:
    """Функция проверяет возможность закрытия задачи"""
    status = get_git_status(project_path)
    if status == ["Git не инициализирован"]:
        return (False, "Git не инициализирован")
    if status:
        return (False, "Изминения в Git не сохранены")
    branch = get_current_branch(project_path)
    if not branch:
        return (False, "Detached HEAD")
    if branch in ("main", "master"):
        return (False, f"Нельзя выполнять задачи в {branch}")
    return (True, "Всё ОК!")
