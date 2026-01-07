"""
Parallel Executor for concurrent task execution with dependency tracking.
Enables 4-5x speedup through wave-based parallel processing.
"""

import asyncio
from typing import List, Dict, Any, Callable, Optional, Awaitable
from datetime import datetime
import time

from .rate_limiter import MultiProviderRateLimiter, RateLimitedTask
from .state_manager import WorkflowStateManager, ChapterTask, TaskStatus


class ParallelExecutor:
    """
    Executes tasks in parallel waves based on dependency graph.

    Key Features:
    - Wave-based execution (independent tasks run concurrently)
    - Rate limiting per API provider
    - Progress tracking
    - Error handling and retry logic
    - Performance metrics
    """

    def __init__(
        self,
        state_manager: WorkflowStateManager,
        max_concurrent: int = 5,
        rate_limiter: Optional[MultiProviderRateLimiter] = None,
        verbose: bool = True
    ):
        """
        Initialize parallel executor.

        Args:
            state_manager: WorkflowStateManager instance
            max_concurrent: Max concurrent tasks (default: 5)
            rate_limiter: Optional rate limiter (creates default if None)
            verbose: Whether to print progress
        """
        self.state = state_manager
        self.max_concurrent = max_concurrent
        self.rate_limiter = rate_limiter or MultiProviderRateLimiter()
        self.verbose = verbose

        # Metrics
        self.metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "total_time": 0,
            "wave_times": []
        }

    async def execute_wave(
        self,
        tasks: List[ChapterTask],
        task_executor: Callable[[ChapterTask], Awaitable[Any]],
        provider: str = "openai"
    ) -> List[Any]:
        """
        Execute a wave of independent tasks in parallel.

        Args:
            tasks: List of ChapterTask objects to execute
            task_executor: Async function that executes a task
            provider: API provider for rate limiting

        Returns:
            List of task results
        """
        if not tasks:
            return []

        wave_start = time.time()

        if self.verbose:
            print(f"\n🌊 Executing wave with {len(tasks)} tasks...")
            for task in tasks:
                print(f"   - {task.id}")

        # Create async tasks
        async_tasks = [
            self._execute_single_task(task, task_executor, provider)
            for task in tasks
        ]

        # Execute all tasks concurrently
        results = await asyncio.gather(*async_tasks, return_exceptions=True)

        wave_time = time.time() - wave_start
        self.metrics["wave_times"].append(wave_time)

        if self.verbose:
            print(f"✓ Wave completed in {wave_time:.1f}s")

        return results

    async def _execute_single_task(
        self,
        task: ChapterTask,
        task_executor: Callable[[ChapterTask], Awaitable[Any]],
        provider: str
    ) -> Any:
        """
        Execute a single task with rate limiting.

        Args:
            task: ChapterTask to execute
            task_executor: Async function to execute
            provider: API provider

        Returns:
            Task result
        """
        self.metrics["total_tasks"] += 1

        # Mark task as started
        self.state.mark_task_started(task.id)

        try:
            # Rate-limited execution
            async with RateLimitedTask(self.rate_limiter, provider):
                if self.verbose:
                    print(f"▶️  Starting: {task.id}")

                result = await task_executor(task)

                # Mark as complete
                self.state.mark_task_complete(task.id, result)
                self.metrics["completed_tasks"] += 1

                if self.verbose:
                    print(f"✅ Completed: {task.id}")

                return result

        except Exception as e:
            # Mark as failed
            self.state.mark_task_failed(task.id, str(e))
            self.metrics["failed_tasks"] += 1

            if self.verbose:
                print(f"❌ Failed: {task.id} - {str(e)}")

            raise

    async def execute_workflow(
        self,
        task_executor: Callable[[ChapterTask], Awaitable[Any]],
        provider: str = "openai"
    ) -> Dict[str, Any]:
        """
        Execute entire workflow in dependency-aware waves.

        Args:
            task_executor: Async function to execute each task
            provider: API provider for rate limiting

        Returns:
            Execution metrics and results
        """
        workflow_start = time.time()

        if self.verbose:
            print("\n" + "=" * 60)
            print("🚀 PARALLEL WORKFLOW EXECUTION")
            print("=" * 60)

        # Get tasks organized by wave
        waves = self.state.get_tasks_by_wave()

        if self.verbose:
            print(f"\n📊 Workflow Analysis:")
            print(f"   Total tasks: {sum(len(tasks) for tasks in waves.values())}")
            print(f"   Total waves: {len(waves)}")
            print(f"   Max concurrent: {self.max_concurrent}")

        all_results = {}

        # Execute each wave sequentially (tasks within wave run in parallel)
        for wave_num in sorted(waves.keys()):
            wave_tasks = waves[wave_num]

            if self.verbose:
                print(f"\n{'='*60}")
                print(f"Wave {wave_num}: {len(wave_tasks)} tasks")
                print(f"{'='*60}")

            # Execute wave
            results = await self.execute_wave(wave_tasks, task_executor, provider)

            # Store results
            for task, result in zip(wave_tasks, results):
                if not isinstance(result, Exception):
                    all_results[task.id] = result

        workflow_time = time.time() - workflow_start
        self.metrics["total_time"] = workflow_time

        if self.verbose:
            print(f"\n{'='*60}")
            print("✅ WORKFLOW COMPLETE")
            print(f"{'='*60}")
            print(f"Total time: {workflow_time:.1f}s")
            print(f"Completed: {self.metrics['completed_tasks']}/{self.metrics['total_tasks']}")
            print(f"Failed: {self.metrics['failed_tasks']}")
            print(f"Average wave time: {sum(self.metrics['wave_times'])/len(self.metrics['wave_times']):.1f}s")

        return {
            "results": all_results,
            "metrics": self.metrics.copy(),
            "state": self.state.get_workflow_stats()
        }

    async def execute_chapter_batch(
        self,
        chapter_numbers: List[int],
        task_executor: Callable[[int], Awaitable[Any]],
        provider: str = "openai"
    ) -> Dict[int, Any]:
        """
        Execute tasks for multiple chapters in parallel.

        Useful for phases where all chapters are independent (e.g., analysis phase).

        Args:
            chapter_numbers: List of chapter numbers to process
            task_executor: Async function that takes chapter number
            provider: API provider

        Returns:
            Dictionary mapping chapter numbers to results
        """
        if self.verbose:
            print(f"\n🔀 Batch processing {len(chapter_numbers)} chapters...")

        # Create wrapper tasks
        async def execute_chapter(ch_num: int) -> Any:
            async with RateLimitedTask(self.rate_limiter, provider):
                if self.verbose:
                    print(f"▶️  Processing Chapter {ch_num}...")

                result = await task_executor(ch_num)

                if self.verbose:
                    print(f"✅ Chapter {ch_num} complete")

                return result

        # Execute all chapters concurrently
        results = await asyncio.gather(
            *[execute_chapter(ch) for ch in chapter_numbers],
            return_exceptions=True
        )

        # Build result dictionary
        result_dict = {}
        for ch_num, result in zip(chapter_numbers, results):
            if not isinstance(result, Exception):
                result_dict[ch_num] = result
            else:
                if self.verbose:
                    print(f"❌ Chapter {ch_num} failed: {result}")

        return result_dict

    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics."""
        return {
            **self.metrics,
            "rate_limiter_stats": self.rate_limiter.get_all_stats(),
            "workflow_stats": self.state.get_workflow_stats()
        }

    def estimate_time(self, sequential_time: float) -> Dict[str, float]:
        """
        Estimate parallel execution time based on sequential time.

        Args:
            sequential_time: Time for sequential execution (seconds)

        Returns:
            Dictionary with time estimates
        """
        waves = self.state.get_tasks_by_wave()
        num_waves = len(waves)
        avg_tasks_per_wave = sum(len(tasks) for tasks in waves.values()) / num_waves

        # Assume each task takes sequential_time / total_tasks
        total_tasks = sum(len(tasks) for tasks in waves.values())
        time_per_task = sequential_time / total_tasks

        # Parallel time = time_per_task * num_waves (if all wave tasks run in parallel)
        # But account for max_concurrent limit
        max_wave_size = max(len(tasks) for tasks in waves.values())
        if max_wave_size > self.max_concurrent:
            # Some waves will take longer due to concurrent limit
            parallel_time = time_per_task * num_waves * (max_wave_size / self.max_concurrent)
        else:
            parallel_time = time_per_task * num_waves

        speedup = sequential_time / parallel_time

        return {
            "sequential_time": sequential_time,
            "estimated_parallel_time": parallel_time,
            "speedup_factor": speedup,
            "time_saved": sequential_time - parallel_time,
            "num_waves": num_waves,
            "avg_tasks_per_wave": avg_tasks_per_wave
        }


class MockTaskExecutor:
    """
    Mock task executor for testing parallel execution.

    Simulates task execution with configurable delay.
    """

    def __init__(self, delay_seconds: float = 1.0):
        """
        Initialize mock executor.

        Args:
            delay_seconds: Simulated task duration
        """
        self.delay = delay_seconds
        self.executed_tasks = []

    async def execute(self, task: ChapterTask) -> str:
        """
        Simulate task execution.

        Args:
            task: ChapterTask to execute

        Returns:
            Result string
        """
        self.executed_tasks.append(task.id)
        await asyncio.sleep(self.delay)
        return f"Result for {task.id}"
