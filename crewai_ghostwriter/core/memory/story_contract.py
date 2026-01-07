"""
Global Story Contract - Shared coherence guardrails for parallel execution.

Prevents voice drift, pacing inconsistency, and magic reveal timing issues
when chapters are processed in parallel.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class GlobalStoryContract:
    """
    Shared story rules that all chapter-level tasks must follow.

    This artifact is built once at the start and read by all parallel tasks
    to ensure global coherence despite parallel processing.

    Key problem it solves:
    - Parallel chapter work can cause voice drift
    - Romance pacing can become inconsistent
    - Magic reveals can leak information too early
    - Character facts can contradict

    Solution: Single source of truth that all agents read before working.
    """

    def __init__(self, book_id: str):
        """
        Initialize story contract.

        Args:
            book_id: Unique identifier for this book
        """
        self.book_id = book_id
        self.contract = {
            # POV & Technical Rules
            "pov": {
                "type": None,  # "first_person", "third_limited", "third_omniscient"
                "perspective": None,  # "FMC", "MMC", "alternating"
                "tense": None,  # "past", "present"
                "rules": []  # ["no head hopping", "single POV per chapter"]
            },

            # Voice Fingerprints
            "voice": {
                "FMC": {
                    "tone": None,  # "witty", "sarcastic", "earnest", "guarded"
                    "dialogue_tendencies": [],  # ["short sentences", "questions", "deflects"]
                    "internal_voice": None,  # "self-deprecating", "analytical"
                    "speech_patterns": []  # ["contractions", "modern slang", "formal"]
                },
                "MMC": {
                    "tone": None,
                    "dialogue_tendencies": [],
                    "internal_voice": None,
                    "speech_patterns": []
                }
            },

            # Romance Escalation
            "romance": {
                "type": None,  # "slow_burn", "enemies_to_lovers", "friends_to_lovers"
                "escalation_ladder": {
                    # Chapter ranges → allowed intimacy level
                    "chapters_1_3": "antagonistic_tension",
                    "chapters_4_6": "grudging_respect",
                    "chapters_7_9": "emotional_vulnerability",
                    "chapters_10_12": "undeniable_attraction",
                    "chapters_13_15": "commitment_and_resolution"
                },
                "first_kiss": None,  # Chapter number or "not_yet"
                "love_confession": None,  # Chapter number or "not_yet"
                "boundaries": []  # ["no open door scenes", "fade to black"]
            },

            # Magic System
            "magic": {
                "type": None,  # "elemental", "blood_magic", "rune_based"
                "rules": [],  # ["magic has physical cost", "powered by emotion"]
                "limitations": [],  # ["drains energy", "requires line of sight"]
                "reveal_schedule": {
                    # What can be known when
                    "chapters_1_5": [],  # ["magic exists", "FMC has dormant power"]
                    "chapters_6_10": [],  # ["power awakens", "first manifestation"]
                    "chapters_11_15": []  # ["full powers revealed", "true nature"]
                },
                "forbidden_knowledge": []  # Things that CANNOT be revealed yet
            },

            # Character Facts
            "characters": {
                "FMC": {
                    "name": None,
                    "age": None,
                    "appearance": {},  # {"hair": "red", "eyes": "green", "height": "5'6"}
                    "background": None,
                    "arc": None,  # "orphan → belongs", "powerless → powerful"
                    "fatal_flaw": None,  # "trusts no one", "impulsive"
                    "core_desire": None  # "freedom", "family", "acceptance"
                },
                "MMC": {
                    "name": None,
                    "age": None,
                    "appearance": {},
                    "background": None,
                    "arc": None,
                    "fatal_flaw": None,
                    "core_desire": None
                },
                "supporting": {}  # name → character details
            },

            # World Rules
            "world": {
                "setting": None,  # "fae court", "modern with hidden magic"
                "geography": {},  # key locations and their rules
                "politics": {},  # power structures, conflicts
                "culture": {},  # traditions, taboos, social rules
                "tone": None  # "dark", "cozy", "epic", "intimate"
            },

            # Genre Requirements
            "genre": {
                "primary": "romantasy",
                "requirements": [
                    "HEA (happily ever after) required",
                    "Romance must be central to plot",
                    "Magic/fantasy element required",
                    "Emotional beats prioritized over action",
                    "Character growth through relationship"
                ]
            },

            # Metadata
            "created_at": None,
            "last_updated": None,
            "version": "1.0"
        }

    def set_pov(self, pov_type: str, perspective: str, tense: str, rules: List[str]):
        """
        Set POV and technical rules.

        Args:
            pov_type: "first_person", "third_limited", "third_omniscient"
            perspective: "FMC", "MMC", "alternating"
            tense: "past", "present"
            rules: List of rules like ["no head hopping"]
        """
        self.contract["pov"] = {
            "type": pov_type,
            "perspective": perspective,
            "tense": tense,
            "rules": rules
        }
        self._update_timestamp()

    def set_voice_fingerprint(
        self,
        character: str,
        tone: str,
        dialogue_tendencies: List[str],
        internal_voice: str,
        speech_patterns: List[str]
    ):
        """
        Set voice fingerprint for a character.

        Args:
            character: "FMC" or "MMC"
            tone: Overall tone ("witty", "sarcastic", etc.)
            dialogue_tendencies: List of dialogue patterns
            internal_voice: Internal monologue style
            speech_patterns: Speech patterns
        """
        self.contract["voice"][character] = {
            "tone": tone,
            "dialogue_tendencies": dialogue_tendencies,
            "internal_voice": internal_voice,
            "speech_patterns": speech_patterns
        }
        self._update_timestamp()

    def set_romance_rules(
        self,
        romance_type: str,
        escalation_ladder: Dict[str, str],
        boundaries: List[str]
    ):
        """
        Set romance progression rules.

        Args:
            romance_type: "slow_burn", "enemies_to_lovers", etc.
            escalation_ladder: Chapter ranges → intimacy levels
            boundaries: Content boundaries
        """
        self.contract["romance"]["type"] = romance_type
        self.contract["romance"]["escalation_ladder"] = escalation_ladder
        self.contract["romance"]["boundaries"] = boundaries
        self._update_timestamp()

    def set_magic_system(
        self,
        magic_type: str,
        rules: List[str],
        limitations: List[str],
        reveal_schedule: Dict[str, List[str]]
    ):
        """
        Set magic system rules and reveal timing.

        Args:
            magic_type: Type of magic
            rules: How magic works
            limitations: Magic limitations
            reveal_schedule: What can be revealed when
        """
        self.contract["magic"] = {
            "type": magic_type,
            "rules": rules,
            "limitations": limitations,
            "reveal_schedule": reveal_schedule,
            "forbidden_knowledge": []
        }
        self._update_timestamp()

    def add_character(
        self,
        role: str,
        name: str,
        age: int,
        appearance: Dict[str, str],
        background: str,
        arc: str,
        fatal_flaw: str,
        core_desire: str
    ):
        """
        Add or update character details.

        Args:
            role: "FMC", "MMC", or character name for supporting
            name: Character name
            age: Character age
            appearance: Physical description
            background: Backstory
            arc: Character arc
            fatal_flaw: Fatal flaw
            core_desire: Core desire
        """
        character_data = {
            "name": name,
            "age": age,
            "appearance": appearance,
            "background": background,
            "arc": arc,
            "fatal_flaw": fatal_flaw,
            "core_desire": core_desire
        }

        if role in ["FMC", "MMC"]:
            self.contract["characters"][role] = character_data
        else:
            self.contract["characters"]["supporting"][role] = character_data

        self._update_timestamp()

    def check_romance_pacing(self, chapter_number: int, proposed_action: str) -> Dict[str, Any]:
        """
        Check if a romantic action is allowed at this chapter.

        Args:
            chapter_number: Current chapter
            proposed_action: What the agent wants to write

        Returns:
            Dictionary with allowed status and reason
        """
        # Determine which range chapter falls into
        if 1 <= chapter_number <= 3:
            allowed_level = self.contract["romance"]["escalation_ladder"]["chapters_1_3"]
        elif 4 <= chapter_number <= 6:
            allowed_level = self.contract["romance"]["escalation_ladder"]["chapters_4_6"]
        elif 7 <= chapter_number <= 9:
            allowed_level = self.contract["romance"]["escalation_ladder"]["chapters_7_9"]
        elif 10 <= chapter_number <= 12:
            allowed_level = self.contract["romance"]["escalation_ladder"]["chapters_10_12"]
        else:
            allowed_level = self.contract["romance"]["escalation_ladder"]["chapters_13_15"]

        # Simple keyword matching (could be more sophisticated)
        if "kiss" in proposed_action.lower():
            first_kiss_ch = self.contract["romance"].get("first_kiss")
            if first_kiss_ch and chapter_number < first_kiss_ch:
                return {
                    "allowed": False,
                    "reason": f"First kiss scheduled for Chapter {first_kiss_ch}, this is Chapter {chapter_number}",
                    "current_level": allowed_level
                }

        return {
            "allowed": True,
            "reason": f"Within escalation level: {allowed_level}",
            "current_level": allowed_level
        }

    def check_magic_reveal(self, chapter_number: int, proposed_reveal: str) -> Dict[str, Any]:
        """
        Check if a magic reveal is allowed at this chapter.

        Args:
            chapter_number: Current chapter
            proposed_reveal: What magic info agent wants to reveal

        Returns:
            Dictionary with allowed status and reason
        """
        # Check forbidden knowledge
        for forbidden in self.contract["magic"]["forbidden_knowledge"]:
            if forbidden.lower() in proposed_reveal.lower():
                return {
                    "allowed": False,
                    "reason": f"Forbidden knowledge: {forbidden}",
                    "suggestion": "Save this reveal for later chapters"
                }

        # Check reveal schedule
        if 1 <= chapter_number <= 5:
            allowed = self.contract["magic"]["reveal_schedule"]["chapters_1_5"]
        elif 6 <= chapter_number <= 10:
            allowed = self.contract["magic"]["reveal_schedule"]["chapters_6_10"]
        else:
            allowed = self.contract["magic"]["reveal_schedule"]["chapters_11_15"]

        return {
            "allowed": True,
            "reason": "Within reveal schedule",
            "allowed_reveals": allowed
        }

    def get_contract_summary(self) -> str:
        """
        Get human-readable contract summary.

        Returns:
            Formatted contract summary
        """
        lines = [
            "GLOBAL STORY CONTRACT",
            "=" * 60,
            "",
            f"Book ID: {self.book_id}",
            f"Version: {self.contract['version']}",
            f"Last Updated: {self.contract['last_updated']}",
            "",
            "POV:",
            f"  Type: {self.contract['pov']['type']}",
            f"  Perspective: {self.contract['pov']['perspective']}",
            f"  Tense: {self.contract['pov']['tense']}",
            f"  Rules: {', '.join(self.contract['pov']['rules'])}",
            "",
            "Romance:",
            f"  Type: {self.contract['romance']['type']}",
            f"  Escalation: {len(self.contract['romance']['escalation_ladder'])} stages",
            "",
            "Magic:",
            f"  Type: {self.contract['magic']['type']}",
            f"  Rules: {len(self.contract['magic']['rules'])} rules",
            f"  Limitations: {len(self.contract['magic']['limitations'])} limitations",
            "",
            "Characters:",
            f"  FMC: {self.contract['characters']['FMC'].get('name', 'Not set')}",
            f"  MMC: {self.contract['characters']['MMC'].get('name', 'Not set')}",
            "",
            "=" * 60
        ]

        return "\n".join(lines)

    def to_dict(self) -> Dict:
        """Export contract as dictionary."""
        return self.contract.copy()

    def from_dict(self, data: Dict):
        """Import contract from dictionary."""
        self.contract = data.copy()

    def to_json(self) -> str:
        """Export contract as JSON."""
        return json.dumps(self.contract, indent=2)

    def from_json(self, json_str: str):
        """Import contract from JSON."""
        self.contract = json.loads(json_str)

    def _update_timestamp(self):
        """Update last modified timestamp."""
        self.contract["last_updated"] = datetime.now().isoformat()
        if not self.contract["created_at"]:
            self.contract["created_at"] = self.contract["last_updated"]
