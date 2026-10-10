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
        return []
    output = result.stdout.strip()
    if not output:
        return []
    return output.split("\n")


def get_current_branch(project_path: Path) -> str:
    """Функция возврашает текещию ветку в гит"""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=project_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()
