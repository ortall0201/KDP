"""
Story Contract Tools for accessing global coherence guardrails.

Prevents voice drift, romance pacing errors, and magic reveal timing issues
during parallel chapter processing.
"""

from typing import Optional
from crewai_tools import BaseTool
from pydantic import BaseModel, Field


class GetStoryContractInput(BaseModel):
    """Input schema for getting story contract."""
    pass  # No input needed


class GetGlobalStoryContractTool(BaseTool):
    """
    Tool for loading the Global Story Contract.

    Use this BEFORE working on a chapter to understand:
    - POV and technical rules
    - Character voice fingerprints
    - Romance escalation guidelines for this chapter range
    - Magic reveal schedule (what can be revealed when)
    - Character facts that must remain consistent

    This prevents parallel chapter work from drifting in voice, pacing, or coherence.
    """

    name: str = "Get Global Story Contract"
    description: str = """
    Load the Global Story Contract with coherence guardrails for this manuscript.

    IMPORTANT: Call this BEFORE working on any chapter to ensure:
    - Voice consistency (FMC/MMC dialogue and internal voice)
    - Romance pacing (what intimacy level is appropriate for this chapter)
    - Magic reveals (what can/cannot be revealed yet)
    - Character facts (names, appearances, backgrounds)
    - POV rules (no head hopping, tense consistency)

    Example usage:
    1. Before expanding Chapter 5, load contract
    2. Check romance escalation: chapters 4-6 = "grudging respect and banter"
    3. Check magic reveals: can reveal "power awakens" but NOT "true nature"
    4. Write chapter within these guardrails

    This tool has no parameters - just call it to get the full contract.
    """
    args_schema: type[BaseModel] = GetStoryContractInput

    def __init__(self, manuscript_memory):
        """
        Initialize with manuscript memory.

        Args:
            manuscript_memory: ManuscriptMemory instance
        """
        super().__init__()
        self.memory = manuscript_memory

    def _run(self) -> str:
        """
        Get the story contract.

        Returns:
            Formatted story contract with all guardrails
        """
        contract = self.memory.get_story_contract()

        if not contract.contract.get("created_at"):
            return (
                "⚠️  Story contract not yet initialized!\n\n"
                "The contract should be set up before parallel processing begins.\n"
                "Contact the Manuscript Strategist to initialize it."
            )

        # Format the contract for agent consumption
        result = [
            "=" * 60,
            "GLOBAL STORY CONTRACT - COHERENCE GUARDRAILS",
            "=" * 60,
            "",
            "📖 POV & TECHNICAL RULES",
            "-" * 60,
            f"POV Type: {contract.contract['pov']['type']}",
            f"Perspective: {contract.contract['pov']['perspective']}",
            f"Tense: {contract.contract['pov']['tense']}",
            f"Rules: {', '.join(contract.contract['pov']['rules'])}",
            "",
            "🗣️  CHARACTER VOICE FINGERPRINTS",
            "-" * 60
        ]

        # FMC Voice
        fmc_voice = contract.contract['voice']['FMC']
        if fmc_voice.get('tone'):
            result.extend([
                "FMC:",
                f"  Tone: {fmc_voice['tone']}",
                f"  Internal Voice: {fmc_voice.get('internal_voice', 'not set')}",
                f"  Dialogue: {', '.join(fmc_voice.get('dialogue_tendencies', []))}",
                f"  Speech: {', '.join(fmc_voice.get('speech_patterns', []))}",
            ])

        # MMC Voice
        mmc_voice = contract.contract['voice']['MMC']
        if mmc_voice.get('tone'):
            result.extend([
                "MMC:",
                f"  Tone: {mmc_voice['tone']}",
                f"  Internal Voice: {mmc_voice.get('internal_voice', 'not set')}",
                f"  Dialogue: {', '.join(mmc_voice.get('dialogue_tendencies', []))}",
                f"  Speech: {', '.join(mmc_voice.get('speech_patterns', []))}",
            ])

        # Romance Escalation
        result.extend([
            "",
            "💕 ROMANCE ESCALATION LADDER",
            "-" * 60,
            f"Type: {contract.contract['romance']['type']}",
            ""
        ])

        for chapter_range, intimacy_level in contract.contract['romance']['escalation_ladder'].items():
            result.append(f"  {chapter_range}: {intimacy_level}")

        if contract.contract['romance'].get('boundaries'):
            result.append(f"\nBoundaries: {', '.join(contract.contract['romance']['boundaries'])}")

        # Magic System
        result.extend([
            "",
            "✨ MAGIC SYSTEM RULES",
            "-" * 60,
            f"Type: {contract.contract['magic']['type']}",
            "",
            "Rules:"
        ])

        for rule in contract.contract['magic']['rules']:
            result.append(f"  • {rule}")

        result.append("\nLimitations:")
        for limit in contract.contract['magic']['limitations']:
            result.append(f"  • {limit}")

        result.extend([
            "",
            "REVEAL SCHEDULE (What can be revealed when):",
            ""
        ])

        for chapter_range, reveals in contract.contract['magic']['reveal_schedule'].items():
            result.append(f"{chapter_range}:")
            for reveal in reveals:
                result.append(f"  • {reveal}")

        # Characters
        result.extend([
            "",
            "👥 CHARACTER FACTS",
            "-" * 60
        ])

        fmc = contract.contract['characters']['FMC']
        if fmc.get('name'):
            result.extend([
                f"FMC: {fmc['name']}",
                f"  Age: {fmc.get('age', 'not set')}",
                f"  Arc: {fmc.get('arc', 'not set')}",
                f"  Fatal Flaw: {fmc.get('fatal_flaw', 'not set')}",
                f"  Core Desire: {fmc.get('core_desire', 'not set')}",
            ])

        mmc = contract.contract['characters']['MMC']
        if mmc.get('name'):
            result.extend([
                f"\nMMC: {mmc['name']}",
                f"  Age: {mmc.get('age', 'not set')}",
                f"  Arc: {mmc.get('arc', 'not set')}",
                f"  Fatal Flaw: {mmc.get('fatal_flaw', 'not set')}",
                f"  Core Desire: {mmc.get('core_desire', 'not set')}",
            ])

        # Genre Requirements
        result.extend([
            "",
            "📚 GENRE REQUIREMENTS (ROMANTASY)",
            "-" * 60
        ])

        for req in contract.contract['genre']['requirements']:
            result.append(f"  ✓ {req}")

        result.extend([
            "",
            "=" * 60,
            "⚠️  IMPORTANT: Follow these guardrails to maintain coherence",
            "across parallel chapter processing. Violations will cause",
            "voice drift, pacing errors, and continuity issues.",
            "=" * 60
        ])

        return "\n".join(result)


class CheckRomancePacingInput(BaseModel):
    """Input schema for checking romance pacing."""
    chapter_number: int = Field(..., description="Current chapter number (1-15)")
    proposed_action: str = Field(..., description="Romantic action you want to write (e.g., 'first kiss', 'love confession')")


class CheckRomancePacingTool(BaseTool):
    """
    Tool for checking if a romantic action is appropriate for current chapter.

    Use this to avoid romance pacing errors in parallel execution.
    """

    name: str = "Check Romance Pacing"
    description: str = """
    Check if a proposed romantic action fits the escalation ladder for this chapter.

    Use this BEFORE writing romantic scenes to ensure proper pacing:
    - Is a kiss appropriate in Chapter 3? (Check the ladder!)
    - Should characters confess love in Chapter 7? (Check the ladder!)
    - Can they have physical intimacy in Chapter 10? (Check boundaries!)

    Input:
    - chapter_number: Current chapter (1-15)
    - proposed_action: What you want to write

    Returns guidance on whether it's allowed and why.
    """
    args_schema: type[BaseModel] = CheckRomancePacingInput

    def __init__(self, manuscript_memory):
        """Initialize with manuscript memory."""
        super().__init__()
        self.memory = manuscript_memory

    def _run(self, chapter_number: int, proposed_action: str) -> str:
        """Check romance pacing."""
        contract = self.memory.get_story_contract()

        result = contract.check_romance_pacing(chapter_number, proposed_action)

        if result["allowed"]:
            return (
                f"✅ ALLOWED for Chapter {chapter_number}\n\n"
                f"Current escalation level: {result['current_level']}\n"
                f"Reason: {result['reason']}\n\n"
                f"You may proceed with: {proposed_action}"
            )
        else:
            return (
                f"❌ NOT ALLOWED for Chapter {chapter_number}\n\n"
                f"Current escalation level: {result['current_level']}\n"
                f"Reason: {result['reason']}\n\n"
                f"Proposed action '{proposed_action}' is premature.\n"
                f"Consider holding this for a later chapter."
            )


class CheckMagicRevealInput(BaseModel):
    """Input schema for checking magic reveals."""
    chapter_number: int = Field(..., description="Current chapter number (1-15)")
    proposed_reveal: str = Field(..., description="Magic information you want to reveal")


class CheckMagicRevealTool(BaseTool):
    """
    Tool for checking if a magic reveal is appropriate for current chapter.

    Prevents spoiling major reveals or revealing information too early.
    """

    name: str = "Check Magic Reveal"
    description: str = """
    Check if a proposed magic reveal fits the reveal schedule for this chapter.

    Use this BEFORE revealing magic information to avoid spoilers:
    - Can FMC's true power be revealed in Chapter 4? (Check schedule!)
    - Can magic system rules be explained in Chapter 2? (Check schedule!)
    - Is this reveal on the forbidden list? (Check forbidden knowledge!)

    Input:
    - chapter_number: Current chapter (1-15)
    - proposed_reveal: What magic info you want to reveal

    Returns guidance on whether it's allowed and what CAN be revealed.
    """
    args_schema: type[BaseModel] = CheckMagicRevealInput

    def __init__(self, manuscript_memory):
        """Initialize with manuscript memory."""
        super().__init__()
        self.memory = manuscript_memory

    def _run(self, chapter_number: int, proposed_reveal: str) -> str:
        """Check magic reveal timing."""
        contract = self.memory.get_story_contract()

        result = contract.check_magic_reveal(chapter_number, proposed_reveal)

        if result["allowed"]:
            return (
                f"✅ ALLOWED for Chapter {chapter_number}\n\n"
                f"Reason: {result['reason']}\n"
                f"Allowed reveals at this stage:\n" +
                "\n".join(f"  • {r}" for r in result.get('allowed_reveals', []))
            )
        else:
            return (
                f"❌ NOT ALLOWED for Chapter {chapter_number}\n\n"
                f"Reason: {result['reason']}\n"
                f"Suggestion: {result.get('suggestion', 'Save for later')}\n\n"
                f"This reveal would spoil a major plot point. Hold it for later chapters."
            )
