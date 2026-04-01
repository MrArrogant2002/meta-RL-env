from __future__ import annotations

"""
Rule-based (no-LLM) baseline for Customer Support Ticket Triage.

Decisions are made entirely from keyword signals in the ticket text,
customer tier, and sentiment — no external API calls required.
"""

from src.models import Action, ActionType, Observation


def _decide(observation: Observation) -> dict:
    ticket = observation.current_ticket
    text = (ticket.subject + " " + ticket.body).lower()

    # ── Category ──────────────────────────────────────────────────────────
    if any(w in text for w in ["refund", "charge", "billing", "invoice", "payment"]):
        if "duplicate" in text or "dispute" in text or "charged twice" in text:
            category = "billing_dispute"
        else:
            category = "billing_refund"
    elif any(w in text for w in ["login", "locked", "account", "hack", "unauthorized", "security"]):
        category = "account_security"
    else:
        category = "general_inquiry"

    # ── Priority ──────────────────────────────────────────────────────────
    if ticket.customer_tier == "vip" or any(
        w in text for w in ["urgent", "board", "cfo", "executive", "critical"]
    ):
        priority = "urgent"
    elif ticket.sentiment == "angry" or category == "account_security" or ticket.customer_tier == "pro":
        priority = "high"
    elif ticket.sentiment == "frustrated":
        priority = "medium"
    else:
        priority = "low"

    # ── Queue ─────────────────────────────────────────────────────────────
    if category == "account_security":
        queue = "trust_safety"
    elif category == "billing_dispute" and ticket.customer_tier == "vip":
        queue = "executive_billing"
    elif "billing" in category:
        queue = "billing_support"
    else:
        queue = "general_support"

    # ── Response template ─────────────────────────────────────────────────
    if category == "billing_refund":
        response_template = "refund_status"
    elif category == "account_security":
        response_template = "security_verification"
    elif category == "billing_dispute" and ticket.customer_tier == "vip":
        response_template = "vip_charge_acknowledgement"
    else:
        response_template = "general_response"

    # ── Escalation ────────────────────────────────────────────────────────
    escalated = (
        category == "account_security"
        or (ticket.customer_tier == "vip" and ticket.sentiment == "angry")
        or priority == "urgent"
    )

    # ── Tags ──────────────────────────────────────────────────────────────
    tags: list[str] = []
    if "refund" in text:
        tags.append("refund")
    if category == "account_security" or any(w in text for w in ["login", "hack", "unauthorized"]):
        tags.append("security")
    if "account" in text and ("login" in text or "locked" in text):
        tags.append("account_access")
    if ticket.customer_tier == "vip":
        tags.append("vip")
    if "duplicate" in text or "charged twice" in text:
        tags.append("duplicate_charge")
    if "renewal" in text or "contract" in text:
        tags.append("renewal_risk")

    return {
        "category": category,
        "priority": priority,
        "queue": queue,
        "response_template": response_template,
        "tags": tags,
        "escalated": escalated,
        "resolved": False,
    }


def plan_actions(observation: Observation) -> list[Action]:
    decision = _decide(observation)
    ticket_id = observation.current_ticket.ticket_id

    # High-value actions first so they execute before max_turns is hit
    actions: list[Action] = [
        Action(action_type=ActionType.SET_CATEGORY, ticket_id=ticket_id, value=decision["category"]),
        Action(action_type=ActionType.SET_PRIORITY, ticket_id=ticket_id, value=decision["priority"]),
        Action(action_type=ActionType.SET_QUEUE, ticket_id=ticket_id, value=decision["queue"]),
        Action(
            action_type=ActionType.SET_RESPONSE_TEMPLATE,
            ticket_id=ticket_id,
            value=decision["response_template"],
        ),
    ]

    if decision["escalated"]:
        actions.append(Action(action_type=ActionType.MARK_ESCALATED, ticket_id=ticket_id))

    if decision["resolved"]:
        actions.append(Action(action_type=ActionType.MARK_RESOLVED, ticket_id=ticket_id))

    for tag in decision["tags"]:
        actions.append(Action(action_type=ActionType.ADD_TAG, ticket_id=ticket_id, value=tag))

    actions.append(Action(action_type=ActionType.FINISH, ticket_id=ticket_id))
    return actions
