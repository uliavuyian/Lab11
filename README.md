# Lab 11 — Async Batch Processor

A hands-on demonstration of how Python handles asynchronous execution — covering sequential vs concurrent task processing, semaphore-based concurrency control, and error handling strategies.

## Project Structure

```
Lab11/
├── README.md
├── requirements.txt
├── report/
│   └── answers.md
└── src/
    └── async_tool/
        └── __main__.py
```

## Requirements

Python 3.11+

## Environment Setup

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Program

```bash
python -m async_tool input.json [OPTIONS]
```

## Options

- `--mode sync|async|limited` — execution mode (default: `sync`)
- `--limit N` — concurrency limit for `limited` mode (default: `5`)
- `--continue-on-error` — continue processing if a task fails
- `--log-level DEBUG|INFO|WARNING|ERROR` — logging level (default: `WARNING`)

## Examples

```bash
# sequential
python -m async_tool input.json --mode sync

# all tasks at the same time
python -m async_tool input.json --mode async --continue-on-error

# max 3 tasks at the same time
python -m async_tool input.json --mode limited --limit 3
```

## Input Format

```json
[
  {"id": 1, "delay": 1, "good": true},
  {"id": 2, "delay": 2, "good": false},
  {"id": 3, "delay": 1, "good": true}
]
```

## Output Format

```json
[
  {"id": 1, "status": "done"},
  {"id": 2, "status": "error", "message": "Task 2 failed"},
  {"id": 3, "status": "done"}
]
```

## What the Program Does

The tool reads a JSON file with a list of tasks and processes them in the selected mode.

**sync** — tasks run one by one using `await` inside a loop.

**async** — all tasks run at the same time using `asyncio.gather`.

**limited** — tasks run concurrently but no more than `--limit` at a time, controlled by `asyncio.Semaphore`.

## Notes

- Output order always matches input order
- Each task produces exactly one result
- Without `--continue-on-error` the program stops on first failure and exits with non-zero code
```
