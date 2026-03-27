from src.graders import grade_ticket
from src.tasks import get_task


def test_grader_returns_valid_score_range() -> None:
    task = get_task("refund_status_easy")
    result = grade_ticket(task, task.starting_ticket)

    assert 0.0 <= result.score <= 1.0


def test_grader_scores_perfect_ticket_as_one() -> None:
    task = get_task("account_takeover_medium")
    perfect_ticket = task.starting_ticket.model_copy(deep=True)
    perfect_ticket.category = task.success_criteria.category
    perfect_ticket.priority = task.success_criteria.priority
    perfect_ticket.queue = task.success_criteria.queue
    perfect_ticket.response_template = task.success_criteria.response_template
    perfect_ticket.escalated = task.success_criteria.escalated
    perfect_ticket.resolved = task.success_criteria.resolved
    perfect_ticket.tags = list(task.success_criteria.required_tags)

    result = grade_ticket(task, perfect_ticket)

    assert result.score == 1.0
