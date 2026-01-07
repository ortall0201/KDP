"""
Short-term memory system for manuscript processing.
Stores context during single book processing including cross-chapter flags.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import redis
from .story_contract import GlobalStoryContract


class ManuscriptMemory:
    """
    Short-term memory for a single manuscript processing session.

    Key Features:
    - Stores all 15 chapters in memory
    - Cross-chapter flagging (Ch 15 can flag Ch 1 issue)
    - Dependency tracking
    - Task state management
    - Iteration counting
    """

    def __init__(self, book_id: str, redis_host: str = "localhost", redis_port: int = 6379):
        """
        Initialize manuscript memory.

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

        # In-memory context (synced with Redis)
        self.context = {
            "manuscript": None,
            "chapters": {},  # chapter_num → chapter_text
            "chapter_analyses": {},  # chapter_num → analysis_data
            "cross_chapter_flags": [],
            "continuity_db": {},  # character/magic/timeline facts
            "task_states": {},  # task_id → status
            "iteration_count": 0
        }

        # Global Story Contract (coherence guardrails for parallel execution)
        self.story_contract = GlobalStoryContract(book_id)

        # Load existing data from Redis if available
        self._load_from_redis()

    def _load_from_redis(self):
        """Load existing manuscript data from Redis."""
        # Load manuscript metadata
        manuscript_key = f"book:{self.book_id}:manuscript"
        manuscript_data = self.redis.get(manuscript_key)
        if manuscript_data:
            self.context["manuscript"] = json.loads(manuscript_data)

        # Load chapters
        for i in range(1, 16):  # Chapters 1-15
            chapter_key = f"book:{self.book_id}:chapter:{i}"
            chapter_data = self.redis.get(chapter_key)
            if chapter_data:
                self.context["chapters"][i] = json.loads(chapter_data)

        # Load flags
        flags_key = f"book:{self.book_id}:flags"
        flags = self.redis.lrange(flags_key, 0, -1)
        self.context["cross_chapter_flags"] = [json.loads(f) for f in flags]

        # Load iteration count
        iter_key = f"book:{self.book_id}:iteration_count"
        count = self.redis.get(iter_key)
        self.context["iteration_count"] = int(count) if count else 0

        # Load story contract
        contract_key = f"book:{self.book_id}:story_contract"
        contract_data = self.redis.get(contract_key)
        if contract_data:
            self.story_contract.from_json(contract_data)

    def store_manuscript(self, manuscript_data: Dict[str, Any]):
        """
        Store the original manuscript data.

        Args:
            manuscript_data: Dictionary containing manuscript metadata
        """
        self.context["manuscript"] = manuscript_data
        manuscript_key = f"book:{self.book_id}:manuscript"
        self.redis.set(manuscript_key, json.dumps(manuscript_data))

    def store_chapter(self, chapter_number: int, chapter_text: str, metadata: Optional[Dict] = None):
        """
        Store a chapter's text and metadata.

        Args:
            chapter_number: Chapter number (1-15)
            chapter_text: The chapter content
            metadata: Optional metadata (word count, scene count, etc.)
        """
        chapter_data = {
            "text": chapter_text,
            "metadata": metadata or {},
            "stored_at": datetime.now().isoformat()
        }

        self.context["chapters"][chapter_number] = chapter_data
        chapter_key = f"book:{self.book_id}:chapter:{chapter_number}"
        self.redis.set(chapter_key, json.dumps(chapter_data))

    def get_chapter(self, chapter_number: int) -> Optional[Dict]:
        """
        Retrieve a chapter's data.

        Args:
            chapter_number: Chapter number (1-15)

        Returns:
            Chapter data dictionary or None if not found
        """
        return self.context["chapters"].get(chapter_number)

    def get_all_chapters(self) -> Dict[int, Dict]:
        """
        Get all stored chapters.

        Returns:
            Dictionary mapping chapter numbers to chapter data
        """
        return self.context["chapters"]

    def store_chapter_analysis(self, chapter_number: int, analysis: Dict[str, Any]):
        """
        Store the analysis results for a chapter.

        Args:
            chapter_number: Chapter number (1-15)
            analysis: Analysis results from Manuscript Strategist
        """
        self.context["chapter_analyses"][chapter_number] = analysis
        analysis_key = f"book:{self.book_id}:analysis:{chapter_number}"
        self.redis.set(analysis_key, json.dumps(analysis))

    def flag_cross_chapter_issue(
        self,
        discovered_in: int,
        affects_chapter: int,
        issue: Dict[str, Any]
    ) -> str:
        """
        KEY FEATURE: Non-linear editing via cross-chapter flagging.

        When an agent working on Chapter 15 discovers an issue that affects
        Chapter 1, they can flag it here. The system will create a dependency
        and ensure Ch 1 is fixed after Ch 15 analysis completes.

        Args:
            discovered_in: Chapter number where issue was discovered
            affects_chapter: Chapter number that needs fixing
            issue: Dictionary with 'type', 'detail', 'severity', etc.

        Returns:
            Flag ID for tracking

        Example:
            memory.flag_cross_chapter_issue(
                discovered_in=15,
                affects_chapter=1,
                issue={
                    "type": "foreshadowing",
                    "detail": "Ch 1 needs to foreshadow the magic reveal in Ch 15",
                    "severity": "high"
                }
            )
        """
        flag_id = f"flag_{discovered_in}_to_{affects_chapter}_{len(self.context['cross_chapter_flags'])}"

        flag = {
            "id": flag_id,
            "discovered_in": discovered_in,
            "affects_chapter": affects_chapter,
            "issue": issue,
            "status": "open",
            "created_at": datetime.now().isoformat()
        }

        self.context["cross_chapter_flags"].append(flag)

        # Store in Redis list
        flags_key = f"book:{self.book_id}:flags"
        self.redis.lpush(flags_key, json.dumps(flag))

        return flag_id

    def get_unresolved_flags(self) -> List[Dict]:
        """
        Get all flags that haven't been resolved yet.

        Returns:
            List of flag dictionaries with status='open'
        """
        return [
            f for f in self.context["cross_chapter_flags"]
            if f["status"] == "open"
        ]

    def get_flags_for_chapter(self, chapter_number: int) -> List[Dict]:
        """
        Get all flags that affect a specific chapter.

        Args:
            chapter_number: Chapter number to check

        Returns:
            List of flags affecting this chapter
        """
        return [
            f for f in self.context["cross_chapter_flags"]
            if f["affects_chapter"] == chapter_number and f["status"] == "open"
        ]

    def resolve_flag(self, flag_id: str):
        """
        Mark a flag as resolved.

        Args:
            flag_id: The flag ID to resolve
        """
        for flag in self.context["cross_chapter_flags"]:
            if flag["id"] == flag_id:
                flag["status"] = "resolved"
                flag["resolved_at"] = datetime.now().isoformat()

                # Update in Redis
                flags_key = f"book:{self.book_id}:flags"
                all_flags = self.redis.lrange(flags_key, 0, -1)
                self.redis.delete(flags_key)

                for f in all_flags:
                    flag_dict = json.loads(f)
                    if flag_dict["id"] == flag_id:
                        flag_dict["status"] = "resolved"
                        flag_dict["resolved_at"] = datetime.now().isoformat()
                    self.redis.lpush(flags_key, json.dumps(flag_dict))

                break

    def store_continuity_fact(self, category: str, key: str, value: Any):
        """
        Store a continuity fact (character trait, magic rule, timeline event).

        Args:
            category: 'character', 'magic', 'timeline', etc.
            key: Identifier for the fact
            value: The fact data
        """
        if category not in self.context["continuity_db"]:
            self.context["continuity_db"][category] = {}

        self.context["continuity_db"][category][key] = value

        # Store in Redis
        continuity_key = f"book:{self.book_id}:continuity:{category}"
        self.redis.hset(continuity_key, key, json.dumps(value))

    def get_continuity_facts(self, category: str) -> Dict:
        """
        Get all continuity facts for a category.

        Args:
            category: 'character', 'magic', 'timeline', etc.

        Returns:
            Dictionary of facts in this category
        """
        return self.context["continuity_db"].get(category, {})

    def increment_iteration(self) -> int:
        """
        Increment and return the iteration counter.
        Used for safety guards (max 50 iterations).

        Returns:
            New iteration count
        """
        self.context["iteration_count"] += 1
        iter_key = f"book:{self.book_id}:iteration_count"
        self.redis.incr(iter_key)
        return self.context["iteration_count"]

    def get_iteration_count(self) -> int:
        """Get current iteration count."""
        return self.context["iteration_count"]

    def clear(self):
        """Clear all data for this book from memory and Redis."""
        # Clear Redis keys
        pattern = f"book:{self.book_id}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)

        # Clear in-memory context
        self.context = {
            "manuscript": None,
            "chapters": {},
            "chapter_analyses": {},
            "cross_chapter_flags": [],
            "continuity_db": {},
            "task_states": {},
            "iteration_count": 0
        }

    def get_story_contract(self) -> GlobalStoryContract:
        """
        Get the global story contract.

        Returns:
            GlobalStoryContract instance
        """
        return self.story_contract

    def save_story_contract(self):
        """Save the story contract to Redis."""
        contract_key = f"book:{self.book_id}:story_contract"
        self.redis.set(contract_key, self.story_contract.to_json())

    def initialize_story_contract_from_manuscript(self):
        """
        Initialize story contract by analyzing the manuscript.

        This should be called after loading all chapters and before parallel processing.
        Extracts POV, voice, pacing rules from the existing manuscript.
        """
        # This is a placeholder - in production, would analyze manuscript
        # For now, set some sensible defaults for romantasy

        self.story_contract.set_pov(
            pov_type="third_limited",
            perspective="alternating",  # FMC/MMC
            tense="past",
            rules=["no head hopping within chapter", "clear POV transitions"]
        )

        self.story_contract.set_romance_rules(
            romance_type="enemies_to_lovers",
            escalation_ladder={
                "chapters_1_3": "antagonistic_tension",
                "chapters_4_6": "grudging_respect_and_banter",
                "chapters_7_9": "emotional_vulnerability",
                "chapters_10_12": "undeniable_attraction",
                "chapters_13_15": "commitment_and_HEA"
            },
            boundaries=["fade_to_black", "no_explicit_content"]
        )

        self.story_contract.set_magic_system(
            magic_type="elemental_with_cost",
            rules=[
                "magic powered by emotion",
                "physical cost proportional to power used",
                "requires concentration and intent"
            ],
            limitations=[
                "drains user energy",
                "can backfire if emotionally unstable",
                "requires training to control"
            ],
            reveal_schedule={
                "chapters_1_5": [
                    "magic exists in world",
                    "FMC has dormant power",
                    "basic magical concepts"
                ],
                "chapters_6_10": [
                    "FMC power awakens",
                    "first successful magic use",
                    "power limitations revealed"
                ],
                "chapters_11_15": [
                    "full powers manifested",
                    "true nature of magic revealed",
                    "connection to MMC powers"
                ]
            }
        )

        # Save to Redis
        self.save_story_contract()

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current memory usage.

        Returns:
            Dictionary with stats (chapters stored, flags count, etc.)
        """
        return {
            "book_id": self.book_id,
            "chapters_stored": len(self.context["chapters"]),
            "total_flags": len(self.context["cross_chapter_flags"]),
            "unresolved_flags": len(self.get_unresolved_flags()),
            "iteration_count": self.context["iteration_count"],
            "continuity_categories": list(self.context["continuity_db"].keys()),
            "story_contract_version": self.story_contract.contract.get("version", "not_set")
        }
