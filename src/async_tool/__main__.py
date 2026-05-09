import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import TypedDict


class TaskItem(TypedDict):
    id: int
    delay: float
    good: bool


class TaskResult(TypedDict, total=False):
    id: int
    status: str
    message: str


# provided function, do not modify
async def process_item(item: TaskItem) -> TaskResult:
    await asyncio.sleep(item["delay"])
    if not item["good"]:
        raise ValueError(f"Task {item['id']} failed")
    return {
        "id": item["id"],
        "status": "done",
    }


def setup_logging(level: str) -> None:
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=getattr(logging, level)
    )


def load_tasks(path: Path) -> list[TaskItem]:
    with path.open() as f:
        data: list[TaskItem] = json.load(f)
        return data


# run tasks one by one
async def run_sync(tasks: list[TaskItem], continue_on_error: bool) -> list[TaskResult]:
    results = []
    for task in tasks:
        logging.info(f"Starting task {task['id']}")
        try:
            result = await process_item(task)
            logging.info(f"Done task {task['id']}")
            results.append(result)
        except ValueError as e:
            if continue_on_error:
                results.append({
                    "id": task["id"],
                    "status": "error",
                    "message": str(e)
                })
            else:
                raise
    return results


# helper for async mode
async def safe_process_async(task: TaskItem, continue_on_error: bool) -> TaskResult:
    logging.info(f"Starting task {task['id']}")
    try:
        result = await process_item(task)
        logging.info(f"Done task {task['id']}")
        return result
    except ValueError as e:
        if continue_on_error:
            return {
                "id": task["id"],
                "status": "error",
                "message": str(e)
            }
        raise


# run all tasks at the same time
async def run_async(tasks: list[TaskItem], continue_on_error: bool) -> list[TaskResult]:
    coroutines = [safe_process_async(t, continue_on_error) for t in tasks]
    return list(await asyncio.gather(*coroutines))


# helper for limited mode
async def safe_process_limited(
    task: TaskItem,
    semaphore: asyncio.Semaphore,
    continue_on_error: bool
) -> TaskResult:
    async with semaphore:
        logging.info(f"Starting task {task['id']}")
        try:
            result = await process_item(task)
            logging.info(f"Done task {task['id']}")
            return result
        except ValueError as e:
            if continue_on_error:
                return {
                    "id": task["id"],
                    "status": "error",
                    "message": str(e)
                }
            raise


# run tasks with concurrency limit
async def run_limited(
    tasks: list[TaskItem],
    limit: int,
    continue_on_error: bool
) -> list[TaskResult]:
    semaphore = asyncio.Semaphore(limit)
    coroutines = [safe_process_limited(t, semaphore, continue_on_error) for t in tasks]
    return list(await asyncio.gather(*coroutines))


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--mode", choices=["sync", "async", "limited"], default="sync")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="WARNING"
    )

    args = parser.parse_args()
    setup_logging(args.log_level)
    tasks = load_tasks(args.input)

    try:
        if args.mode == "sync":
            results = await run_sync(tasks, args.continue_on_error)
        elif args.mode == "async":
            results = await run_async(tasks, args.continue_on_error)
        else:
            results = await run_limited(tasks, args.limit, args.continue_on_error)
    except ValueError as e:
        logging.error(str(e))
        sys.exit(1)

    print(json.dumps(results, indent=2))


asyncio.run(main())
