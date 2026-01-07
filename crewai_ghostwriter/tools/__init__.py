"""Custom tools for CrewAI agents."""

from .issue_tracker import (
    IssueTrackerTool,
    GetFlagsForChapterTool,
    ResolveFlagTool
)

from .vector_memory_search import (
    VectorMemorySearchTool,
    SearchPlotSolutionsTool,
    GetNichePatternsTool
)

from .chapter_context_loader import (
    ChapterContextLoaderTool,
    LoadMultipleChaptersTool,
    GetContinuityFactsTool,
    StoreContinuityFactTool,
    GetAllChapterSummariesTool
)

from .story_contract_tools import (
    GetGlobalStoryContractTool,
    CheckRomancePacingTool,
    CheckMagicRevealTool
)

__all__ = [
    # Issue tracking
    "IssueTrackerTool",
    "GetFlagsForChapterTool",
    "ResolveFlagTool",

    # Vector memory search
    "VectorMemorySearchTool",
    "SearchPlotSolutionsTool",
    "GetNichePatternsTool",

    # Chapter context
    "ChapterContextLoaderTool",
    "LoadMultipleChaptersTool",
    "GetContinuityFactsTool",
    "StoreContinuityFactTool",
    "GetAllChapterSummariesTool",

    # Story contract (coherence guardrails)
    "GetGlobalStoryContractTool",
    "CheckRomancePacingTool",
    "CheckMagicRevealTool"
]
