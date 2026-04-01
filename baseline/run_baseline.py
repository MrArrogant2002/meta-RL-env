from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from openai import APIConnectionError, AuthenticationError, OpenAI, RateLimitError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.environment import TicketTriageEnv
from src.models import Action, ActionType, Observation
from src.tasks import list_tasks


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1])
    return json.loads(text)


def _build_prompt(observation: Observation) -> str:
    ticket = observation.current_ticket
    return f"""
You are a customer support triage assistant.
Return JSON only with this schema:
{{
  "category": "...",
  "priority": "...",
  "queue": "...",
  "response_template": "...",
  "tags": ["..."],
  "escalated": true_or_false,
  "resolved": true_or_false
}}

Allowed action types in the environment:
- set_category
- set_priority
- set_queue
- set_response_template
- add_tag
- mark_escalated
- mark_resolved
- finish

Ticket:
- task_id: {observation.task_id}
- difficulty: {observation.difficulty.value}
- subject: {ticket.subject}
- body: {ticket.body}
- channel: {ticket.channel}
- customer_tier: {ticket.customer_tier}
- sentiment: {ticket.sentiment}
""".strip()


def _plan_actions(observation: Observation, decision: dict[str, Any]) -> list[Action]:
    ticket_id = observation.current_ticket.ticket_id
    actions = [
        Action(action_type=ActionType.SET_CATEGORY, ticket_id=ticket_id, value=decision["category"]),
        Action(action_type=ActionType.SET_PRIORITY, ticket_id=ticket_id, value=decision["priority"]),
        Action(action_type=ActionType.SET_QUEUE, ticket_id=ticket_id, value=decision["queue"]),
        Action(
            action_type=ActionType.SET_RESPONSE_TEMPLATE,
            ticket_id=ticket_id,
            value=decision["response_template"],
        ),
    ]

    for tag in decision.get("tags", []):
        actions.append(Action(action_type=ActionType.ADD_TAG, ticket_id=ticket_id, value=tag))

    if decision.get("escalated"):
        actions.append(Action(action_type=ActionType.MARK_ESCALATED, ticket_id=ticket_id))

    if decision.get("resolved"):
        actions.append(Action(action_type=ActionType.MARK_RESOLVED, ticket_id=ticket_id))

    actions.append(Action(action_type=ActionType.FINISH, ticket_id=ticket_id))
    return actions


def _run_with_llm(client: "OpenAI") -> list[dict[str, Any]]:
    env = TicketTriageEnv()
    results: list[dict[str, Any]] = []
    for task in list_tasks():
        observation = env.reset(task.task_id)
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You output strict JSON only. Do not include explanations.",
                },
                {
                    "role": "user",
                    "content": _build_prompt(observation),
                },
            ],
        )
        content = response.choices[0].message.content or "{}"
        decision = _extract_json(content)

        last_result = None
        for action in _plan_actions(observation, decision):
            last_result = env.step(action)
            if last_result.done:
                break

        grader = env.grader()
        results.append(
            {
                "task_id": task.task_id,
                "difficulty": task.difficulty.value,
                "grader_score": grader["score"],
                "components": grader["components"],
                "missing_or_incorrect": grader["missing_or_incorrect"],
                "final_reward": last_result.reward.value if last_result else 0.0,
            }
        )
    return results


def _run_rule_based() -> list[dict[str, Any]]:
    from baseline.rule_based import plan_actions as rule_plan_actions

    env = TicketTriageEnv()
    results: list[dict[str, Any]] = []
    for task in list_tasks():
        observation = env.reset(task.task_id)
        last_result = None
        for action in rule_plan_actions(observation):
            last_result = env.step(action)
            if last_result.done:
                break

        grader = env.grader()
        results.append(
            {
                "task_id": task.task_id,
                "difficulty": task.difficulty.value,
                "grader_score": grader["score"],
                "components": grader["components"],
                "missing_or_incorrect": grader["missing_or_incorrect"],
                "final_reward": last_result.reward.value if last_result else 0.0,
            }
        )
    return results


def run_baseline() -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")

    try:
        if api_key:
            client = OpenAI(api_key=api_key)
            results = _run_with_llm(client)
            model = DEFAULT_MODEL
        else:
            results = _run_rule_based()
            model = "rule_based"
    except AuthenticationError as exc:
        raise RuntimeError(
            "OpenAI authentication failed. Check OPENAI_API_KEY in your environment."
        ) from exc
    except RateLimitError as exc:
        raise RuntimeError(
            "OpenAI API quota is unavailable for this key. Add billing or use a funded key, "
            "then rerun `python3 baseline/run_baseline.py`."
        ) from exc
    except APIConnectionError as exc:
        raise RuntimeError(
            "OpenAI API connection failed. Check internet access and try again."
        ) from exc

    overall = round(sum(item["grader_score"] for item in results) / len(results), 4)
    return {"model": model, "results": results, "overall_score": overall}


if __name__ == "__main__":
    print(json.dumps(run_baseline(), indent=2))
