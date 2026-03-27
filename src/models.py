from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ActionType(str, Enum):
    SET_CATEGORY = "set_category"
    SET_PRIORITY = "set_priority"
    SET_QUEUE = "set_queue"
    SET_RESPONSE_TEMPLATE = "set_response_template"
    ADD_TAG = "add_tag"
    MARK_ESCALATED = "mark_escalated"
    MARK_RESOLVED = "mark_resolved"
    ADD_INTERNAL_NOTE = "add_internal_note"
    FINISH = "finish"


class TicketRecord(BaseModel):
    ticket_id: str
    customer_tier: str
    channel: str
    subject: str
    body: str
    sentiment: str
    tags: list[str] = Field(default_factory=list)
    category: str | None = None
    priority: str | None = None
    queue: str | None = None
    response_template: str | None = None
    escalated: bool = False
    resolved: bool = False
    internal_notes: list[str] = Field(default_factory=list)


class Action(BaseModel):
    action_type: ActionType
    ticket_id: str
    value: str | None = None


class Reward(BaseModel):
    value: float
    components: dict[str, float] = Field(default_factory=dict)
    rationale: str


class Observation(BaseModel):
    task_id: str
    difficulty: Difficulty
    turn: int
    max_turns: int
    current_ticket: TicketRecord
    required_outputs: list[str]
    allowed_actions: list[ActionType]
    action_history: list[Action] = Field(default_factory=list)


class SuccessCriteria(BaseModel):
    category: str
    priority: str
    queue: str
    response_template: str
    escalated: bool = False
    resolved: bool = False
    required_tags: list[str] = Field(default_factory=list)


class TaskDefinition(BaseModel):
    task_id: str
    difficulty: Difficulty
    title: str
    description: str
    starting_ticket: TicketRecord
    success_criteria: SuccessCriteria
    max_turns: int = 6


class GraderResult(BaseModel):
    task_id: str
    score: float
    components: dict[str, float]
    missing_or_incorrect: list[str]


class EnvironmentState(BaseModel):
    task_id: str
    difficulty: Difficulty
    turn: int
    max_turns: int
    ticket: TicketRecord
    action_history: list[Action] = Field(default_factory=list)
    done: bool = False
    last_reward: float = 0.0
    last_info: dict[str, Any] = Field(default_factory=dict)


class StepResult(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: dict[str, Any] = Field(default_factory=dict)

