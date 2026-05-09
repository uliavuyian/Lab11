# Lab 11 — Report

## 1. Why does `await` inside a loop lead to sequential execution?

When `await` is used inside a loop, the program waits for each task to fully complete before moving to the next one. Tasks are executed strictly one by one, with no overlap.

## 2. How does `asyncio.gather` change behavior?

`asyncio.gather` starts all tasks at the same time. While one task is waiting (for example during `asyncio.sleep`), other tasks are already running. This way all tasks overlap in time and the total execution time is much shorter than running them one by one.

## 3. What happens if one task fails in async mode without `--continue-on-error`?

If one task fails with an error, the program stops immediately and exits with a non-zero code. The results of all other tasks are ignored.

## 4. Why is a semaphore needed?

A semaphore limits the number of tasks that run at the same time. Without a semaphore `asyncio.gather` starts all tasks at once. If there are too many tasks, this can overload memory or an external resource.

## 5. When should async NOT be used?

Async should not be used in three cases. First — for heavy computations like math calculations, because the CPU is busy the whole time and async brings no advantage. Second — when the code uses blocking calls like `time.sleep` or `requests`, they block the entire event loop. Third — for simple short scripts where async only makes the code more complex without any benefit.
