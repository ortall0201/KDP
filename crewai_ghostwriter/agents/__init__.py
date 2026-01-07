"""CrewAI agents for ghostwriting tasks."""

from .manuscript_strategist import (
    create_manuscript_strategist,
    get_strategist_tools,
    get_strategist_analysis_task
)

from .scene_architect import (
    create_scene_architect,
    get_architect_tools,
    get_architect_expansion_task
)

from .all_agents import (
    create_continuity_guardian,
    get_continuity_tools,
    get_continuity_check_task,
    create_line_editor,
    get_editor_tools,
    get_line_edit_task,
    create_qa_agent,
    get_qa_tools,
    get_qa_evaluation_task,
    create_learning_coordinator,
    get_learning_tools,
    get_learning_analysis_task
)

__all__ = [
    # Manuscript Strategist
    "create_manuscript_strategist",
    "get_strategist_tools",
    "get_strategist_analysis_task",

    # Scene Architect
    "create_scene_architect",
    "get_architect_tools",
    "get_architect_expansion_task",

    # Continuity Guardian
    "create_continuity_guardian",
    "get_continuity_tools",
    "get_continuity_check_task",

    # Line Editor
    "create_line_editor",
    "get_editor_tools",
    "get_line_edit_task",

    # QA Agent
    "create_qa_agent",
    "get_qa_tools",
    "get_qa_evaluation_task",

    # Learning Coordinator
    "create_learning_coordinator",
    "get_learning_tools",
    "get_learning_analysis_task"
]
