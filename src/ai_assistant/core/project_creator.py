import subprocess
from pathlib import Path


def create_project_skeleton(project_path: Path, project_name: str) -> bool:
    """Функция для создания скилета"""
    try:
        project_path.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init"], cwd=project_path, check=True)
        subprocess.run(
            [
                "poetry",
                "init",
                "--no-interaction",
                "--python",
                "^3.12",
                "--name",
                project_name,
            ],
            cwd=project_path,
            check=True,
        )
        return True
    except Exception as e:
        print(e)
        return False
