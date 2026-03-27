from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.environment import TicketTriageEnv
from src.models import Action
from src.tasks import list_tasks

app = FastAPI(title="Customer Support Ticket Triage")
env = TicketTriageEnv()


class ResetRequest(BaseModel):
    task_id: str | None = None


@app.get("/")
def root() -> dict:
    return {
        "name": "customer-support-ticket-triage",
        "status": "ok",
        "endpoints": [
            "/health",
            "/tasks",
            "/reset",
            "/step",
            "/state",
            "/grader",
            "/baseline",
        ],
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks")
def tasks() -> dict:
    task_items = []
    for task in list_tasks():
        task_items.append(
            {
                "task_id": task.task_id,
                "difficulty": task.difficulty.value,
                "title": task.title,
                "description": task.description,
                "max_turns": task.max_turns,
            }
        )

    return {
        "tasks": task_items,
        "action_schema": Action.model_json_schema(),
    }


@app.post("/reset")
def reset(request: ResetRequest) -> dict:
    try:
        observation = env.reset(request.task_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return observation.model_dump()


@app.post("/step")
def step(action: Action) -> dict:
    try:
        result = env.step(action)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result.model_dump()


@app.get("/state")
def state() -> dict:
    try:
        return env.state().model_dump()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/grader")
def grader() -> dict:
    try:
        return env.grader()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/baseline")
def baseline() -> dict:
    try:
        from baseline.run_baseline import run_baseline

        return run_baseline()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
