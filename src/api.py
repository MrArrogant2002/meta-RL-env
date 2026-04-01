from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel, ValidationError

from src.environment import TicketTriageEnv
from src.models import Action, EnvironmentState, Observation
from src.tasks import list_tasks

APP_NAME = "customer-support-ticket-triage"
APP_DESCRIPTION = (
    "An OpenEnv-style environment that simulates customer support ticket triage."
)
APP_VERSION = "0.1.0"

app = FastAPI(
    title="Customer Support Ticket Triage",
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)
env = TicketTriageEnv()


class ResetRequest(BaseModel):
    task_id: str | None = None
    seed: int | None = None
    episode_id: str | None = None


class SimulationResponse(BaseModel):
    observation: dict[str, Any]
    reward: float | None = None
    done: bool = False


class MetadataResponse(BaseModel):
    name: str
    description: str
    version: str


class SchemaResponse(BaseModel):
    action: dict[str, Any]
    observation: dict[str, Any]
    state: dict[str, Any]


def _serialize_observation(
    observation: Observation,
    *,
    reward: float | None = None,
    done: bool = False,
) -> SimulationResponse:
    return SimulationResponse(
        observation=observation.model_dump(),
        reward=reward,
        done=done,
    )


def _get_metadata() -> MetadataResponse:
    return MetadataResponse(
        name=APP_NAME,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
    )


@app.get("/")
def root() -> dict:
    return {
        "name": APP_NAME,
        "status": "ok",
        "endpoints": [
            "/health",
            "/metadata",
            "/schema",
            "/mcp",
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
    return {"status": "healthy"}


@app.get("/metadata", response_model=MetadataResponse)
def metadata() -> MetadataResponse:
    return _get_metadata()


@app.get("/schema", response_model=SchemaResponse)
def schema() -> SchemaResponse:
    return SchemaResponse(
        action=Action.model_json_schema(),
        observation=Observation.model_json_schema(),
        state=EnvironmentState.model_json_schema(),
    )


@app.post("/mcp")
def mcp(request: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "error": {
            "code": -32601,
            "message": "MCP tool calls are not implemented for this environment.",
        },
    }


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


@app.post("/reset", response_model=SimulationResponse)
def reset(request: ResetRequest | None = Body(default=None)) -> SimulationResponse:
    if request is None:
        request = ResetRequest()
    try:
        observation = env.reset(request.task_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _serialize_observation(observation)


@app.post("/step", response_model=SimulationResponse)
def step(payload: dict[str, Any] = Body(...)) -> SimulationResponse:
    try:
        action_payload = payload.get("action", payload)
        action = Action.model_validate(action_payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc

    try:
        result = env.step(action)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _serialize_observation(
        result.observation,
        reward=result.reward.value,
        done=result.done,
    )


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
