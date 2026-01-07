"""
Safety Guards for preventing infinite loops and workflow issues.

Implements multiple safety mechanisms:
1. Max iterations limit
2. Circular dependency detection
3. No progress detection
4. Flag explosion guard
5. Timeout protection
"""

from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta
import time


class MaxIterationsExceeded(Exception):
    """Raised when max iterations limit is exceeded."""
    pass


class CircularDependencyDetected(Exception):
    """Raised when circular dependency is found."""
    pass


class NoProgressError(Exception):
    """Raised when workflow makes no progress."""
    pass


class TooManyFlagsError(Exception):
    """Raised when too many flags are created."""
    pass


class WorkflowTimeoutError(Exception):
    """Raised when workflow exceeds time limit."""
    pass


class SafetyGuards:
    """
    Safety guard system for workflow execution.

    Prevents common failure modes:
    - Infinite loops
    - Circular dependencies
    - Stuck workflows
    - Flag explosion
    - Runaway execution time
    """

    def __init__(
        self,
        max_iterations: int = 50,
        max_open_flags: int = 100,
        no_progress_threshold: int = 10,
        max_execution_time_hours: int = 6
    ):
        """
        Initialize safety guards.

        Args:
            max_iterations: Maximum total iterations allowed
            max_open_flags: Maximum unresolved flags allowed
            no_progress_threshold: Iterations without progress before error
            max_execution_time_hours: Maximum workflow execution time
        """
        self.max_iterations = max_iterations
        self.max_open_flags = max_open_flags
        self.no_progress_threshold = no_progress_threshold
        self.max_execution_time = timedelta(hours=max_execution_time_hours)

        # Tracking
        self.iteration_count = 0
        self.last_progress_iteration = 0
        self.completed_tasks_history: List[int] = []
        self.workflow_start_time: Optional[datetime] = None

    def start_workflow(self):
        """Mark workflow start time."""
        self.workflow_start_time = datetime.now()
        self.iteration_count = 0
        self.last_progress_iteration = 0
        self.completed_tasks_history = [0]

    def check_iteration_limit(self):
        """
        Check if iteration limit exceeded.

        Raises:
            MaxIterationsExceeded: If limit exceeded
        """
        self.iteration_count += 1

        if self.iteration_count > self.max_iterations:
            raise MaxIterationsExceeded(
                f"Workflow exceeded maximum iterations limit ({self.max_iterations}). "
                f"This likely indicates an infinite loop or improper task dependencies. "
                f"Review the workflow state and dependency graph."
            )

    def check_progress(self, completed_tasks: int):
        """
        Check if workflow is making progress.

        Args:
            completed_tasks: Number of currently completed tasks

        Raises:
            NoProgressError: If no progress in threshold iterations
        """
        self.completed_tasks_history.append(completed_tasks)

        # Check if we've made progress
        if len(self.completed_tasks_history) > self.no_progress_threshold:
            # Get completed count from threshold iterations ago
            old_count = self.completed_tasks_history[-self.no_progress_threshold]
            current_count = completed_tasks

            if current_count == old_count:
                raise NoProgressError(
                    f"No progress in last {self.no_progress_threshold} iterations. "
                    f"Stuck at {current_count} completed tasks. "
                    f"Check for blocked tasks with unsatisfiable dependencies."
                )

            # Progress made, update last progress iteration
            if current_count > old_count:
                self.last_progress_iteration = self.iteration_count

    def check_flag_count(self, open_flags: int):
        """
        Check if too many flags have been created.

        Args:
            open_flags: Number of unresolved flags

        Raises:
            TooManyFlagsError: If flag count exceeds limit
        """
        if open_flags > self.max_open_flags:
            raise TooManyFlagsError(
                f"Too many unresolved flags ({open_flags} > {self.max_open_flags}). "
                f"Agents may be over-flagging issues or creating circular flag dependencies. "
                f"Review agent prompts and flag resolution process."
            )

    def check_execution_time(self):
        """
        Check if workflow has exceeded time limit.

        Raises:
            WorkflowTimeoutError: If execution time exceeded
        """
        if self.workflow_start_time is None:
            return

        elapsed = datetime.now() - self.workflow_start_time

        if elapsed > self.max_execution_time:
            raise WorkflowTimeoutError(
                f"Workflow exceeded maximum execution time ({self.max_execution_time}). "
                f"Elapsed: {elapsed}. Consider breaking into smaller workflows or "
                f"investigating slow tasks."
            )

    def check_circular_dependency(
        self,
        task_id: str,
        dependency_graph: Dict[str, List[str]],
        visited: Optional[Set[str]] = None
    ) -> bool:
        """
        Check for circular dependencies in task graph.

        Args:
            task_id: Task ID to check
            dependency_graph: Map of task_id -> list of dependency task_ids
            visited: Set of visited task IDs (for recursion)

        Returns:
            True if circular dependency detected

        Raises:
            CircularDependencyDetected: If circular dependency found
        """
        if visited is None:
            visited = set()

        if task_id in visited:
            # Found a cycle!
            cycle_path = " → ".join(list(visited) + [task_id])
            raise CircularDependencyDetected(
                f"Circular dependency detected: {cycle_path}\n"
                f"This creates an impossible situation where tasks depend on each other. "
                f"Review task dependencies and cross-chapter flags."
            )

        visited.add(task_id)

        # Check all dependencies
        dependencies = dependency_graph.get(task_id, [])
        for dep_id in dependencies:
            self.check_circular_dependency(dep_id, dependency_graph, visited.copy())

        return False

    def get_status(self) -> Dict:
        """
        Get current safety guard status.

        Returns:
            Dictionary with current status
        """
        elapsed = None
        if self.workflow_start_time:
            elapsed = (datetime.now() - self.workflow_start_time).total_seconds()

        return {
            "iteration_count": self.iteration_count,
            "max_iterations": self.max_iterations,
            "iterations_remaining": self.max_iterations - self.iteration_count,
            "last_progress_iteration": self.last_progress_iteration,
            "iterations_since_progress": self.iteration_count - self.last_progress_iteration,
            "no_progress_threshold": self.no_progress_threshold,
            "max_open_flags": self.max_open_flags,
            "elapsed_seconds": elapsed,
            "max_execution_seconds": self.max_execution_time.total_seconds()
        }


class WorkflowHealthMonitor:
    """
    Monitors workflow health and provides diagnostics.

    Tracks metrics and identifies potential issues before they become critical.
    """

    def __init__(self):
        """Initialize health monitor."""
        self.metrics = {
            "iterations": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "blocked_tasks": 0,
            "open_flags": 0,
            "avg_task_time": 0,
            "slowest_task": None,
            "warnings": []
        }

    def update(self, workflow_state: Dict):
        """
        Update metrics from workflow state.

        Args:
            workflow_state: Current workflow state dictionary
        """
        self.metrics["completed_tasks"] = workflow_state.get("completed", 0)
        self.metrics["failed_tasks"] = workflow_state.get("status_breakdown", {}).get("failed", 0)
        self.metrics["blocked_tasks"] = workflow_state.get("status_breakdown", {}).get("blocked", 0)
        self.metrics["open_flags"] = workflow_state.get("total_flags", 0)

        # Check for warning conditions
        self._check_warnings()

    def _check_warnings(self):
        """Check for warning conditions."""
        self.metrics["warnings"] = []

        # High failure rate
        total = self.metrics["completed_tasks"] + self.metrics["failed_tasks"]
        if total > 5:
            failure_rate = self.metrics["failed_tasks"] / total
            if failure_rate > 0.2:  # >20% failure
                self.metrics["warnings"].append(
                    f"High failure rate: {failure_rate*100:.1f}% of tasks failing"
                )

        # Many blocked tasks
        if self.metrics["blocked_tasks"] > 10:
            self.metrics["warnings"].append(
                f"Many blocked tasks ({self.metrics['blocked_tasks']}). "
                f"Check for dependency issues."
            )

        # Many open flags
        if self.metrics["open_flags"] > 50:
            self.metrics["warnings"].append(
                f"Many open flags ({self.metrics['open_flags']}). "
                f"Agents may be over-flagging or flags not resolving."
            )

    def get_health_report(self) -> str:
        """
        Get human-readable health report.

        Returns:
            Formatted health report string
        """
        lines = [
            "Workflow Health Report",
            "=" * 60,
            f"Completed Tasks: {self.metrics['completed_tasks']}",
            f"Failed Tasks: {self.metrics['failed_tasks']}",
            f"Blocked Tasks: {self.metrics['blocked_tasks']}",
            f"Open Flags: {self.metrics['open_flags']}",
        ]

        if self.metrics["warnings"]:
            lines.append(f"\n⚠️  Warnings ({len(self.metrics['warnings'])}):")
            for warning in self.metrics["warnings"]:
                lines.append(f"  - {warning}")
        else:
            lines.append("\n✅ No warnings - workflow healthy")

        return "\n".join(lines)

    def is_healthy(self) -> bool:
        """
        Check if workflow is healthy.

        Returns:
            True if no warnings
        """
        return len(self.metrics["warnings"]) == 0
