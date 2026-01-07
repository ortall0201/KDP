"""
Issue Tracker Tool for cross-chapter flagging.
Enables agents to flag issues in other chapters while working.
"""

from typing import Dict, Any, Optional
from crewai_tools import BaseTool
from pydantic import BaseModel, Field


class IssueTrackerInput(BaseModel):
    """Input schema for IssueTracker tool."""
    discovered_in: int = Field(..., description="Chapter number where issue was discovered (1-15)")
    affects_chapter: int = Field(..., description="Chapter number that needs fixing (1-15)")
    issue_type: str = Field(..., description="Type of issue: 'foreshadowing', 'continuity', 'pacing', 'character', 'plot'")
    detail: str = Field(..., description="Detailed description of the issue and what needs to be fixed")
    severity: str = Field(..., description="Issue severity: 'low', 'medium', 'high', 'critical'")


class IssueTrackerTool(BaseTool):
    """
    Tool for flagging cross-chapter issues.

    This is the KEY tool that enables non-linear editing.
    Agents can flag issues in other chapters while working on current chapter.

    Example:
        Agent working on Chapter 15 discovers that Chapter 1 needs to
        foreshadow the magic reveal. Agent uses this tool to flag it.
    """

    name: str = "Issue Tracker"
    description: str = """
    Flag an issue in another chapter that needs fixing.
    Use this when you discover a problem in a different chapter while working.

    Examples:
    - Working on Ch 15, realize Ch 1 needs foreshadowing
    - Working on Ch 10, notice character inconsistency in Ch 3
    - Working on Ch 12, see pacing issue that starts in Ch 7

    Input parameters:
    - discovered_in: Your current chapter number
    - affects_chapter: Chapter that needs fixing
    - issue_type: Type (foreshadowing/continuity/pacing/character/plot)
    - detail: What needs to be fixed
    - severity: How important (low/medium/high/critical)
    """
    args_schema: type[BaseModel] = IssueTrackerInput

    def __init__(self, manuscript_memory, state_manager):
        """
        Initialize with memory systems.

        Args:
            manuscript_memory: ManuscriptMemory instance
            state_manager: WorkflowStateManager instance
        """
        super().__init__()
        self.memory = manuscript_memory
        self.state = state_manager

    def _run(
        self,
        discovered_in: int,
        affects_chapter: int,
        issue_type: str,
        detail: str,
        severity: str
    ) -> str:
        """
        Create a cross-chapter flag.

        Returns:
            Success message with flag ID
        """
        # Validate inputs
        if not (1 <= discovered_in <= 15):
            return f"Error: discovered_in must be between 1-15, got {discovered_in}"

        if not (1 <= affects_chapter <= 15):
            return f"Error: affects_chapter must be between 1-15, got {affects_chapter}"

        if discovered_in == affects_chapter:
            return f"Error: Use regular editing for same-chapter issues, not cross-chapter flagging"

        valid_types = ['foreshadowing', 'continuity', 'pacing', 'character', 'plot']
        if issue_type not in valid_types:
            return f"Error: issue_type must be one of {valid_types}, got '{issue_type}'"

        valid_severities = ['low', 'medium', 'high', 'critical']
        if severity not in valid_severities:
            return f"Error: severity must be one of {valid_severities}, got '{severity}'"

        # Create issue dictionary
        issue = {
            "type": issue_type,
            "detail": detail,
            "severity": severity
        }

        # Flag in ManuscriptMemory
        flag_id = self.memory.flag_cross_chapter_issue(
            discovered_in=discovered_in,
            affects_chapter=affects_chapter,
            issue=issue
        )

        # Create fix task in WorkflowStateManager
        self.state.add_flag(
            discovered_in=discovered_in,
            affects_chapter=affects_chapter,
            issue=issue
        )

        return (
            f"✓ Issue flagged successfully!\n"
            f"Flag ID: {flag_id}\n"
            f"Discovered in: Chapter {discovered_in}\n"
            f"Affects: Chapter {affects_chapter}\n"
            f"Type: {issue_type} ({severity} severity)\n"
            f"Detail: {detail}\n\n"
            f"A fix task has been automatically created for Chapter {affects_chapter}.\n"
            f"It will execute after Chapter {discovered_in} analysis completes."
        )


class GetFlagsForChapterInput(BaseModel):
    """Input schema for getting flags."""
    chapter_number: int = Field(..., description="Chapter number to check for flags (1-15)")


class GetFlagsForChapterTool(BaseTool):
    """
    Tool for retrieving flags affecting a specific chapter.

    Agents use this before working on a chapter to see what issues
    need to be fixed.
    """

    name: str = "Get Chapter Flags"
    description: str = """
    Get all unresolved flags affecting a specific chapter.
    Use this before working on a chapter to see what needs fixing.

    Returns list of issues that were flagged by other chapters.
    """
    args_schema: type[BaseModel] = GetFlagsForChapterInput

    def __init__(self, manuscript_memory):
        """
        Initialize with manuscript memory.

        Args:
            manuscript_memory: ManuscriptMemory instance
        """
        super().__init__()
        self.memory = manuscript_memory

    def _run(self, chapter_number: int) -> str:
        """
        Get flags for a chapter.

        Returns:
            Formatted list of flags or message if none
        """
        if not (1 <= chapter_number <= 15):
            return f"Error: chapter_number must be between 1-15, got {chapter_number}"

        flags = self.memory.get_flags_for_chapter(chapter_number)

        if not flags:
            return f"No unresolved flags for Chapter {chapter_number}. Ready to proceed!"

        result = [f"Unresolved flags for Chapter {chapter_number}:\n"]

        for i, flag in enumerate(flags, 1):
            result.append(
                f"\n{i}. Issue from Chapter {flag['discovered_in']}:\n"
                f"   Type: {flag['issue']['type']}\n"
                f"   Severity: {flag['issue']['severity']}\n"
                f"   Detail: {flag['issue']['detail']}\n"
                f"   Flag ID: {flag['id']}"
            )

        result.append(f"\nTotal: {len(flags)} issue(s) to address")
        return "".join(result)


class ResolveFlagInput(BaseModel):
    """Input schema for resolving flags."""
    flag_id: str = Field(..., description="The flag ID to mark as resolved")


class ResolveFlagTool(BaseTool):
    """
    Tool for marking a flag as resolved.

    Agents use this after fixing an issue to mark it complete.
    """

    name: str = "Resolve Flag"
    description: str = """
    Mark a flag as resolved after fixing the issue.
    Use this after you've addressed the flagged issue in a chapter.
    """
    args_schema: type[BaseModel] = ResolveFlagInput

    def __init__(self, manuscript_memory):
        """
        Initialize with manuscript memory.

        Args:
            manuscript_memory: ManuscriptMemory instance
        """
        super().__init__()
        self.memory = manuscript_memory

    def _run(self, flag_id: str) -> str:
        """
        Resolve a flag.

        Returns:
            Success message
        """
        # Check if flag exists
        all_flags = self.memory.get_unresolved_flags()
        flag_exists = any(f['id'] == flag_id for f in all_flags)

        if not flag_exists:
            return f"Error: Flag ID '{flag_id}' not found or already resolved"

        self.memory.resolve_flag(flag_id)

        return f"✓ Flag {flag_id} marked as resolved!"
