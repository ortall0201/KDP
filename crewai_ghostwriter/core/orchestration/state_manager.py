"""
Workflow state manager with dependency tracking.
Manages task states, dependencies, and ensures proper execution order.
"""

import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from enum import Enum
import redis


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    BLOCKED = "blocked"  # Waiting on dependencies
    READY = "ready"  # Dependencies satisfied, ready to run
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"


class TaskType(Enum):
    """Types of tasks in the workflow."""
    ANALYZE = "analyze"  # Initial chapter analysis
    EXPAND = "expand"  # Expand chapter content
    FIX = "fix"  # Fix cross-chapter issue
    POLISH = "polish"  # Line editing
    VALIDATE = "validate"  # QA validation


class ChapterTask:
    """Represents a task to be performed on a chapter."""

    def __init__(
        self,
        chapter_number: int,
        task_type: TaskType,
        status: TaskStatus = TaskStatus.PENDING,
        dependencies: Optional[List[str]] = None,
        flags: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Initialize a chapter task.

        Args:
            chapter_number: Chapter number (1-15)
            task_type: Type of task
            status: Current status
            dependencies: List of task IDs this task depends on
            flags: Cross-chapter flags to address
            metadata: Additional task metadata
        """
        self.chapter_number = chapter_number
        self.task_type = task_type
        self.status = status
        self.dependencies = dependencies or []
        self.flags = flags or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
        self.result = None

    @property
    def id(self) -> str:
        """Generate task ID."""
        return f"{self.task_type.value}_{self.chapter_number}"

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "chapter_number": self.chapter_number,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "flags": self.flags,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ChapterTask':
        """Create task from dictionary."""
        task = cls(
            chapter_number=data["chapter_number"],
            task_type=TaskType(data["task_type"]),
            status=TaskStatus(data["status"]),
            dependencies=data.get("dependencies", []),
            flags=data.get("flags", []),
            metadata=data.get("metadata", {})
        )
        task.created_at = data.get("created_at")
        task.started_at = data.get("started_at")
        task.completed_at = data.get("completed_at")
        task.result = data.get("result")
        return task


class WorkflowStateManager:
    """
    Central workflow state management with dependency tracking.

    Key Features:
    - Tracks all tasks and their states
    - Manages dependencies between tasks
    - Automatically creates fix tasks from cross-chapter flags
    - Returns only ready tasks (dependencies satisfied)
    - Detects circular dependencies
    """

    def __init__(self, book_id: str, redis_host: str = "localhost", redis_port: int = 6379):
        """
        Initialize workflow state manager.

        Args:
            book_id: Unique identifier for this book
            redis_host: Redis server host
            redis_port: Redis server port
        """
        self.book_id = book_id
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )

        self.tasks: Dict[str, ChapterTask] = {}
        self.flags: List[Dict] = []
        self.completed_tasks_count = 0
        self.tasks_by_wave: Dict[int, List[str]] = {}

        # Load existing state from Redis
        self._load_from_redis()

    def _load_from_redis(self):
        """Load existing workflow state from Redis."""
        # Load tasks
        tasks_key = f"workflow:{self.book_id}:tasks"
        task_ids = self.redis.smembers(tasks_key)

        for task_id in task_ids:
            task_data_key = f"workflow:{self.book_id}:task:{task_id}"
            task_data = self.redis.get(task_data_key)
            if task_data:
                task = ChapterTask.from_dict(json.loads(task_data))
                self.tasks[task_id] = task

        # Load completed count
        count_key = f"workflow:{self.book_id}:completed_count"
        count = self.redis.get(count_key)
        self.completed_tasks_count = int(count) if count else 0

    def add_task(self, task: ChapterTask):
        """
        Add a task to the workflow.

        Args:
            task: ChapterTask to add
        """
        self.tasks[task.id] = task

        # Save to Redis
        tasks_key = f"workflow:{self.book_id}:tasks"
        self.redis.sadd(tasks_key, task.id)

        task_data_key = f"workflow:{self.book_id}:task:{task.id}"
        self.redis.set(task_data_key, json.dumps(task.to_dict()))

    def add_flag(self, discovered_in: int, affects_chapter: int, issue: Dict):
        """
        Add a cross-chapter flag and automatically create a fix task.

        This is the key integration with ManuscriptMemory.flag_cross_chapter_issue().

        Args:
            discovered_in: Chapter where issue was discovered
            affects_chapter: Chapter that needs fixing
            issue: Issue details
        """
        flag = {
            "discovered_in": discovered_in,
            "affects_chapter": affects_chapter,
            "issue": issue,
            "created_at": datetime.now().isoformat()
        }
        self.flags.append(flag)

        # Create fix task with dependency
        # Fix task must wait for the discovering chapter's analysis to complete
        fix_task = ChapterTask(
            chapter_number=affects_chapter,
            task_type=TaskType.FIX,
            status=TaskStatus.BLOCKED,
            dependencies=[f"analyze_{discovered_in}"],  # Wait for Ch 15 analysis
            flags=[flag],
            metadata={
                "triggered_by": discovered_in,
                "issue_type": issue.get("type", "unknown")
            }
        )

        self.add_task(fix_task)

    def get_ready_tasks(self) -> List[ChapterTask]:
        """
        Get all tasks whose dependencies are satisfied and ready to execute.

        Returns:
            List of ChapterTask objects ready to run
        """
        ready = []

        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING or task.status == TaskStatus.BLOCKED:
                # Check if all dependencies are complete
                deps_complete = all(
                    self.tasks.get(dep_id, ChapterTask(0, TaskType.ANALYZE)).status == TaskStatus.COMPLETE
                    for dep_id in task.dependencies
                )

                if deps_complete:
                    task.status = TaskStatus.READY
                    ready.append(task)

        return ready

    def get_tasks_by_wave(self) -> Dict[int, List[ChapterTask]]:
        """
        Organize tasks into execution waves based on dependencies.

        Wave 1: Tasks with no dependencies
        Wave 2: Tasks depending only on Wave 1
        Wave 3: Tasks depending on Wave 1 or 2
        etc.

        Returns:
            Dictionary mapping wave number to list of tasks
        """
        waves = {}
        wave_num = 1
        assigned_tasks = set()

        while len(assigned_tasks) < len(self.tasks):
            wave_tasks = []

            for task in self.tasks.values():
                if task.id in assigned_tasks:
                    continue

                # Check if all dependencies are in previous waves
                deps_satisfied = all(
                    dep_id in assigned_tasks
                    for dep_id in task.dependencies
                )

                if deps_satisfied:
                    wave_tasks.append(task)
                    assigned_tasks.add(task.id)

            if not wave_tasks:
                # No progress - circular dependency or error
                break

            waves[wave_num] = wave_tasks
            wave_num += 1

        return waves

    def mark_task_started(self, task_id: str):
        """Mark a task as in progress."""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.IN_PROGRESS
            self.tasks[task_id].started_at = datetime.now().isoformat()

            # Update Redis
            task_data_key = f"workflow:{self.book_id}:task:{task_id}"
            self.redis.set(task_data_key, json.dumps(self.tasks[task_id].to_dict()))

    def mark_task_complete(self, task_id: str, result: Optional[Any] = None):
        """
        Mark a task as complete.

        Args:
            task_id: Task ID
            result: Optional result data from task execution
        """
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.COMPLETE
            self.tasks[task_id].completed_at = datetime.now().isoformat()
            self.tasks[task_id].result = result

            self.completed_tasks_count += 1

            # Update Redis
            task_data_key = f"workflow:{self.book_id}:task:{task_id}"
            self.redis.set(task_data_key, json.dumps(self.tasks[task_id].to_dict()))

            count_key = f"workflow:{self.book_id}:completed_count"
            self.redis.set(count_key, self.completed_tasks_count)

    def mark_task_failed(self, task_id: str, error: str):
        """Mark a task as failed."""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.FAILED
            self.tasks[task_id].metadata["error"] = error

            # Update Redis
            task_data_key = f"workflow:{self.book_id}:task:{task_id}"
            self.redis.set(task_data_key, json.dumps(self.tasks[task_id].to_dict()))

    def has_circular_dependency(self, task_id: str, visited: Optional[Set[str]] = None) -> bool:
        """
        Check if a task has circular dependencies.

        Args:
            task_id: Task ID to check
            visited: Set of already visited task IDs

        Returns:
            True if circular dependency detected
        """
        if visited is None:
            visited = set()

        if task_id in visited:
            return True  # Circular!

        visited.add(task_id)

        task = self.tasks.get(task_id)
        if not task:
            return False

        for dep_id in task.dependencies:
            if self.has_circular_dependency(dep_id, visited.copy()):
                return True

        return False

    def get_workflow_stats(self) -> Dict[str, Any]:
        """
        Get workflow statistics.

        Returns:
            Dictionary with workflow stats
        """
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = sum(
                1 for t in self.tasks.values()
                if t.status == status
            )

        return {
            "book_id": self.book_id,
            "total_tasks": len(self.tasks),
            "completed": self.completed_tasks_count,
            "status_breakdown": status_counts,
            "total_flags": len(self.flags),
            "progress_pct": (
                self.completed_tasks_count / len(self.tasks) * 100
                if self.tasks else 0
            )
        }

    def get_task(self, task_id: str) -> Optional[ChapterTask]:
        """Get a specific task by ID."""
        return self.tasks.get(task_id)

    def get_tasks_for_chapter(self, chapter_number: int) -> List[ChapterTask]:
        """Get all tasks for a specific chapter."""
        return [
            task for task in self.tasks.values()
            if task.chapter_number == chapter_number
        ]

    def clear(self):
        """Clear all workflow state for this book."""
        # Clear Redis
        pattern = f"workflow:{self.book_id}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)

        # Clear in-memory state
        self.tasks.clear()
        self.flags.clear()
        self.completed_tasks_count = 0
        self.tasks_by_wave.clear()

    def initialize_standard_workflow(self, num_chapters: int = 15):
        """
        Initialize the standard workflow phases for all chapters.

        Args:
            num_chapters: Number of chapters (default 15)
        """
        # Phase 1: Analyze all chapters (no dependencies)
        for i in range(1, num_chapters + 1):
            analyze_task = ChapterTask(
                chapter_number=i,
                task_type=TaskType.ANALYZE,
                status=TaskStatus.PENDING,
                dependencies=[]
            )
            self.add_task(analyze_task)

        # Phase 2: Expand chapters (depends on own analysis)
        for i in range(1, num_chapters + 1):
            expand_task = ChapterTask(
                chapter_number=i,
                task_type=TaskType.EXPAND,
                status=TaskStatus.BLOCKED,
                dependencies=[f"analyze_{i}"]
            )
            self.add_task(expand_task)

        # Phase 3: Polish (depends on expand)
        for i in range(1, num_chapters + 1):
            polish_task = ChapterTask(
                chapter_number=i,
                task_type=TaskType.POLISH,
                status=TaskStatus.BLOCKED,
                dependencies=[f"expand_{i}"]
            )
            self.add_task(polish_task)

        # Phase 4: Validate (depends on polish)
        for i in range(1, num_chapters + 1):
            validate_task = ChapterTask(
                chapter_number=i,
                task_type=TaskType.VALIDATE,
                status=TaskStatus.BLOCKED,
                dependencies=[f"polish_{i}"]
            )
            self.add_task(validate_task)

    def visualize_dependencies(self) -> str:
        """
        Create a text visualization of task dependencies.

        Returns:
            String representation of dependency graph
        """
        lines = ["Task Dependency Graph:", "=" * 50]

        waves = self.get_tasks_by_wave()
        for wave_num, tasks in sorted(waves.items()):
            lines.append(f"\nWave {wave_num}:")
            for task in tasks:
                deps_str = ", ".join(task.dependencies) if task.dependencies else "none"
                lines.append(f"  - {task.id} [{task.status.value}] (deps: {deps_str})")

        return "\n".join(lines)
