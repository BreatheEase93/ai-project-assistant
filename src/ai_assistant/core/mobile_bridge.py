from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from .database import (
    add_idea,
    add_project,
    add_task,
    get_db_connection,
    get_ideas,
    get_projects,
)


DB_PATH = Path(__file__).resolve().parent.parent / "assistant.db"

app = FastAPI()

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


class Idea(BaseModel):
    """Класс идеи"""

    project_id: int
    text: str


@app.get("/ui", response_class=HTMLResponse)
async def ui(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/projects")
async def list_project():
    conn = get_db_connection(DB_PATH)
    try:
        return get_projects(conn)
    finally:
        conn.close()


@app.get("/ideas")
async def ideas():
    conn = get_db_connection(DB_PATH)
    try:
        return get_ideas(conn)
    finally:
        conn.close()


@app.post("/ideas")
async def create_idea(idea: Idea):
    conn = get_db_connection(DB_PATH)
    try:
        new_id = add_idea(conn, idea.project_id, idea.text)
        return {"id": new_id, "status": "created"}
    finally:
        conn.close()


class ProjectCreate(BaseModel):
    """Параметры создания нового проекта."""

    name: str = Field(..., min_length=1, max_length=100)
    path: str


@app.post("/projects")
async def create_project(project: ProjectCreate):
    conn = get_db_connection(DB_PATH)
    try:
        project_id = add_project(conn, project.name, project.path)
        if project_id == -1:
            raise HTTPException(
                status_code=400, detail="Project with this path already exists"
            )
        parent_id = add_task(conn, project_id, "Начало работы", "big_block")
        add_task(
            conn,
            project_id,
            "Установка зависимостей, подключение poetry",
            "subtask",
            parent_id,
        )
        add_task(conn, project_id, "Короткий README", "subtask", parent_id)
        add_task(conn, project_id, "Инициализация Docker", "subtask", parent_id)
        add_task(conn, project_id, "Первый коммит", "subtask", parent_id)

        return {"id": project_id, "status": "created"}
    finally:
        conn.close()
