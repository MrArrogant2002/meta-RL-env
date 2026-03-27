# Round 1 Build Plan

## Objective

Build a complete OpenEnv environment for a real-world task that:

- passes automated validation
- avoids all disqualification conditions
- produces reproducible baseline scores
- is ready to deploy as a Hugging Face Space

This document turns the Round 1 requirements into an execution plan and a qualification checklist.

## Qualification Gates

These are the non-negotiable items. Missing any of them can fail or disqualify the submission.

| Requirement | What must exist | How it will be checked |
| --- | --- | --- |
| Real-world environment | A task humans actually do, not a game or toy | Human review + environment behavior |
| OpenEnv compliance | Typed `Observation`, `Action`, `Reward` models, `step()`, `reset()`, `state()`, `openenv.yaml` | `openenv validate` |
| Minimum 3 tasks | Easy, medium, hard tasks with deterministic graders | Task enumeration + grader execution |
| Meaningful rewards | Partial progress rewards and penalties for bad behavior | Review of reward behavior during episodes |
| Baseline inference | Script using OpenAI API, `OPENAI_API_KEY`, reproducible scores | Baseline run in validation |
| Dockerized app | Working `Dockerfile` that builds and runs cleanly | `docker build` + `docker run` |
| HF Space deployment | Containerized Space responding correctly | Automated ping to Space URL |
| Documentation | README with all required sections | Repo review |
| Extra endpoints | `/baseline`, `/grader`, `/tasks` | Endpoint checks |

## What To Build

### 1. Choose the right environment

Pick one real-world workflow with:

- clear state that can be represented as structured observations
- actions that are realistic and safe to simulate
- objective task completion criteria
- room for partial progress rewards
- enough complexity to support easy, medium, and hard tasks

Good domains from the prompt:

- email triage
- code review
- data cleaning
- scheduling
- customer support
- content moderation

Best selection criteria:

- deterministic grading is possible
- outcomes are measurable
- multi-step behavior matters
- the task is not trivially solved in one action
- it feels useful for evaluating real agents

### 2. Define the environment contract

Implement the standard OpenEnv interface:

- `reset() -> Observation`
- `step(action: Action) -> (Observation, Reward, done, info)`
- `state() -> State`

Required typed models:

- `Observation`
- `Action`
- `Reward`
- internal `State` model or equivalent typed state object

The action and observation spaces should be explicit, minimal, and documented.

### 3. Create at least 3 tasks

Each task must include:

- a concrete objective
- a starting state or scenario generator
- difficulty label: easy, medium, hard
- a deterministic grader returning a score from `0.0` to `1.0`
- clear completion conditions

Task design rules:

- easy task should validate core functionality
- medium task should require multi-step planning
- hard task should challenge strong models and require precision
- graders must not always return the same score
- graders should evaluate outcome quality, not just episode length

### 4. Design a meaningful reward function

Reward shaping should:

- give positive signal for partial progress
- reward correct intermediate actions
- penalize loops, invalid actions, or destructive actions
- align with the final grader
- avoid being purely sparse and binary

Recommended reward structure:

- task progress reward
- correctness reward
- efficiency penalty for wasted steps
- safety penalty for bad actions
- final completion bonus tied to grader output

### 5. Expose required endpoints

In addition to the standard environment endpoints, expose:

- `/baseline`: runs the baseline inference script and returns scores for all tasks
- `/grader`: returns the final grader score for a completed episode
- `/tasks`: returns the task list and action schema

`/tasks` should include:

- task ids
- task descriptions
- difficulty labels
- action fields and required types

### 6. Package for deployment

The repo must include:

- working `Dockerfile`
- dependency manifest
- app entrypoint
- `openenv.yaml`
- README

The container must start cleanly and serve the environment in a Hugging Face Space.

## Recommended Repo Structure

Use a layout close to this:

```text
.
├── README.md
├── Dockerfile
├── openenv.yaml
├── requirements.txt
├── app.py
├── src/
│   ├── environment.py
│   ├── models.py
│   ├── tasks.py
│   ├── graders.py
│   ├── rewards.py
│   └── api.py
├── baseline/
│   └── run_baseline.py
├── scripts/
│   └── validate_round1.sh
└── tests/
    ├── test_env.py
    ├── test_graders.py
    └── test_api.py
```

Exact file names can vary, but these responsibilities must exist.

## Execution Plan

### Phase 1. Lock the problem scope

Deliverables:

- one-paragraph environment description
- chosen real-world domain
- action schema
- observation schema
- episode boundary rules
- list of 3 tasks

Exit criteria:

- the team can explain why the task is realistic
- each task can be graded deterministically
- the hard task is meaningfully harder than the easy task

### Phase 2. Implement the environment core

Build:

- typed Pydantic models
- environment state container
- `reset()`
- `step()`
- `state()`
- task loading or scenario generation

Exit criteria:

- `reset()` always returns a clean initial state
- `step()` updates state predictably
- `state()` reflects current internal state
- all models are typed and serializable

### Phase 3. Implement tasks and graders

Build:

- easy, medium, hard tasks
- deterministic graders
- score normalization to `0.0-1.0`
- final episode scoring logic

Exit criteria:

- every task can run start to finish
- graders produce different scores for better vs worse trajectories
- grading is stable across repeated runs

### Phase 4. Implement reward shaping

Build:

- intermediate progress signals
- penalties for invalid or harmful actions
- completion rewards

Exit criteria:

- rewards change across the trajectory
- partial success receives partial credit
- reward does not encourage exploitative behavior

### Phase 5. Build service endpoints

Build:

- environment API
- `/tasks`
- `/grader`
- `/baseline`

Exit criteria:

- all endpoints return `200`
- endpoint payloads are structured and documented
- `/baseline` returns scores for all tasks

### Phase 6. Add baseline inference

Build:

- script using the OpenAI API client
- env var based auth with `OPENAI_API_KEY`
- fixed prompts and settings for reproducibility
- aggregate scoring output across all tasks

Exit criteria:

- baseline script runs without manual intervention
- output is reproducible enough for validation
- scores are reported clearly per task and overall

### Phase 7. Containerize and deploy

Build:

- working `Dockerfile`
- container startup command
- HF Space configuration

Exit criteria:

- `docker build` passes
- `docker run` starts the app successfully
- the HF Space responds to validation requests

### Phase 8. Documentation and submission prep

Build:

- README
- local validation script
- final submission checklist

Exit criteria:

- README covers every required section
- validator passes locally
- no disqualification condition is still open

## README Requirements

The README must include:

- environment description
- motivation and real-world value
- action space definition
- observation space definition
- task descriptions and difficulty progression
- setup instructions
- usage instructions
- baseline scoring results
- deployment notes if needed

## openenv.yaml Requirements

Ensure `openenv.yaml` includes:

- environment metadata
- environment name and description
- action and observation model references if required by the framework
- task metadata
- runtime configuration needed by OpenEnv

Before submission, verify it passes:

```bash
openenv validate
```

## Baseline Script Requirements

The baseline script must:

- use the OpenAI API client
- read the API key from `OPENAI_API_KEY`
- run all 3 tasks
- output task-level and aggregate scores
- be reproducible
- complete without manual input

Recommended output:

- task id
- difficulty
- episode score
- final grader score
- overall mean score

## Local Validation Commands

Run these before submission:

```bash
openenv validate
docker build -t round1-openenv .
docker run -p 7860:7860 round1-openenv
```

Then verify endpoints:

```bash
curl http://localhost:7860/tasks
curl http://localhost:7860/baseline
curl http://localhost:7860/grader
```

Also run:

```bash
python baseline/run_baseline.py
```

If available, run the official pre-submission validator as the final gate.

## Suggested Test Coverage

Minimum tests:

- `reset()` returns clean initial state
- `step()` handles valid actions
- invalid actions are rejected or penalized correctly
- `state()` matches internal state
- each grader returns values in `0.0-1.0`
- tasks differ by difficulty and expected behavior
- baseline endpoint executes successfully
- task listing endpoint returns correct action schema

## Disqualification Risks

Avoid these explicitly:

- environment does not deploy
- Space does not return `200`
- `Dockerfile` fails to build
- `openenv validate` fails
- no baseline script
- baseline script depends on manual edits or hidden local setup
- fewer than 3 tasks
- graders always return the same score
- environment is a toy or thin wrapper around an existing trivial environment
- plagiarism or superficial modification of an existing submission

## Scoring Strategy

To maximize the judged score, optimize for these:

### Real-world utility

- choose a domain people genuinely care about
- make the simulation believable
- expose realistic constraints and tradeoffs

### Task and grader quality

- make goals precise
- use deterministic graders
- ensure the hard task tests real reasoning, not randomness

### Environment design

- keep state transitions clean
- reward partial progress
- define sensible episode boundaries

### Code quality and compliance

- keep models typed and documented
- keep the project easy to validate and run
- make Docker and baseline execution boring and reliable

### Creativity and novelty

- choose a domain not already overused
- add interesting mechanics without making grading ambiguous

## Recommended Definition Of Done

Round 1 is ready only when all of the following are true:

- `openenv validate` passes
- at least 3 tasks exist
- all graders return values from `0.0` to `1.0`
- baseline script runs successfully with `OPENAI_API_KEY`
- `/tasks`, `/grader`, and `/baseline` respond correctly
- Docker image builds and runs locally
- HF Space is deployable and healthy
- README is complete
- reward shaping is meaningful
- no disqualification criteria remain

## Final Submission Checklist

- choose and lock the environment domain
- implement typed OpenEnv models
- implement `reset()`, `step()`, and `state()`
- create easy, medium, hard tasks
- implement deterministic graders
- implement partial-progress rewards
- expose `/tasks`, `/grader`, and `/baseline`
- add `openenv.yaml`
- add baseline script using `OPENAI_API_KEY`
- add `Dockerfile`
- complete README
- run validation locally
- deploy to HF Space
- run final validation again after deployment

