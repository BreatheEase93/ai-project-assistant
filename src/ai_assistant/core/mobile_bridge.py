from pathlib import Path

from core.database import add_idea, get_db_connection, get_ideas, get_projects
from fastapi import FastAPI
from pydantic import BaseModel


DB_PATH = Path("assistant.db")

app = FastAPI()


class Idea(BaseModel):
    """Класс идеи"""

    project_id: int
    text: str


@app.get("/projects/")
async def list_project():
    conn = get_db_connection(DB_PATH)
    try:
        return get_projects(conn)
    finally:
        conn.close()


@app.get("/ideas/")
async def ideas():
    conn = get_db_connection(DB_PATH)
    try:
        return get_ideas(conn)
    finally:
        conn.close()


@app.post("/ideas/")
async def create_idea(idea: Idea):
    conn = get_db_connection(DB_PATH)
    try:
        new_id = add_idea(conn, idea.project_id, idea.text)
        return {"id": new_id, "status": "created"}
    finally:
        conn.close()
