from __future__ import annotations

from src.models import Reward


def compute_reward(
    *,
    previous_score: float,
    new_score: float,
    done: bool,
    invalid_action: bool = False,
    repeated_action: bool = False,
    early_finish: bool = False,
) -> Reward:
    components: dict[str, float] = {
        "progress": round(new_score - previous_score, 4),
        "invalid_action_penalty": -0.10 if invalid_action else 0.0,
        "repeated_action_penalty": -0.03 if repeated_action else 0.0,
        "early_finish_penalty": -0.15 if early_finish else 0.0,
        "completion_bonus": round(new_score * 0.20, 4) if done else 0.0,
    }

    value = round(sum(components.values()), 4)
    rationale = (
        "Reward is based on grader improvement, penalties for low-quality actions, "
        "and a small completion bonus when the episode ends."
    )
    return Reward(value=value, components=components, rationale=rationale)

