"""
Long-term memory system for learning across multiple books.
Uses ChromaDB vector database to store and retrieve patterns, solutions, and feedback.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings


class GhostwriterLongTermMemory:
    """
    Long-term memory for learning across multiple manuscripts.

    Collections:
    - style_patterns: High-quality scenes (score ≥9) for reference
    - plot_solutions: Successful plot fixes and techniques
    - reader_feedback: Amazon review learnings
    - niche_knowledge: Genre-specific wisdom (romantasy patterns)
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        persist_directory: Optional[str] = None
    ):
        """
        Initialize long-term memory with ChromaDB.

        Args:
            host: ChromaDB server host
            port: ChromaDB server port
            persist_directory: Local directory for persistence (if not using server)
        """
        if persist_directory:
            # Local persistent client
            self.client = chromadb.Client(Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            ))
        else:
            # HTTP client connecting to server
            self.client = chromadb.HttpClient(host=host, port=port)

        # Initialize collections
        self.style_patterns = self.client.get_or_create_collection(
            name="style_patterns",
            metadata={"description": "High-quality scenes for style reference"}
        )

        self.plot_solutions = self.client.get_or_create_collection(
            name="plot_solutions",
            metadata={"description": "Successful plot fixes and techniques"}
        )

        self.reader_feedback = self.client.get_or_create_collection(
            name="reader_feedback",
            metadata={"description": "Amazon review learnings"}
        )

        self.niche_knowledge = self.client.get_or_create_collection(
            name="niche_knowledge",
            metadata={"description": "Genre-specific patterns (romantasy)"}
        )

    def store_successful_scene(
        self,
        scene_data: Dict[str, Any],
        book_id: str,
        chapter_number: int,
        quality_score: float
    ):
        """
        Store a high-quality scene (score ≥9) for future reference.

        Args:
            scene_data: Dictionary with 'text', 'type', 'techniques' used
            book_id: Book identifier
            chapter_number: Chapter number
            quality_score: Quality score from QA agent (1-10)

        Example:
            ltm.store_successful_scene(
                scene_data={
                    "text": "...",
                    "type": "banter",
                    "techniques": ["show_dont_tell", "subtext"]
                },
                book_id="book_001",
                chapter_number=3,
                quality_score=9.5
            )
        """
        if quality_score < 9.0:
            return  # Only store high-quality scenes

        scene_id = f"{book_id}_ch{chapter_number}_{datetime.now().timestamp()}"

        metadata = {
            "book_id": book_id,
            "chapter_number": chapter_number,
            "quality_score": quality_score,
            "scene_type": scene_data.get("type", "unknown"),
            "techniques": json.dumps(scene_data.get("techniques", [])),
            "stored_at": datetime.now().isoformat()
        }

        self.style_patterns.add(
            documents=[scene_data["text"]],
            metadatas=[metadata],
            ids=[scene_id]
        )

    def retrieve_similar_scenes(
        self,
        query_text: str,
        scene_type: Optional[str] = None,
        min_quality: float = 9.0,
        n_results: int = 3
    ) -> List[Dict]:
        """
        Find similar high-quality scenes for reference when writing.

        Args:
            query_text: The scene being written (for similarity search)
            scene_type: Optional filter by scene type (e.g., "banter", "action")
            min_quality: Minimum quality score threshold
            n_results: Number of results to return

        Returns:
            List of similar scene dictionaries with metadata

        Example:
            # When writing a banter scene, find similar high-quality examples
            similar = ltm.retrieve_similar_scenes(
                query_text="They argued in the tavern...",
                scene_type="banter",
                n_results=3
            )
        """
        where_filter = {"quality_score": {"$gte": min_quality}}
        if scene_type:
            where_filter["scene_type"] = scene_type

        results = self.style_patterns.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where_filter
        )

        # Format results
        similar_scenes = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                similar_scenes.append({
                    "text": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })

        return similar_scenes

    def store_plot_solution(
        self,
        problem: str,
        solution: str,
        book_id: str,
        effectiveness: float
    ):
        """
        Store a successful plot fix for future reference.

        Args:
            problem: Description of the plot issue
            solution: How it was fixed
            book_id: Book identifier
            effectiveness: How well it worked (1-10)

        Example:
            ltm.store_plot_solution(
                problem="Pacing too slow in middle chapters",
                solution="Added subplot with secondary character conflict",
                book_id="book_001",
                effectiveness=8.5
            )
        """
        solution_id = f"{book_id}_solution_{datetime.now().timestamp()}"

        metadata = {
            "book_id": book_id,
            "problem": problem,
            "effectiveness": effectiveness,
            "stored_at": datetime.now().isoformat()
        }

        # Store the solution text
        self.plot_solutions.add(
            documents=[solution],
            metadatas=[metadata],
            ids=[solution_id]
        )

    def find_similar_plot_solutions(
        self,
        problem_description: str,
        min_effectiveness: float = 7.0,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Find similar plot problems and their solutions.

        Args:
            problem_description: Description of current plot issue
            min_effectiveness: Minimum effectiveness threshold
            n_results: Number of results to return

        Returns:
            List of similar solutions with metadata
        """
        results = self.plot_solutions.query(
            query_texts=[problem_description],
            n_results=n_results,
            where={"effectiveness": {"$gte": min_effectiveness}}
        )

        solutions = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                solutions.append({
                    "solution": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })

        return solutions

    def store_reader_feedback(
        self,
        book_id: str,
        feedback_text: str,
        rating: float,
        category: str,
        actionable_insight: str
    ):
        """
        Store learnings from Amazon reviews.

        Args:
            book_id: Book identifier
            feedback_text: The review text
            rating: Star rating (1-5)
            category: 'pacing', 'characters', 'plot', 'romance', etc.
            actionable_insight: What to do differently next time

        Example:
            ltm.store_reader_feedback(
                book_id="book_001",
                feedback_text="Loved the banter but wanted more world-building",
                rating=4.0,
                category="world_building",
                actionable_insight="Add more world-building in first 3 chapters"
            )
        """
        feedback_id = f"{book_id}_feedback_{datetime.now().timestamp()}"

        metadata = {
            "book_id": book_id,
            "rating": rating,
            "category": category,
            "actionable_insight": actionable_insight,
            "stored_at": datetime.now().isoformat()
        }

        self.reader_feedback.add(
            documents=[feedback_text],
            metadatas=[metadata],
            ids=[feedback_id]
        )

    def get_feedback_by_category(
        self,
        category: str,
        min_rating: float = 3.0,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get reader feedback for a specific category.

        Args:
            category: Feedback category
            min_rating: Minimum rating threshold
            limit: Maximum number of results

        Returns:
            List of feedback with insights
        """
        results = self.reader_feedback.query(
            query_texts=[category],
            n_results=limit,
            where={
                "category": category,
                "rating": {"$gte": min_rating}
            }
        )

        feedback_list = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                feedback_list.append({
                    "text": doc,
                    "metadata": results["metadatas"][0][i]
                })

        return feedback_list

    def store_niche_pattern(
        self,
        pattern_name: str,
        pattern_description: str,
        confidence: float,
        evidence_count: int,
        genre: str = "romantasy"
    ):
        """
        Store a discovered genre-specific pattern.

        Args:
            pattern_name: Short name for the pattern
            pattern_description: Detailed description
            confidence: How confident we are (0-1)
            evidence_count: Number of books supporting this
            genre: Genre (default: romantasy)

        Example:
            ltm.store_niche_pattern(
                pattern_name="banter_early",
                pattern_description="Banter between leads within first 3 chapters",
                confidence=0.90,
                evidence_count=9,
                genre="romantasy"
            )
        """
        pattern_id = f"{genre}_{pattern_name}"

        metadata = {
            "pattern_name": pattern_name,
            "confidence": confidence,
            "evidence_count": evidence_count,
            "genre": genre,
            "stored_at": datetime.now().isoformat()
        }

        # Upsert (update if exists, insert if not)
        try:
            self.niche_knowledge.delete(ids=[pattern_id])
        except:
            pass

        self.niche_knowledge.add(
            documents=[pattern_description],
            metadatas=[metadata],
            ids=[pattern_id]
        )

    def get_niche_patterns(
        self,
        genre: str = "romantasy",
        min_confidence: float = 0.7
    ) -> List[Dict]:
        """
        Get all high-confidence patterns for a genre.

        Args:
            genre: Genre to retrieve patterns for
            min_confidence: Minimum confidence threshold

        Returns:
            List of patterns with metadata
        """
        # Get all patterns for genre
        results = self.niche_knowledge.get(
            where={
                "genre": genre,
                "confidence": {"$gte": min_confidence}
            }
        )

        patterns = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                patterns.append({
                    "description": doc,
                    "metadata": results["metadatas"][i]
                })

        return patterns

    def analyze_niche_patterns(self, genre: str = "romantasy") -> Dict[str, Any]:
        """
        Analyze and summarize all learned patterns for a genre.

        Args:
            genre: Genre to analyze

        Returns:
            Dictionary with pattern analysis

        Example output:
            {
                "total_patterns": 15,
                "high_confidence": [
                    {"name": "banter_early", "confidence": 0.90},
                    {"name": "hea_required", "confidence": 1.00}
                ],
                "recommendations": "Focus on banter in first 3 chapters..."
            }
        """
        patterns = self.get_niche_patterns(genre, min_confidence=0.0)

        high_confidence = [
            {
                "name": p["metadata"]["pattern_name"],
                "confidence": p["metadata"]["confidence"],
                "description": p["description"]
            }
            for p in patterns
            if p["metadata"]["confidence"] >= 0.8
        ]

        # Sort by confidence
        high_confidence.sort(key=lambda x: x["confidence"], reverse=True)

        return {
            "genre": genre,
            "total_patterns": len(patterns),
            "high_confidence_count": len(high_confidence),
            "high_confidence": high_confidence,
            "recommendations": self._generate_recommendations(high_confidence)
        }

    def _generate_recommendations(self, high_confidence_patterns: List[Dict]) -> str:
        """Generate text recommendations from high-confidence patterns."""
        if not high_confidence_patterns:
            return "No high-confidence patterns yet. Process more books to build knowledge."

        recommendations = []
        for pattern in high_confidence_patterns[:5]:  # Top 5
            conf_pct = int(pattern["confidence"] * 100)
            recommendations.append(
                f"- {pattern['description']} ({conf_pct}% confidence)"
            )

        return "\n".join(recommendations)

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about long-term memory usage.

        Returns:
            Dictionary with collection counts and stats
        """
        return {
            "style_patterns_count": self.style_patterns.count(),
            "plot_solutions_count": self.plot_solutions.count(),
            "reader_feedback_count": self.reader_feedback.count(),
            "niche_patterns_count": self.niche_knowledge.count(),
            "total_documents": (
                self.style_patterns.count() +
                self.plot_solutions.count() +
                self.reader_feedback.count() +
                self.niche_knowledge.count()
            )
        }

    def clear_all(self):
        """WARNING: Delete all collections. Use with caution!"""
        self.client.delete_collection("style_patterns")
        self.client.delete_collection("plot_solutions")
        self.client.delete_collection("reader_feedback")
        self.client.delete_collection("niche_knowledge")

        # Recreate empty collections
        self.__init__()
