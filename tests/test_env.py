from src.environment import TicketTriageEnv
from src.models import Action, ActionType


def test_reset_returns_expected_task() -> None:
    env = TicketTriageEnv()
    observation = env.reset("refund_status_easy")

    assert observation.task_id == "refund_status_easy"
    assert observation.current_ticket.ticket_id == "TKT-1001"
    assert observation.turn == 0


def test_step_updates_ticket_state() -> None:
    env = TicketTriageEnv()
    observation = env.reset("refund_status_easy")

    result = env.step(
        Action(
            action_type=ActionType.SET_CATEGORY,
            ticket_id=observation.current_ticket.ticket_id,
            value="billing_refund",
        )
    )

    assert result.observation.current_ticket.category == "billing_refund"
    assert result.reward.value >= 0
