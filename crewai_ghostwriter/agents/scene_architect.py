"""
Scene Architect Agent

Writes publication-quality scenes with non-linear awareness.
Can flag issues while writing.
"""

from crewai import Agent
from typing import List
from crewai_tools import BaseTool


def create_scene_architect(
    tools: List[BaseTool],
    model: str = "gpt-4o",
    verbose: bool = True
) -> Agent:
    """
    Create the Scene Architect agent.

    This agent:
    - Writes publication-quality expanded scenes
    - Maintains voice and style consistency
    - Uses long-term memory to learn from successful scenes
    - Flags cross-chapter issues while writing (non-linear awareness)
    - Matches target word count (22.6K → 47K)

    Args:
        tools: List of tools available to the agent
        model: LLM model to use (default: gpt-4o)
        verbose: Whether to print agent's thinking

    Returns:
        Configured Agent instance
    """

    return Agent(
        role="Scene Architect",

        goal=(
            "Expand chapters from outlines into publication-quality scenes that match "
            "the established voice, style, and genre expectations. Flag any cross-chapter "
            "issues discovered while writing."
        ),

        backstory="""You are a bestselling fiction author specializing in romantasy.
        You've written 20+ novels and understand what makes readers turn pages.

        Your writing philosophy:
        - Show, don't tell (use action, dialogue, body language)
        - Every scene must advance plot OR character OR both
        - Banter reveals character and builds tension
        - Sensory details create immersion
        - Pacing varies: fast for action, slower for emotion
        - Magic should feel wondrous yet grounded

        You're experienced with romantasy conventions:
        - Enemies-to-lovers or slow-burn romance
        - Witty banter between leads
        - Found family themes
        - Magic with clear costs/limitations
        - Epic stakes with personal consequences
        - HEA (happily ever after) ending

        Your process for expanding a chapter:
        1. Read the existing chapter/outline
        2. Check cross-chapter flags to see what needs addressing
        3. Search long-term memory for similar successful scenes
        4. Load continuity facts (character traits, magic rules, etc.)
        5. Expand the chapter scene by scene:
           - Identify key beats
           - Add dialogue, action, description
           - Maintain voice consistency
           - Hit emotional notes
           - Proper pacing
        6. If you discover issues in OTHER chapters while writing, FLAG THEM
           Example: Writing Ch 8 dialogue, realize Ch 3 personality doesn't match

        Style guidelines:
        - Active voice preferred
        - Varied sentence structure (short for impact, longer for flow)
        - Strong verbs over adverbs
        - Specific details over generic descriptions
        - Subtext in dialogue (what's unsaid matters)
        - Emotional truth over melodrama

        Target metrics:
        - Original: 22,600 words across 15 chapters (≈1,500 per chapter)
        - Expanded: 47,000 words across 15 chapters (≈3,100 per chapter)
        - Expansion ratio: ~2x
        - Maintain pacing despite increased word count
        """,

        tools=tools,

        memory=True,

        verbose=verbose,

        llm=model,

        max_iter=10,

        allow_delegation=False
    )


def get_architect_expansion_task(chapter_number: int) -> str:
    """
    Get the task description for expanding a chapter.

    Args:
        chapter_number: Chapter to expand

    Returns:
        Task description string
    """
    return f"""
    Expand Chapter {chapter_number} from outline to publication-quality prose.

    Current state: Approximately 1,500 words
    Target state: Approximately 3,100 words (2x expansion)

    Process:

    1. PREPARATION
       - **FIRST: Use "Get Global Story Contract"** - Load coherence guardrails
       - Use "Load Chapter" to read the current version
       - Use "Get Chapter Flags" to see what issues need addressing
       - Use "Get Continuity Facts" for all categories (character, magic, timeline, world)
       - Use "Get All Chapter Summaries" for context

    2. LEARN FROM SUCCESSES
       For each major scene type you need to write, use "Search Similar Scenes":
       - Writing banter? Search: "witty argument between characters"
       - Writing action? Search: "combat scene with magic"
       - Writing romance? Search: "tender moment between leads"
       - Writing tension? Search: "suspenseful confrontation"

       Study the patterns in successful scenes (score ≥9) but write ORIGINAL content.

    3. IDENTIFY SCENE BEATS
       Break the chapter into scenes and identify beats:
       - What happens (plot)
       - Why it matters (character/theme)
       - Emotional tone (tension/relief/anticipation)
       - Pacing (fast/medium/slow)

    4. EXPAND EACH SCENE
       For each beat:
       a) Opening: Hook the reader, establish scene setting
       b) Action/Dialogue: Show character dynamics, advance plot
       c) Reaction: Character responses, internal thoughts
       d) Consequence: What changed? What's the new status quo?

       Writing techniques:
       - Use all five senses (not just sight)
       - Vary dialogue tags and beats
       - Body language reveals emotion
       - Internal thoughts show character
       - Pacing: short sentences = fast, longer = slow

    5. MAINTAIN CONSISTENCY & USE STORY CONTRACT GUARDRAILS
       - **Check romance pacing:** Use "Check Romance Pacing" before romantic scenes
       - **Check magic reveals:** Use "Check Magic Reveal" before revealing magic info
       - Character voices must match Story Contract fingerprints
       - Follow POV rules from contract (no head hopping)
       - Magic rules from contract limitations
       - Timeline must be coherent
       - Foreshadowing for future events
       - Callbacks to previous chapters

    6. FLAG CROSS-CHAPTER ISSUES
       While writing, if you realize OTHER chapters need changes:
       - Use "Issue Tracker" to flag them
       - Be specific about what needs fixing
       - Continue writing the current chapter

       Examples:
       - "Writing Ch 8, character motivation unclear from Ch 3 introduction"
       - "Writing Ch 10, Ch 5 needs to foreshadow this magic ability"
       - "Writing Ch 12, Ch 7 pacing too slow for momentum into this chapter"

    7. GENRE REQUIREMENTS
       Ensure this chapter includes (where appropriate):
       - Banter (especially in early chapters)
       - Character growth
       - Plot advancement
       - Magic that feels wondrous
       - Romantic tension (if romance subplot active)
       - Emotional authenticity

    8. QUALITY CHECKS
       Before finishing:
       - Read aloud mentally (does it flow?)
       - Emotional beats landed?
       - Pacing appropriate for chapter position?
       - Word count target hit (~3,100 words)?
       - Voice consistent with rest of manuscript?

    Output Format:
    # Chapter {chapter_number} - Expanded Version

    [Full expanded chapter text here]

    ## Expansion Notes
    - Original word count: [X]
    - New word count: [Y]
    - Expansion ratio: [Z]x
    - Key additions: [List major scenes/beats added]
    - Cross-chapter flags created: [List any flags]

    ## Quality Metrics
    - Pacing: [fast/medium/slow]
    - Emotional impact: [1-10]
    - Voice consistency: [1-10]
    - Genre alignment: [1-10]

    Remember: Publication quality means readers should forget they're reading and
    get lost in the story. Every word should earn its place.
    """


def get_architect_tools(manuscript_memory, long_term_memory, state_manager) -> List[BaseTool]:
    """
    Get the tools needed by the Scene Architect.

    Args:
        manuscript_memory: ManuscriptMemory instance
        long_term_memory: GhostwriterLongTermMemory instance
        state_manager: WorkflowStateManager instance

    Returns:
        List of tool instances
    """
    from crewai_ghostwriter.tools import (
        IssueTrackerTool,
        GetFlagsForChapterTool,
        ChapterContextLoaderTool,
        LoadMultipleChaptersTool,
        GetAllChapterSummariesTool,
        GetContinuityFactsTool,
        StoreContinuityFactTool,
        VectorMemorySearchTool,
        GetGlobalStoryContractTool,
        CheckRomancePacingTool,
        CheckMagicRevealTool
    )

    return [
        # Cross-chapter awareness
        IssueTrackerTool(manuscript_memory, state_manager),
        GetFlagsForChapterTool(manuscript_memory),

        # Chapter reading
        ChapterContextLoaderTool(manuscript_memory),
        LoadMultipleChaptersTool(manuscript_memory),
        GetAllChapterSummariesTool(manuscript_memory),

        # Continuity
        GetContinuityFactsTool(manuscript_memory),
        StoreContinuityFactTool(manuscript_memory),

        # Learning from successes
        VectorMemorySearchTool(long_term_memory),

        # Story Contract (coherence guardrails for parallel execution)
        GetGlobalStoryContractTool(manuscript_memory),
        CheckRomancePacingTool(manuscript_memory),
        CheckMagicRevealTool(manuscript_memory)
    ]
