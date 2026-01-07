"""
Chapter Context Loader Tool for accessing chapter content and metadata.
Enables agents to read and understand chapter context.
"""

from typing import Optional, List
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
import json


class LoadChapterInput(BaseModel):
    """Input schema for loading a chapter."""
    chapter_number: int = Field(..., description="Chapter number to load (1-15)")
    include_metadata: bool = Field(True, description="Include metadata like word count (default: True)")


class ChapterContextLoaderTool(BaseTool):
    """
    Tool for loading chapter content and metadata.

    Agents use this to read chapters before analyzing or editing them.
    """

    name: str = "Load Chapter"
    description: str = """
    Load the content and metadata for a specific chapter.
    Use this to read a chapter before analyzing or editing it.

    Returns the chapter text and optional metadata (word count, scene count, etc.).

    Input:
    - chapter_number: Which chapter to load (1-15)
    - include_metadata: Whether to include metadata (default: True)
    """
    args_schema: type[BaseModel] = LoadChapterInput

    def __init__(self, manuscript_memory):
        """
        Initialize with manuscript memory.

        Args:
            manuscript_memory: ManuscriptMemory instance
        """
        super().__init__()
        self.memory = manuscript_memory

    def _run(
        self,
        chapter_number: int,
        include_metadata: bool = True
    ) -> str:
        """
        Load a chapter.

        Returns:
            Chapter text with optional metadata
        """
        if not (1 <= chapter_number <= 15):
            return f"Error: chapter_number must be between 1-15, got {chapter_number}"

        chapter_data = self.memory.get_chapter(chapter_number)

        if not chapter_data:
            return f"Error: Chapter {chapter_number} not found in memory"

        result = [f"Chapter {chapter_number}\n", "=" * 60, "\n\n"]

        if include_metadata and chapter_data.get('metadata'):
            metadata = chapter_data['metadata']
            result.append("Metadata:\n")
            for key, value in metadata.items():
                result.append(f"  {key}: {value}\n")
            result.append("\n")

        result.append("Content:\n")
        result.append(chapter_data['text'])

        return "".join(result)


class LoadMultipleChaptersInput(BaseModel):
    """Input schema for loading multiple chapters."""
    chapter_numbers: List[int] = Field(..., description="List of chapter numbers to load (e.g., [1, 5, 10])")
    summary_only: bool = Field(False, description="Only return summaries, not full text (default: False)")


class LoadMultipleChaptersTool(BaseTool):
    """
    Tool for loading multiple chapters at once.

    Useful for understanding context across chapters.
    """

    name: str = "Load Multiple Chapters"
    description: str = """
    Load multiple chapters at once.
    Use this when you need context from multiple chapters.

    Input:
    - chapter_numbers: List of chapter numbers [1, 5, 10]
    - summary_only: If True, returns just metadata (default: False)
    """
    args_schema: type[BaseModel] = LoadMultipleChaptersInput

    def __init__(self, manuscript_memory):
        """
        Initialize with manuscript memory.

        Args:
            manuscript_memory: ManuscriptMemory instance
        """
        super().__init__()
        self.memory = manuscript_memory

    def _run(
        self,
        chapter_numbers: List[int],
        summary_only: bool = False
    ) -> str:
        """
        Load multiple chapters.

        Returns:
            Formatted content from multiple chapters
        """
        if not chapter_numbers:
            return "Error: Must provide at least one chapter number"

        if any(ch < 1 or ch > 15 for ch in chapter_numbers):
            return "Error: All chapter numbers must be between 1-15"

        result = [f"Loading {len(chapter_numbers)} chapters: {chapter_numbers}\n\n"]

        for ch_num in sorted(chapter_numbers):
            chapter_data = self.memory.get_chapter(ch_num)

            if not chapter_data:
                result.append(f"[Chapter {ch_num}: Not found]\n\n")
                continue

            result.append(f"--- Chapter {ch_num} ---\n")

            if chapter_data.get('metadata'):
                metadata = chapter_data['metadata']
                result.append(f"Word count: {metadata.get('word_count', 'N/A')}\n")

            if not summary_only:
                text = chapter_data['text']
                # Truncate if very long
                if len(text) > 2000:
                    result.append(f"\n{text[:2000]}...\n[Truncated]\n\n")
                else:
                    result.append(f"\n{text}\n\n")
            else:
                result.append(f"[Summary only - use Load Chapter for full text]\n\n")

        return "".join(result)


class GetContinuityFactsInput(BaseModel):
    """Input schema for getting continuity facts."""
    category: str = Field(..., description="Category: 'character', 'magic', 'timeline', 'world'")


class GetContinuityFactsTool(BaseTool):
    """
    Tool for retrieving continuity facts.

    Agents use this to check established facts about characters,
    magic system, timeline, etc.
    """

    name: str = "Get Continuity Facts"
    description: str = """
    Get established continuity facts for a category.
    Use this to check what's already established about characters,
    magic rules, timeline events, etc.

    Categories:
    - character: Character traits, descriptions, relationships
    - magic: Magic system rules, limitations, costs
    - timeline: Important dates and event sequence
    - world: World-building details, geography, culture

    Input:
    - category: Which category to retrieve
    """
    args_schema: type[BaseModel] = GetContinuityFactsInput

    def __init__(self, manuscript_memory):
        """
        Initialize with manuscript memory.

        Args:
            manuscript_memory: ManuscriptMemory instance
        """
        super().__init__()
        self.memory = manuscript_memory

    def _run(self, category: str) -> str:
        """
        Get continuity facts.

        Returns:
            Formatted list of facts in the category
        """
        valid_categories = ['character', 'magic', 'timeline', 'world']
        if category not in valid_categories:
            return f"Error: category must be one of {valid_categories}, got '{category}'"

        facts = self.memory.get_continuity_facts(category)

        if not facts:
            return f"No continuity facts established yet for category: {category}"

        result = [
            f"Continuity Facts - {category.title()}\n",
            "=" * 60,
            "\n\n"
        ]

        for key, value in facts.items():
            if isinstance(value, dict):
                result.append(f"{key}:\n")
                for k, v in value.items():
                    result.append(f"  {k}: {v}\n")
            else:
                result.append(f"{key}: {value}\n")
            result.append("\n")

        return "".join(result)


class StoreContinuityFactInput(BaseModel):
    """Input schema for storing continuity facts."""
    category: str = Field(..., description="Category: 'character', 'magic', 'timeline', 'world'")
    key: str = Field(..., description="Identifier for the fact")
    value: str = Field(..., description="The fact value")


class StoreContinuityFactTool(BaseTool):
    """
    Tool for storing continuity facts.

    Agents use this to record important facts that need to be
    consistent across chapters.
    """

    name: str = "Store Continuity Fact"
    description: str = """
    Store a continuity fact for future reference.
    Use this to record important details that must stay consistent.

    Examples:
    - Store character eye color: category='character', key='protagonist_eyes', value='emerald green'
    - Store magic rule: category='magic', key='healing_cost', value='user feels recipient pain'
    - Store timeline event: category='timeline', key='coronation_date', value='Spring Festival, Year 1023'

    Input:
    - category: 'character', 'magic', 'timeline', 'world'
    - key: Identifier
    - value: The fact
    """
    args_schema: type[BaseModel] = StoreContinuityFactInput

    def __init__(self, manuscript_memory):
        """
        Initialize with manuscript memory.

        Args:
            manuscript_memory: ManuscriptMemory instance
        """
        super().__init__()
        self.memory = manuscript_memory

    def _run(
        self,
        category: str,
        key: str,
        value: str
    ) -> str:
        """
        Store a continuity fact.

        Returns:
            Success message
        """
        valid_categories = ['character', 'magic', 'timeline', 'world']
        if category not in valid_categories:
            return f"Error: category must be one of {valid_categories}, got '{category}'"

        if not key or not value:
            return "Error: Both key and value are required"

        self.memory.store_continuity_fact(category, key, value)

        return (
            f"✓ Continuity fact stored!\n"
            f"Category: {category}\n"
            f"Key: {key}\n"
            f"Value: {value}\n\n"
            f"This fact will be checked for consistency across all chapters."
        )


class GetAllChapterSummariesInput(BaseModel):
    """Input schema for getting all chapter summaries."""
    pass


class GetAllChapterSummariesTool(BaseTool):
    """
    Tool for getting a quick overview of all chapters.

    Useful for the Manuscript Strategist to understand the full manuscript.
    """

    name: str = "Get All Chapter Summaries"
    description: str = """
    Get a quick overview of all stored chapters.
    Use this to understand the full manuscript structure.

    Returns chapter numbers, word counts, and brief previews.
    """
    args_schema: type[BaseModel] = GetAllChapterSummariesInput

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
        Get all chapter summaries.

        Returns:
            Formatted overview of all chapters
        """
        all_chapters = self.memory.get_all_chapters()

        if not all_chapters:
            return "No chapters loaded in memory yet."

        result = [
            f"Manuscript Overview\n",
            "=" * 60,
            f"\nTotal Chapters: {len(all_chapters)}\n\n"
        ]

        total_words = 0

        for ch_num in sorted(all_chapters.keys()):
            chapter_data = all_chapters[ch_num]
            text = chapter_data['text']
            word_count = chapter_data.get('metadata', {}).get('word_count', len(text.split()))
            total_words += word_count

            # Get first 100 characters as preview
            preview = text[:100].replace('\n', ' ')

            result.append(
                f"Ch {ch_num:2d}: {word_count:5d} words | {preview}...\n"
            )

        result.append(f"\n{'=' * 60}\n")
        result.append(f"Total: {total_words:,} words\n")

        return "".join(result)
