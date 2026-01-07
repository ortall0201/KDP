"""
Vector Memory Search Tool for querying long-term memory.
Enables agents to learn from previous successful work.
"""

from typing import Optional
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
import json


class SearchSimilarScenesInput(BaseModel):
    """Input schema for searching similar scenes."""
    query_text: str = Field(..., description="Description of the scene you're writing")
    scene_type: Optional[str] = Field(None, description="Optional scene type filter: 'banter', 'action', 'romance', 'tension'")
    n_results: int = Field(3, description="Number of similar scenes to retrieve (default: 3)")


class VectorMemorySearchTool(BaseTool):
    """
    Tool for searching similar high-quality scenes from previous books.

    Agents use this to find examples of successful scenes when writing.
    Only returns scenes with quality score ≥9.

    Example:
        Agent writing a banter scene searches for similar high-quality
        banter scenes from previous books to learn the style.
    """

    name: str = "Search Similar Scenes"
    description: str = """
    Search for similar high-quality scenes from previous books.
    Use this when writing a new scene to find successful examples.

    Only returns scenes with quality score ≥9 from long-term memory.

    Examples:
    - Writing banter → search for "witty argument between characters"
    - Writing action → search for "sword fight in tavern"
    - Writing romance → search for "first kiss moment"

    Input:
    - query_text: Description of what you're writing
    - scene_type: Optional filter (banter/action/romance/tension)
    - n_results: How many examples to get (default 3)
    """
    args_schema: type[BaseModel] = SearchSimilarScenesInput

    def __init__(self, long_term_memory):
        """
        Initialize with long-term memory.

        Args:
            long_term_memory: GhostwriterLongTermMemory instance
        """
        super().__init__()
        self.ltm = long_term_memory

    def _run(
        self,
        query_text: str,
        scene_type: Optional[str] = None,
        n_results: int = 3
    ) -> str:
        """
        Search for similar high-quality scenes.

        Returns:
            Formatted results with scene text and metadata
        """
        if not query_text or len(query_text) < 10:
            return "Error: query_text must be at least 10 characters"

        if n_results < 1 or n_results > 10:
            return "Error: n_results must be between 1 and 10"

        # Search long-term memory
        try:
            similar_scenes = self.ltm.retrieve_similar_scenes(
                query_text=query_text,
                scene_type=scene_type,
                min_quality=9.0,
                n_results=n_results
            )
        except Exception as e:
            return f"Error searching long-term memory: {str(e)}"

        if not similar_scenes:
            return (
                f"No similar high-quality scenes found.\n"
                f"Query: {query_text}\n"
                f"This might be the first time writing this type of scene. "
                f"Write it fresh and it will be stored if quality is ≥9."
            )

        # Format results
        result = [f"Found {len(similar_scenes)} similar high-quality scenes:\n"]

        for i, scene in enumerate(similar_scenes, 1):
            metadata = scene['metadata']
            result.append(
                f"\n--- Scene {i} (Quality: {metadata['quality_score']}/10) ---\n"
                f"Source: Book {metadata['book_id']}, Chapter {metadata['chapter_number']}\n"
                f"Type: {metadata['scene_type']}\n"
                f"Techniques: {metadata.get('techniques', 'N/A')}\n"
                f"Similarity: {(1 - scene['distance']) * 100:.1f}%\n\n"
                f"Scene Text:\n{scene['text'][:500]}...\n"
                f"{'=' * 60}\n"
            )

        result.append(
            f"\nUse these examples to understand the successful patterns, "
            f"but write original content that matches the current story."
        )

        return "".join(result)


class SearchPlotSolutionsInput(BaseModel):
    """Input schema for searching plot solutions."""
    problem_description: str = Field(..., description="Description of the plot problem")
    min_effectiveness: float = Field(7.0, description="Minimum effectiveness score (1-10, default: 7.0)")
    n_results: int = Field(5, description="Number of solutions to retrieve (default: 5)")


class SearchPlotSolutionsTool(BaseTool):
    """
    Tool for searching successful plot fixes from previous books.

    Agents use this when encountering plot problems to see how similar
    issues were successfully resolved before.
    """

    name: str = "Search Plot Solutions"
    description: str = """
    Search for successful solutions to plot problems from previous books.
    Use this when you encounter a plot issue to see how it was fixed before.

    Examples:
    - "Pacing too slow in middle" → find solutions that worked
    - "Character motivation unclear" → find successful fixes
    - "Plot hole in timeline" → find how similar issues were resolved

    Input:
    - problem_description: What's wrong with the plot
    - min_effectiveness: Minimum effectiveness score (default: 7.0)
    - n_results: How many solutions to get (default: 5)
    """
    args_schema: type[BaseModel] = SearchPlotSolutionsInput

    def __init__(self, long_term_memory):
        """
        Initialize with long-term memory.

        Args:
            long_term_memory: GhostwriterLongTermMemory instance
        """
        super().__init__()
        self.ltm = long_term_memory

    def _run(
        self,
        problem_description: str,
        min_effectiveness: float = 7.0,
        n_results: int = 5
    ) -> str:
        """
        Search for plot solutions.

        Returns:
            Formatted solutions with effectiveness ratings
        """
        if not problem_description or len(problem_description) < 10:
            return "Error: problem_description must be at least 10 characters"

        if not (1.0 <= min_effectiveness <= 10.0):
            return "Error: min_effectiveness must be between 1.0 and 10.0"

        # Search long-term memory
        try:
            solutions = self.ltm.find_similar_plot_solutions(
                problem_description=problem_description,
                min_effectiveness=min_effectiveness,
                n_results=n_results
            )
        except Exception as e:
            return f"Error searching plot solutions: {str(e)}"

        if not solutions:
            return (
                f"No similar plot solutions found.\n"
                f"Problem: {problem_description}\n"
                f"This might be a new type of issue. "
                f"Solve it creatively and the solution will be stored for future use."
            )

        # Format results
        result = [f"Found {len(solutions)} similar plot solutions:\n"]

        for i, sol in enumerate(solutions, 1):
            metadata = sol['metadata']
            result.append(
                f"\n--- Solution {i} (Effectiveness: {metadata['effectiveness']}/10) ---\n"
                f"Original Problem: {metadata['problem']}\n"
                f"Solution Applied:\n{sol['solution']}\n"
                f"Source: Book {metadata['book_id']}\n"
                f"Similarity: {(1 - sol['distance']) * 100:.1f}%\n"
                f"{'=' * 60}\n"
            )

        result.append(
            f"\nAdapt these solutions to your specific plot issue. "
            f"Don't copy directly - customize for your story."
        )

        return "".join(result)


class GetNichePatternsInput(BaseModel):
    """Input schema for getting niche patterns."""
    genre: str = Field("romantasy", description="Genre to get patterns for (default: romantasy)")
    min_confidence: float = Field(0.7, description="Minimum confidence threshold (0-1, default: 0.7)")


class GetNichePatternsTool(BaseTool):
    """
    Tool for getting learned genre-specific patterns.

    Agents use this to understand what works in the specific genre
    based on accumulated knowledge from multiple books.
    """

    name: str = "Get Niche Patterns"
    description: str = """
    Get learned patterns for a specific genre (e.g., romantasy).
    Use this to understand what consistently works in this genre.

    After processing 10+ books, the system learns patterns like:
    - "Banter between leads within first 3 chapters" (90% confidence)
    - "HEA (happily ever after) is non-negotiable" (100% confidence)
    - "Magic must have clear cost/limitation" (85% confidence)

    Input:
    - genre: Genre name (default: romantasy)
    - min_confidence: Minimum confidence level (0-1, default: 0.7)
    """
    args_schema: type[BaseModel] = GetNichePatternsInput

    def __init__(self, long_term_memory):
        """
        Initialize with long-term memory.

        Args:
            long_term_memory: GhostwriterLongTermMemory instance
        """
        super().__init__()
        self.ltm = long_term_memory

    def _run(
        self,
        genre: str = "romantasy",
        min_confidence: float = 0.7
    ) -> str:
        """
        Get niche patterns.

        Returns:
            Formatted list of high-confidence patterns
        """
        if not (0.0 <= min_confidence <= 1.0):
            return "Error: min_confidence must be between 0.0 and 1.0"

        # Get patterns from long-term memory
        try:
            analysis = self.ltm.analyze_niche_patterns(genre=genre)
        except Exception as e:
            return f"Error getting niche patterns: {str(e)}"

        if analysis['high_confidence_count'] == 0:
            return (
                f"No high-confidence patterns yet for {genre}.\n"
                f"Total patterns: {analysis['total_patterns']}\n"
                f"Process more books to build genre-specific knowledge."
            )

        # Format results
        result = [
            f"Learned Patterns for {genre.title()}\n",
            f"{'=' * 60}\n",
            f"Total patterns discovered: {analysis['total_patterns']}\n",
            f"High-confidence patterns: {analysis['high_confidence_count']}\n\n",
            f"High-Confidence Patterns:\n"
        ]

        for i, pattern in enumerate(analysis['high_confidence'], 1):
            conf_pct = int(pattern['confidence'] * 100)
            result.append(
                f"\n{i}. {pattern['description']}\n"
                f"   Confidence: {conf_pct}%\n"
                f"   Pattern: {pattern['name']}\n"
            )

        result.append(f"\n{'=' * 60}\n")
        result.append(f"\nRecommendations:\n{analysis['recommendations']}")

        return "".join(result)
