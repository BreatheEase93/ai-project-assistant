import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[3] / ".env")


def register_project_on_server(name: str, path: str) -> bool:
    """Регистрирует проект на сервере через POST /projects."""
    server_url = os.getenv("SERVER_URL")

    if not server_url:
        print("SERVER_URL не задан в .env")
        return False

    url = f"{server_url}/projects"
    payload = {"name": name, "path": path}

    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.post(url, json=payload)

        if response.is_success:
            return True

        print(f"Сервер вернул ошибку: {response.status_code} {response.text}")
        return False

    except Exception as e:
        print(f"Ошибка при регистрации проекта: {e}")
        return False
