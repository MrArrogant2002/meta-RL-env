from __future__ import annotations

from src.models import GraderResult, SuccessCriteria, TaskDefinition, TicketRecord


BASE_WEIGHTS = {
    "category": 0.20,
    "priority": 0.20,
    "queue": 0.20,
    "response_template": 0.15,
    "escalated": 0.10,
    "resolved": 0.05,
    "required_tags": 0.10,
}


def _score_tags(ticket: TicketRecord, criteria: SuccessCriteria) -> tuple[float, list[str]]:
    if not criteria.required_tags:
        return 1.0, []

    missing = [tag for tag in criteria.required_tags if tag not in ticket.tags]
    score = (len(criteria.required_tags) - len(missing)) / len(criteria.required_tags)
    return score, [f"missing_tag:{tag}" for tag in missing]


def grade_ticket(task: TaskDefinition, ticket: TicketRecord) -> GraderResult:
    components: dict[str, float] = {}
    missing: list[str] = []
    criteria = task.success_criteria

    for field_name in ("category", "priority", "queue", "response_template"):
        expected = getattr(criteria, field_name)
        actual = getattr(ticket, field_name)
        match = 1.0 if actual == expected else 0.0
        components[field_name] = match
        if not match:
            missing.append(f"{field_name}:expected={expected}:actual={actual}")

    for field_name in ("escalated", "resolved"):
        expected = getattr(criteria, field_name)
        actual = getattr(ticket, field_name)
        match = 1.0 if actual == expected else 0.0
        components[field_name] = match
        if not match:
            missing.append(f"{field_name}:expected={expected}:actual={actual}")

    tag_score, tag_missing = _score_tags(ticket, criteria)
    components["required_tags"] = tag_score
    missing.extend(tag_missing)

    weighted_score = 0.0
    total_weight = 0.0
    for name, weight in BASE_WEIGHTS.items():
        weighted_score += components[name] * weight
        total_weight += weight

    score = round(weighted_score / total_weight, 4)
    return GraderResult(
        task_id=task.task_id,
        score=score,
        components=components,
        missing_or_incorrect=missing,
    )

