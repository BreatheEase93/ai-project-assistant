import re
import shutil
import subprocess
from pathlib import Path


def create_project_skeleton(project_path: Path, project_name: str) -> bool:
    """Создаёт каркас Python-проекта: папку, git-репозиторий, Poetry-проект."""
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


def copy_templates(project_path: Path, project_name: str) -> bool:
    """Копирует шаблоны в папку проекта."""
    try:
        project_path = Path(project_path)

        templates_dir = Path(__file__).resolve().parent.parent / "templates" / "project"

        # 1. .gitignore
        shutil.copy(templates_dir / "gitignore", project_path / ".gitignore")

        # 2. README.md — с подстановкой имени проекта
        readme = (templates_dir / "README.md").read_text(encoding="utf-8")
        readme = re.sub(r"\bPROJECT_NAME\b", project_name, readme)
        (project_path / "README.md").write_text(readme, encoding="utf-8")

        # 3. ruff.toml
        shutil.copy(templates_dir / "ruff.toml", project_path / "ruff.toml")

        # 4. VS Code settings -> .vscode/settings.json
        vscode_dir = project_path / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        shutil.copy(
            templates_dir / "vscode_settings.json", vscode_dir / "settings.json"
        )

        return True

    except Exception as e:
        print(f"Ошибка при копировании шаблонов: {e}")
        return False
