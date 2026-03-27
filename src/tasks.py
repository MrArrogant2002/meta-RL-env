from __future__ import annotations

from src.models import Difficulty, SuccessCriteria, TaskDefinition, TicketRecord


TASKS: dict[str, TaskDefinition] = {
    "refund_status_easy": TaskDefinition(
        task_id="refund_status_easy",
        difficulty=Difficulty.EASY,
        title="Refund Status Follow-Up",
        description=(
            "A customer says their subscription was canceled and they still have "
            "not received the promised refund. The agent should route this to the "
            "billing support workflow without escalating unnecessarily."
        ),
        starting_ticket=TicketRecord(
            ticket_id="TKT-1001",
            customer_tier="standard",
            channel="email",
            subject="Refund still missing after my cancellation",
            body=(
                "I canceled my annual plan last week and support told me I would "
                "receive a refund within 3 to 5 business days. I still do not see "
                "it on my card. Can someone check what is happening?"
            ),
            sentiment="frustrated",
        ),
        success_criteria=SuccessCriteria(
            category="billing_refund",
            priority="medium",
            queue="billing_support",
            response_template="refund_status",
            escalated=False,
            resolved=False,
            required_tags=["refund"],
        ),
        max_turns=5,
    ),
    "account_takeover_medium": TaskDefinition(
        task_id="account_takeover_medium",
        difficulty=Difficulty.MEDIUM,
        title="Possible Account Takeover",
        description=(
            "A customer cannot access their account and reports suspicious login "
            "emails. The agent must recognize the security risk, prioritize it "
            "appropriately, and escalate to the right queue."
        ),
        starting_ticket=TicketRecord(
            ticket_id="TKT-2001",
            customer_tier="pro",
            channel="chat",
            subject="Locked out after strange login alerts",
            body=(
                "I received two login alerts from countries I have never visited "
                "and now I cannot get into my account. Please help immediately "
                "because I think someone got in."
            ),
            sentiment="angry",
        ),
        success_criteria=SuccessCriteria(
            category="account_security",
            priority="high",
            queue="trust_safety",
            response_template="security_verification",
            escalated=True,
            resolved=False,
            required_tags=["security", "account_access"],
        ),
        max_turns=6,
    ),
    "vip_duplicate_charge_hard": TaskDefinition(
        task_id="vip_duplicate_charge_hard",
        difficulty=Difficulty.HARD,
        title="VIP Duplicate Charge and Renewal Risk",
        description=(
            "A VIP customer reports duplicate charges right before a renewal "
            "decision and threatens to leave. The agent must triage with urgency, "
            "send the case to the executive billing queue, and preserve the "
            "commercial risk context."
        ),
        starting_ticket=TicketRecord(
            ticket_id="TKT-3001",
            customer_tier="vip",
            channel="email",
            subject="Duplicate charges before renewal meeting",
            body=(
                "We were charged twice for the same enterprise renewal and my CFO "
                "needs an answer before tomorrow morning's board review. If this "
                "is not handled today, we will reconsider the contract."
            ),
            sentiment="angry",
        ),
        success_criteria=SuccessCriteria(
            category="billing_dispute",
            priority="urgent",
            queue="executive_billing",
            response_template="vip_charge_acknowledgement",
            escalated=True,
            resolved=False,
            required_tags=["vip", "duplicate_charge", "renewal_risk"],
        ),
        max_turns=7,
    ),
}


def list_tasks() -> list[TaskDefinition]:
    return list(TASKS.values())


def get_task(task_id: str) -> TaskDefinition:
    try:
        return TASKS[task_id]
    except KeyError as exc:
        raise KeyError(f"Unknown task_id: {task_id}") from exc

