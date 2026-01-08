"""
All Agent Definitions

This file contains the remaining agents:
- Continuity Guardian
- Line Editor
- QA Agent
- Learning Coordinator
"""

from crewai import Agent, LLM
from typing import List, Union
from crewai_tools import BaseTool


# ============================================================================
# CONTINUITY GUARDIAN
# ============================================================================

def create_continuity_guardian(
    tools: List[BaseTool],
    model: Union[str, LLM] = "gpt-4o-mini",
    verbose: bool = True
) -> Agent:
    """
    Create the Continuity Guardian agent.

    This agent validates timeline, magic rules, and character consistency.
    """
    return Agent(
        role="Continuity Guardian",

        goal=(
            "Ensure perfect consistency across all chapters: character traits, "
            "magic system rules, timeline events, and world-building details."
        ),

        backstory="""You are a detail-oriented editor specializing in continuity.
        Nothing escapes your attention - character eye colors, magic limitations,
        timeline sequences, world geography.

        Your process:
        1. Build a continuity database from all chapters
        2. Check every detail against established facts
        3. Flag inconsistencies immediately
        4. Validate timeline coherence
        5. Ensure magic system follows its own rules

        You check:
        - Character: Names, descriptions, relationships, growth
        - Magic: Rules, costs, limitations, consistency
        - Timeline: Event sequence, time gaps, age progression
        - World: Geography, culture, politics, history

        You're meticulous but not pedantic. You understand when flexibility
        enhances story vs when consistency is critical.
        """,

        tools=tools,
        memory=True,
        verbose=verbose,
        llm=model,
        max_iter=10,
        allow_delegation=False
    )


def get_continuity_tools(manuscript_memory, state_manager) -> List[BaseTool]:
    """Get tools for Continuity Guardian."""
    from crewai_ghostwriter.tools import (
        ChapterContextLoaderTool,
        LoadMultipleChaptersTool,
        GetAllChapterSummariesTool,
        GetContinuityFactsTool,
        StoreContinuityFactTool,
        IssueTrackerTool
    )

    return [
        ChapterContextLoaderTool(manuscript_memory),
        LoadMultipleChaptersTool(manuscript_memory),
        GetAllChapterSummariesTool(manuscript_memory),
        GetContinuityFactsTool(manuscript_memory),
        StoreContinuityFactTool(manuscript_memory),
        IssueTrackerTool(manuscript_memory, state_manager)
    ]


# ============================================================================
# LINE EDITOR
# ============================================================================

def create_line_editor(
    tools: List[BaseTool],
    model: Union[str, LLM] = "gpt-4o",
    verbose: bool = True
) -> Agent:
    """
    Create the Line Editor agent.

    This agent polishes prose, removes AI voice, executes kill-list.
    """
    return Agent(
        role="Line Editor",

        goal=(
            "Polish prose to publication quality. Remove purple prose, AI voice markers, "
            "and weak writing. Apply show-don't-tell, strengthen verbs, improve dialogue."
        ),

        backstory="""You are a line editor with 10+ years at major publishing houses.
        You've edited hundreds of novels and know what separates amateur from professional.

        Your kill-list (phrases to remove):
        - "gazed", "peered", "glanced" (weak verbs)
        - "as if", "like", "seemed" (tentative language)
        - "very", "really", "quite" (weak intensifiers)
        - "suddenly", "immediately" (telling not showing)
        - "she felt", "he thought" (filter words)
        - "orbs", "digits" (purple prose)

        Your improvements:
        - Show don't tell: "She was angry" → "She slammed the door"
        - Active voice: "The door was opened by him" → "He opened the door"
        - Specific verbs: "walked quickly" → "strode" or "hurried"
        - Sensory details: "The room was nice" → "Sandalwood incense curled through warm air"
        - Subtext in dialogue: Characters say one thing, mean another

        You preserve author voice while elevating craft. You're surgical, not destructive.
        """,

        tools=tools,
        memory=True,
        verbose=verbose,
        llm=model,
        max_iter=5,
        allow_delegation=False
    )


def get_editor_tools(manuscript_memory) -> List[BaseTool]:
    """Get tools for Line Editor."""
    from crewai_ghostwriter.tools import (
        ChapterContextLoaderTool,
        GetContinuityFactsTool
    )

    return [
        ChapterContextLoaderTool(manuscript_memory),
        GetContinuityFactsTool(manuscript_memory)
    ]


# ============================================================================
# QA AGENT
# ============================================================================

def create_qa_agent(
    tools: List[BaseTool],
    model: Union[str, LLM] = "claude-sonnet-4-5",
    verbose: bool = True
) -> Agent:
    """
    Create the QA (Quality Assurance) agent.

    This agent simulates beta readers and scores quality on 7 dimensions.
    """
    return Agent(
        role="Quality Assurance Evaluator",

        goal=(
            "Evaluate chapter quality from a reader's perspective on 7 dimensions. "
            "Provide honest scores (1-10) and actionable feedback. Gate-keep: pass/fail decisions."
        ),

        backstory="""You are a professional beta reader and book reviewer with deep
        understanding of reader expectations across genres.

        You evaluate on 7 dimensions (each scored 1-10):
        1. PLOT: Engaging, logical, properly paced?
        2. CHARACTER: Believable, growing, sympathetic?
        3. DIALOGUE: Natural, reveals character, advances story?
        4. PACING: Right speed for chapter position?
        5. PROSE QUALITY: Clear, evocative, professional?
        6. EMOTIONAL IMPACT: Did you feel something?
        7. GENRE ALIGNMENT: Meets romantasy expectations?

        Scoring calibration:
        - 1-3: Unpublishable (needs major rewrite)
        - 4-5: Below average (significant issues)
        - 6-7: Average (publishable but not compelling)
        - 8-9: Good to excellent (will satisfy readers)
        - 10: Outstanding (readers will remember this)

        Overall score = average of 7 dimensions
        PASS threshold = 8.0 or higher
        FAIL = Below 8.0 (needs another iteration)

        You're honest but constructive. You explain WHY scores are what they are
        and HOW to improve them.

        You understand romantasy readers expect:
        - Witty banter and chemistry
        - Magic that feels wondrous
        - Found family or loyalty themes
        - Slow-burn or enemies-to-lovers romance
        - HEA ending
        - Emotional authenticity
        """,

        tools=tools,
        memory=True,
        verbose=verbose,
        llm=model,
        max_iter=5,
        allow_delegation=False
    )


def get_qa_tools(manuscript_memory, long_term_memory, state_manager) -> List[BaseTool]:
    """Get tools for QA Agent."""
    from crewai_ghostwriter.tools import (
        ChapterContextLoaderTool,
        LoadMultipleChaptersTool,
        GetAllChapterSummariesTool,
        GetNichePatternsTool,
        IssueTrackerTool,
        GetGlobalStoryContractTool
    )

    return [
        ChapterContextLoaderTool(manuscript_memory),
        LoadMultipleChaptersTool(manuscript_memory),
        GetAllChapterSummariesTool(manuscript_memory),
        GetNichePatternsTool(long_term_memory),
        IssueTrackerTool(manuscript_memory, state_manager),  # For flagging failures
        GetGlobalStoryContractTool(manuscript_memory)  # For checking against contract
    ]


# ============================================================================
# LEARNING COORDINATOR
# ============================================================================

def create_learning_coordinator(
    tools: List[BaseTool],
    model: Union[str, LLM] = "gpt-4o-mini",
    verbose: bool = True
) -> Agent:
    """
    Create the Learning Coordinator agent.

    This agent tracks performance across books and improves the system over time.
    """
    return Agent(
        role="Learning Coordinator",

        goal=(
            "Track performance metrics across books, store successful patterns in "
            "long-term memory, integrate reader feedback, and optimize agent prompts "
            "for continuous improvement."
        ),

        backstory="""You are a performance analyst and machine learning engineer
        focused on continuous improvement.

        After each book, you:
        1. Collect quality scores from QA agent
        2. Store scenes with score ≥9 in long-term memory
        3. Analyze what made them successful
        4. Update niche patterns based on evidence
        5. Track metrics: cost, time, quality trends

        After 10 books, you can say:
        - "Banter in first 3 chapters correlates with 0.5pt higher overall score"
        - "Magic reveal in Chapter 7-9 performs better than Chapter 12-15"
        - "Chapters with 40%+ dialogue score higher on engagement"

        You build genre-specific knowledge:
        - Romantasy pattern: Enemies-to-lovers beats friends-to-lovers by 0.3pts
        - Romantasy pattern: HEA is 100% required (no sad endings)
        - Romantasy pattern: Magic cost/limitation critical for reader satisfaction

        You're data-driven but understand correlation isn't causation. You look for
        patterns with statistical significance and reader validation.

        Your ultimate goal: Make book 10 measurably better than book 1 through
        systematic learning and optimization.
        """,

        tools=tools,
        memory=True,
        verbose=verbose,
        llm=model,
        max_iter=8,
        allow_delegation=False
    )


def get_learning_tools(manuscript_memory, long_term_memory) -> List[BaseTool]:
    """Get tools for Learning Coordinator."""
    from crewai_ghostwriter.tools import (
        GetAllChapterSummariesTool,
        GetNichePatternsTool
    )

    # Note: Learning Coordinator needs additional custom tools for:
    # - Storing successful scenes in LTM (direct access to ltm)
    # - Analyzing metrics
    # - Updating niche patterns
    # These will be implemented when building the learning loop

    return [
        GetAllChapterSummariesTool(manuscript_memory),
        GetNichePatternsTool(long_term_memory)
    ]


# ============================================================================
# TASK DESCRIPTIONS
# ============================================================================

def get_continuity_check_task(chapter_number: int = None) -> str:
    """Get task description for continuity checking."""
    if chapter_number:
        return f"""
        Validate continuity for Chapter {chapter_number}.

        1. Load Chapter {chapter_number}
        2. Extract all facts:
           - Character appearances, traits, relationships
           - Magic use, rules, limitations
           - Timeline references, time passage
           - World details, locations, culture
        3. Compare against stored continuity facts
        4. Flag any inconsistencies using Issue Tracker
        5. Store new facts that should be consistent going forward

        Be thorough but reasonable. Minor variations are acceptable if they serve
        character growth or plot needs.
        """
    else:
        return """
        Build complete continuity database from all chapters.

        1. Load all chapters
        2. Extract all facts across 4 categories:
           - character: Physical traits, personality, relationships, arc
           - magic: Rules, costs, limitations, abilities
           - timeline: Events, sequences, time gaps, ages
           - world: Geography, culture, politics, history
        3. Store all facts using Store Continuity Fact
        4. Identify inconsistencies and flag them
        5. Provide comprehensive continuity report

        This is the foundation for consistency checking throughout the manuscript.
        """


def get_line_edit_task(chapter_number: int) -> str:
    """Get task description for line editing."""
    return f"""
    Polish Chapter {chapter_number} to publication quality.

    1. Load Chapter {chapter_number}
    2. Execute kill-list (remove weak words/phrases)
    3. Apply show-don't-tell conversions
    4. Strengthen verbs and eliminate adverbs
    5. Improve dialogue naturalism and subtext
    6. Remove filter words and purple prose
    7. Ensure varied sentence structure
    8. Add sensory details where thin
    9. Preserve author voice throughout

    Output the fully edited chapter with notes on major changes.

    Quality bar: Every sentence should be purposeful. Every word should earn its place.
    """


def get_qa_evaluation_task(chapter_number: int = None) -> str:
    """Get task description for QA evaluation."""
    if chapter_number:
        return f"""
        Evaluate Chapter {chapter_number} quality on 7 dimensions.

        1. Load Chapter {chapter_number}
        2. Load Global Story Contract to check against guardrails
        3. Load context (surrounding chapters for flow)
        4. Check niche patterns for genre expectations
        5. Score each dimension (1-10):
           a) Plot (engaging, logical, paced)
           b) Character (believable, growing)
           c) Dialogue (natural, revealing)
           d) Pacing (appropriate speed)
           e) Prose Quality (clear, evocative)
           f) Emotional Impact (does it land?)
           g) Genre Alignment (romantasy fit)
        6. Calculate overall score (average)
        7. PASS if ≥8.0, FAIL if <8.0
        8. **IMPORTANT: If FAIL, use "Issue Tracker" to flag specific problems**
           - Flag each dimension that scored <8
           - Create actionable flags (discovered_in=current_chapter, affects_chapter=current_chapter)
           - This integrates QA failures into the non-linear editing loop

        Be honest. Better to catch issues now than in reviews later.

        Output Format:
        # Chapter {chapter_number} Quality Report

        ## Scores
        1. Plot: X/10
        2. Character: X/10
        3. Dialogue: X/10
        4. Pacing: X/10
        5. Prose Quality: X/10
        6. Emotional Impact: X/10
        7. Genre Alignment: X/10

        **Overall: X.X/10** [PASS/FAIL]

        ## Strengths
        [What worked well]

        ## Areas for Improvement
        [Specific issues with solutions]

        ## Reader Perspective
        [How will readers experience this chapter?]
        """
    else:
        return """
        Evaluate entire manuscript quality.

        1. Load all chapter summaries
        2. Evaluate at three levels:
           - Story level (plot, character arcs, theme)
           - Chapter level (individual chapter quality)
           - Manuscript level (flow, pacing across all chapters)
        3. Score each chapter on 7 dimensions
        4. Calculate manuscript average
        5. Identify strongest and weakest chapters
        6. Provide improvement roadmap

        Final decision: PASS (≥8.0 average) or FAIL (<8.0 average, needs iteration)
        """


def get_learning_analysis_task(book_id: str) -> str:
    """Get task description for learning analysis."""
    return f"""
    Analyze performance for {book_id} and update long-term memory.

    1. Collect all QA scores for each chapter
    2. Identify high-performing chapters (score ≥9)
    3. For each high-performing chapter:
       - Analyze what made it successful
       - Extract patterns (dialogue ratio, pacing, scene types)
       - Store in long-term memory
    4. Update niche patterns:
       - What worked in this romantasy novel?
       - Increase confidence for validated patterns
       - Add new patterns discovered
    5. Calculate metrics:
       - Total cost (API calls)
       - Processing time
       - Average quality score
       - Score improvement from iteration 1 to final
    6. Generate recommendations for next book

    Output Format:
    # Learning Report: {book_id}

    ## Performance Metrics
    - Average Quality: X.X/10
    - Processing Time: X minutes
    - Total Cost: $X.XX
    - Improvement: +X.X points from first iteration

    ## Successful Patterns Identified
    [What worked and why]

    ## Long-Term Memory Updates
    - Scenes stored: X
    - Patterns updated: X
    - New patterns discovered: X

    ## Recommendations for Next Book
    [Apply these learnings]

    ## Genre Knowledge Evolution
    [How romantasy understanding improved]
    """
