---
title: Customer Support Ticket Triage
emoji: "\ud83d\udce8"
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# Customer Support Ticket Triage OpenEnv

This project scaffolds an OpenEnv environment for customer support ticket triage. The environment simulates a real support workflow where an agent reads an incoming ticket, classifies it, sets priority, assigns the correct queue, adds tags, decides whether it needs escalation, and selects an appropriate response template.

The domain is strong for Round 1 because it is:

- clearly real-world
- easy to evaluate deterministically
- multi-step rather than single-shot
- rich enough for easy, medium, and hard tasks
- well-suited to partial-progress reward shaping

## Round 1 Fit

This environment is designed to satisfy the Round 1 requirements:

- typed `Observation`, `Action`, and `Reward` models
- standard `reset()`, `step()`, and `state()` API
- 3 graded tasks with difficulty progression
- deterministic grader returning `0.0` to `1.0`
- meaningful reward shaping from grader deltas
- baseline script using the OpenAI API client
- extra endpoints: `/tasks`, `/grader`, `/baseline`
- container-ready layout for Hugging Face Spaces

## Environment Concept

Each episode contains one support ticket scenario. The agent must complete the correct triage actions within a limited number of turns. The environment tracks state changes and scores the final ticket against an expected triage target.

The current scaffold focuses on triage decisions:

- set `category`
- set `priority`
- set `queue`
- set `response_template`
- add relevant tags
- mark escalation when required
- optionally mark resolved
- finish the episode

## Action Space

The scaffolded action types are:

- `set_category`
- `set_priority`
- `set_queue`
- `set_response_template`
- `add_tag`
- `mark_escalated`
- `mark_resolved`
- `add_internal_note`
- `finish`

The `Action` model is defined in [src/models.py](/home/eswarbalu/Desktop/mets-competition/src/models.py).

## Observation Space

Each observation includes:

- task id and difficulty
- current turn and max turns
- the current ticket snapshot
- required outputs for the episode
- allowed action list
- action history

The `Observation` model is defined in [src/models.py](/home/eswarbalu/Desktop/mets-competition/src/models.py).

## Tasks

The scaffold includes three deterministic tasks:

1. `refund_status_easy`
   - Straightforward billing refund triage
   - Expected outcome: billing category, medium priority, billing queue

2. `account_takeover_medium`
   - Account access and security triage
   - Expected outcome: security category, high priority, escalation

3. `vip_duplicate_charge_hard`
   - High-risk VIP billing dispute with churn risk
   - Expected outcome: urgent priority, executive billing queue, escalation, multiple tags

Task definitions live in [src/tasks.py](/home/eswarbalu/Desktop/mets-competition/src/tasks.py).

## Reward Design

The scaffold uses grader delta reward shaping:

- positive reward when the ticket moves closer to the target state
- penalty for invalid or wasteful actions
- penalty for finishing early with missing required decisions
- completion bonus tied to final grader score

This is implemented in [src/rewards.py](/home/eswarbalu/Desktop/mets-competition/src/rewards.py).

## Grader Design

The grader compares the final ticket state against expected outputs using weighted components:

- category
- priority
- queue
- response template
- escalation flag
- resolution flag
- required tags

The grader returns:

- final score from `0.0` to `1.0`
- component-level breakdown
- missing or incorrect fields

This is implemented in [src/graders.py](/home/eswarbalu/Desktop/mets-competition/src/graders.py).

## API Surface

The starter API exposes:

- `GET /health`
- `GET /tasks`
- `POST /reset`
- `POST /step`
- `GET /state`
- `GET /grader`
- `POST /baseline`

The FastAPI app lives in [src/api.py](/home/eswarbalu/Desktop/mets-competition/src/api.py).

## Project Layout

```text
.
├── README.md
├── Dockerfile
├── app.py
├── openenv.yaml
├── requirements.txt
├── baseline/
│   └── run_baseline.py
├── scripts/
│   └── validate_round1.sh
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── environment.py
│   ├── graders.py
│   ├── models.py
│   ├── rewards.py
│   └── tasks.py
└── tests/
    ├── test_api.py
    ├── test_env.py
    └── test_graders.py
```

## Quick Start

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the API locally:

```bash
uvicorn app:app --reload
```

Run tests:

```bash
python3 -m pytest
```

Run the baseline:

```bash
set -a
source .env
set +a
python3 baseline/run_baseline.py
```

## Validation Status

The following checks have already been verified locally in this repo:

- `openenv validate` passes
- `python3 -m pytest` passes
- `docker build -t mets-round1 .` passes
- `docker run -p 7860:7860 mets-round1` starts successfully
- `/health`, `/tasks`, `/reset`, and `/step` respond successfully in the container

## Baseline Scores

Baseline execution is implemented in [baseline/run_baseline.py](/home/eswarbalu/Desktop/mets-competition/baseline/run_baseline.py).

Before submission, run it with a funded OpenAI API key and record the results here:

| Task | Difficulty | Score |
| --- | --- | --- |
| `refund_status_easy` | easy | pending |
| `account_takeover_medium` | medium | pending |
| `vip_duplicate_charge_hard` | hard | pending |
| overall | mixed | pending |

If the script fails with `insufficient_quota`, the environment code is fine but the API project needs funded inference quota.

## Docker Usage

Build and run locally:

```bash
docker build -t mets-round1 .
docker run -p 7860:7860 mets-round1
```

Smoke test the container:

```bash
curl http://127.0.0.1:7860/health
curl http://127.0.0.1:7860/tasks
curl -X POST http://127.0.0.1:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id":"refund_status_easy"}'
curl -X POST http://127.0.0.1:7860/step \
  -H "Content-Type: application/json" \
  -d '{"action_type":"set_category","ticket_id":"TKT-1001","value":"billing_refund"}'
```

## Hugging Face Space Deployment

Create a new Hugging Face Space with:

- SDK: `Docker`
- Visibility: your choice
- Hardware: CPU is enough for this scaffold

Then push the repo:

```bash
git init
git add .
git commit -m "Initial OpenEnv ticket triage environment"
git branch -M main
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
git push -u origin main
```

After the Space is created, add these variables in the Space settings if needed:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`

Expected public endpoints:

- `/health`
- `/tasks`
- `/reset`
- `/step`
- `/grader`
- `/baseline`

## Final Submission Checklist

- `openenv validate` passes
- `python3 -m pytest` passes
- Docker image builds successfully
- Docker container starts and serves requests
- Hugging Face Space deploys successfully
- `/tasks`, `/grader`, and `/baseline` are reachable
- baseline inference completes with a funded API key
- README includes final baseline scores
- `openenv.yaml`, `pyproject.toml`, and `uv.lock` are committed

## Next Improvements

1. Expand task coverage from the starter scenarios into richer datasets or generators.
2. Improve the baseline prompt and action loop for stronger reproducibility.
3. Add more tests around invalid and adversarial actions.
4. Replace the placeholder baseline table with final measured scores before submission.
