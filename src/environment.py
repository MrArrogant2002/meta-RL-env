from __future__ import annotations

from copy import deepcopy

from src.graders import grade_ticket
from src.models import (
    Action,
    ActionType,
    EnvironmentState,
    Observation,
    StepResult,
)
from src.rewards import compute_reward
from src.tasks import get_task, list_tasks


class TicketTriageEnv:
    def __init__(self) -> None:
        self._state: EnvironmentState | None = None

    def reset(self, task_id: str | None = None) -> Observation:
        task = get_task(task_id or list_tasks()[0].task_id)
        self._state = EnvironmentState(
            task_id=task.task_id,
            difficulty=task.difficulty,
            turn=0,
            max_turns=task.max_turns,
            ticket=deepcopy(task.starting_ticket),
            action_history=[],
            done=False,
            last_reward=0.0,
            last_info={},
        )
        return self._build_observation()

    def step(self, action: Action) -> StepResult:
        if self._state is None:
            raise RuntimeError("Environment must be reset before step() is called.")
        if self._state.done:
            raise RuntimeError("Episode is already done. Call reset() to start a new one.")
        if action.ticket_id != self._state.ticket.ticket_id:
            raise ValueError(
                f"Ticket id mismatch. Expected {self._state.ticket.ticket_id}, got {action.ticket_id}."
            )

        task = get_task(self._state.task_id)
        previous_grade = grade_ticket(task, self._state.ticket)
        invalid_action = False
        repeated_action = bool(
            self._state.action_history
            and self._state.action_history[-1].action_type == action.action_type
            and self._state.action_history[-1].value == action.value
        )

        if action.action_type == ActionType.SET_CATEGORY and action.value:
            self._state.ticket.category = action.value
        elif action.action_type == ActionType.SET_PRIORITY and action.value:
            self._state.ticket.priority = action.value
        elif action.action_type == ActionType.SET_QUEUE and action.value:
            self._state.ticket.queue = action.value
        elif action.action_type == ActionType.SET_RESPONSE_TEMPLATE and action.value:
            self._state.ticket.response_template = action.value
        elif action.action_type == ActionType.ADD_TAG and action.value:
            if action.value not in self._state.ticket.tags:
                self._state.ticket.tags.append(action.value)
        elif action.action_type == ActionType.MARK_ESCALATED:
            self._state.ticket.escalated = True
        elif action.action_type == ActionType.MARK_RESOLVED:
            self._state.ticket.resolved = True
        elif action.action_type == ActionType.ADD_INTERNAL_NOTE and action.value:
            self._state.ticket.internal_notes.append(action.value)
        elif action.action_type == ActionType.FINISH:
            self._state.done = True
        else:
            invalid_action = True

        self._state.action_history.append(action)
        self._state.turn += 1

        if self._state.turn >= self._state.max_turns:
            self._state.done = True

        new_grade = grade_ticket(task, self._state.ticket)
        early_finish = action.action_type == ActionType.FINISH and new_grade.score < 1.0
        reward = compute_reward(
            previous_score=previous_grade.score,
            new_score=new_grade.score,
            done=self._state.done,
            invalid_action=invalid_action,
            repeated_action=repeated_action,
            early_finish=early_finish,
        )
        self._state.last_reward = reward.value
        self._state.last_info = {"grader": new_grade.model_dump()}

        return StepResult(
            observation=self._build_observation(),
            reward=reward,
            done=self._state.done,
            info=self._state.last_info,
        )

    def state(self) -> EnvironmentState:
        if self._state is None:
            raise RuntimeError("Environment has not been reset yet.")
        return self._state

    def grader(self) -> dict:
        state = self.state()
        task = get_task(state.task_id)
        return grade_ticket(task, state.ticket).model_dump()

    def _build_observation(self) -> Observation:
        if self._state is None:
            raise RuntimeError("Environment has not been reset yet.")

        return Observation(
            task_id=self._state.task_id,
            difficulty=self._state.difficulty,
            turn=self._state.turn,
            max_turns=self._state.max_turns,
            current_ticket=deepcopy(self._state.ticket),
            required_outputs=[
                "category",
                "priority",
                "queue",
                "response_template",
                "tags",
                "escalated",
                "resolved",
            ],
            allowed_actions=list(ActionType),
            action_history=list(self._state.action_history),
        )
