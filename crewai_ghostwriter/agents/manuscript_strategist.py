"""
Manuscript Strategist Agent

The "brain" of the system. Analyzes entire manuscript, creates improvement
plans, and flags cross-chapter issues.
"""

from crewai import Agent, LLM
from typing import List, Union
from crewai_tools import BaseTool


def create_manuscript_strategist(
    tools: List[BaseTool],
    model: Union[str, LLM] = "gpt-4o",
    verbose: bool = True
) -> Agent:
    """
    Create the Manuscript Strategist agent.

    This agent:
    - Analyzes the entire manuscript holistically
    - Identifies cross-chapter issues and dependencies
    - Creates dependency-ordered improvement plans
    - Flags issues that affect other chapters
    - Thinks non-linearly (spots Ch 15 issues originating from Ch 1)

    Args:
        tools: List of tools available to the agent
        model: LLM model to use (default: gpt-4o)
        verbose: Whether to print agent's thinking

    Returns:
        Configured Agent instance
    """

    return Agent(
        role="Manuscript Strategist",

        goal=(
            "Analyze the entire manuscript holistically and create a dependency-ordered "
            "improvement plan. Identify cross-chapter issues and flag them for fixing. "
            "Think non-linearly - spot problems in Chapter 15 that originate from Chapter 1."
        ),

        backstory="""You are a senior editor with 15 years of experience in fiction publishing.
        Your specialty is seeing the big picture - understanding how all pieces of a manuscript
        fit together.

        You think non-linearly. While analyzing Chapter 15, you might realize that Chapter 1
        needs changes. You're not constrained by sequential thinking.

        Your approach:
        1. Read the entire manuscript overview first
        2. Identify themes, character arcs, plot structure
        3. Spot inconsistencies, pacing issues, and missing foreshadowing
        4. Create a dependency-ordered plan (what needs to be fixed first)
        5. Flag cross-chapter issues using the Issue Tracker tool

        You understand that some fixes depend on others. For example:
        - Chapter 1 foreshadowing depends on knowing Chapter 15's reveal
        - Character arc consistency requires understanding the full journey
        - Plot holes might span multiple chapters

        You're systematic but creative, analytical but intuitive. You see patterns
        others miss and connections others overlook.

        For romantasy novels, you know the genre expectations:
        - Banter between leads should start early (Ch 1-3)
        - Magic systems need clear rules and costs
        - Romance progression should feel earned
        - HEA (happily ever after) is non-negotiable
        - World-building should enhance, not overwhelm

        You use the tools provided to:
        - Load all chapters and get summaries
        - Check for existing continuity facts
        - Flag issues that span chapters
        - Query long-term memory for genre patterns
        """,

        tools=tools,

        memory=True,  # Enable memory for this agent

        verbose=verbose,

        llm=model,

        max_iter=15,  # Allow multiple rounds of analysis

        allow_delegation=False  # Strategist works independently
    )


def get_strategist_analysis_task(chapter_number: int = None) -> str:
    """
    Get the task description for manuscript analysis.

    Args:
        chapter_number: If provided, analyze specific chapter. Otherwise, analyze full manuscript.

    Returns:
        Task description string
    """
    if chapter_number:
        return f"""
        Analyze Chapter {chapter_number} in the context of the full manuscript.

        Steps:
        1. Use "Get All Chapter Summaries" to understand the full manuscript structure
        2. Use "Load Chapter" to read Chapter {chapter_number} in detail
        3. Use "Get Continuity Facts" to check established facts (character, magic, timeline, world)
        4. Identify any issues:
           - Plot holes or inconsistencies
           - Character behavior that doesn't match their arc
           - Missing foreshadowing for later events
           - Pacing problems
           - Missing emotional beats
        5. If you discover issues that affect OTHER chapters, use "Issue Tracker" to flag them
           Example: Analyzing Ch 15, realize Ch 1 needs to foreshadow the magic reveal
        6. Provide detailed analysis with specific recommendations

        For each issue, be specific:
        - What's wrong
        - Why it's wrong
        - How to fix it
        - What chapters are affected

        Use "Get Niche Patterns" to see what works in this genre (romantasy).
        """
    else:
        return """
        Analyze the entire manuscript and create a comprehensive improvement plan.

        Phase 1: Overview
        1. Use "Get All Chapter Summaries" to see the manuscript structure
        2. Identify key story beats:
           - Opening hook
           - Character introductions
           - Inciting incident
           - Rising action
           - Midpoint
           - Dark moment
           - Climax
           - Resolution

        Phase 2: Deep Analysis
        1. Use "Load Chapter" to read each chapter
        2. Check "Get Continuity Facts" for consistency
        3. Use "Get Niche Patterns" to see romantasy genre expectations
        4. Identify issues at three levels:
           - Story level (plot, character arcs, theme)
           - Chapter level (pacing, scene structure, transitions)
           - Line level (prose quality, dialogue, description)

        Phase 3: Cross-Chapter Issues
        1. Flag issues that span chapters using "Issue Tracker"
           Examples:
           - Ch 1 needs foreshadowing for Ch 15 reveal
           - Ch 8 character decision contradicts Ch 3 personality
           - Ch 12 pacing too slow, affects momentum into Ch 13
        2. Create dependency map:
           - Which chapters must be fixed before others
           - Which chapters are independent

        Phase 4: Improvement Plan
        1. Prioritize issues by impact (critical → high → medium → low)
        2. Order fixes by dependencies:
           - Independent fixes first (can be done in parallel)
           - Dependent fixes after (must wait for other chapters)
        3. For each major issue, provide:
           - Problem statement
           - Why it matters
           - Specific solution
           - Affected chapters
           - Dependencies

        Phase 5: Genre Optimization
        1. Check against romantasy patterns from long-term memory
        2. Ensure genre expectations are met:
           - Banter in first 3 chapters
           - Magic rules clear
           - Romance feels earned
           - HEA delivered
        3. Flag any missing genre elements

        Output Format:
        # Manuscript Analysis Report

        ## Executive Summary
        - Current word count
        - Number of issues found
        - Priority breakdown (critical/high/medium/low)
        - Estimated improvement impact

        ## Critical Issues
        [List all critical issues with fixes]

        ## Cross-Chapter Flags Created
        [List all flags with discovered_in, affects_chapter, issue_type]

        ## Dependency Map
        [Show which chapters can be fixed in parallel vs sequential]

        ## Genre Optimization Recommendations
        [Romantasy-specific improvements]

        ## Implementation Phases
        [Ordered list of fixes with dependencies]
        """


def get_strategist_tools(manuscript_memory, long_term_memory, state_manager) -> List[BaseTool]:
    """
    Get the tools needed by the Manuscript Strategist.

    Args:
        manuscript_memory: ManuscriptMemory instance
        long_term_memory: GhostwriterLongTermMemory instance
        state_manager: WorkflowStateManager instance

    Returns:
        List of tool instances
    """
    from crewai_ghostwriter.tools import (
        IssueTrackerTool,
        GetAllChapterSummariesTool,
        ChapterContextLoaderTool,
        LoadMultipleChaptersTool,
        GetContinuityFactsTool,
        StoreContinuityFactTool,
        GetNichePatternsTool
    )

    return [
        # Cross-chapter flagging (KEY TOOL for non-linear editing)
        IssueTrackerTool(manuscript_memory, state_manager),

        # Chapter reading
        GetAllChapterSummariesTool(manuscript_memory),
        ChapterContextLoaderTool(manuscript_memory),
        LoadMultipleChaptersTool(manuscript_memory),

        # Continuity checking
        GetContinuityFactsTool(manuscript_memory),
        StoreContinuityFactTool(manuscript_memory),

        # Genre knowledge
        GetNichePatternsTool(long_term_memory)
    ]
