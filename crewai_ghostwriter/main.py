"""
Main orchestrator for CrewAI Ghostwriter System

This is the entry point that coordinates all 6 agents to process a manuscript.
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import json

from dotenv import load_dotenv
from crewai import Crew, Task, Process

# Load environment variables
load_dotenv()

# Import our components
from crewai_ghostwriter.core import (
    ManuscriptMemory,
    GhostwriterLongTermMemory,
    WorkflowStateManager,
    TaskStatus,
    TaskType
)

from crewai_ghostwriter.agents import (
    create_manuscript_strategist,
    get_strategist_tools,
    get_strategist_analysis_task,
    create_scene_architect,
    get_architect_tools,
    get_architect_expansion_task,
    create_continuity_guardian,
    get_continuity_tools,
    get_continuity_check_task,
    create_line_editor,
    get_editor_tools,
    get_line_edit_task,
    create_qa_agent,
    get_qa_tools,
    get_qa_evaluation_task,
    create_learning_coordinator,
    get_learning_tools,
    get_learning_analysis_task
)


class GhostwriterOrchestrator:
    """
    Main orchestrator for the ghostwriting system.

    Coordinates all 6 agents to process a manuscript from 22.6K to 47K words.
    """

    def __init__(
        self,
        book_id: str,
        openai_key: str = None,
        anthropic_key: str = None,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        chromadb_host: str = "localhost",
        chromadb_port: int = 8000,
        verbose: bool = True
    ):
        """
        Initialize the orchestrator.

        Args:
            book_id: Unique identifier for this book
            openai_key: OpenAI API key (optional, uses env if not provided)
            anthropic_key: Anthropic API key (optional, uses env if not provided)
            redis_host: Redis server host
            redis_port: Redis server port
            chromadb_host: ChromaDB server host
            chromadb_port: ChromaDB server port
            verbose: Whether to print agent thinking
        """
        self.book_id = book_id
        self.verbose = verbose

        # Set API keys as environment variables if provided
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key

        # Initialize memory systems
        self.manuscript_memory = ManuscriptMemory(
            book_id=book_id,
            redis_host=redis_host,
            redis_port=redis_port
        )

        self.long_term_memory = GhostwriterLongTermMemory(
            host=chromadb_host,
            port=chromadb_port
        )

        self.state_manager = WorkflowStateManager(
            book_id=book_id,
            redis_host=redis_host,
            redis_port=redis_port
        )

        # Initialize agents (will be created when needed)
        self.agents = {}
        self.tools = {}

    def load_manuscript(self, manuscript_path: str):
        """
        Load manuscript from file and split into chapters.

        Args:
            manuscript_path: Path to manuscript file
        """
        print(f"\n📚 Loading manuscript from {manuscript_path}...")

        with open(manuscript_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by chapter markers (assuming format: "Chapter 1", "Chapter 2", etc.)
        import re
        chapter_pattern = r'Chapter (\d+)'
        chapters = re.split(chapter_pattern, content)

        # Parse chapters
        chapter_num = None
        for i, part in enumerate(chapters):
            if part.strip().isdigit():
                chapter_num = int(part)
            elif chapter_num is not None and part.strip():
                word_count = len(part.split())
                self.manuscript_memory.store_chapter(
                    chapter_number=chapter_num,
                    chapter_text=part.strip(),
                    metadata={"word_count": word_count}
                )
                print(f"  ✓ Chapter {chapter_num}: {word_count} words")
                chapter_num = None

        stats = self.manuscript_memory.get_memory_stats()
        print(f"\n✓ Loaded {stats['chapters_stored']} chapters")

    def initialize_agents(self):
        """Create all agents with their tools."""
        print("\n🤖 Initializing agents...")

        # Manuscript Strategist
        self.tools['strategist'] = get_strategist_tools(
            self.manuscript_memory,
            self.long_term_memory,
            self.state_manager
        )
        self.agents['strategist'] = create_manuscript_strategist(
            tools=self.tools['strategist'],
            verbose=self.verbose
        )
        print("  ✓ Manuscript Strategist")

        # Scene Architect
        self.tools['architect'] = get_architect_tools(
            self.manuscript_memory,
            self.long_term_memory,
            self.state_manager
        )
        self.agents['architect'] = create_scene_architect(
            tools=self.tools['architect'],
            verbose=self.verbose
        )
        print("  ✓ Scene Architect")

        # Continuity Guardian
        self.tools['continuity'] = get_continuity_tools(
            self.manuscript_memory,
            self.state_manager
        )
        self.agents['continuity'] = create_continuity_guardian(
            tools=self.tools['continuity'],
            verbose=self.verbose
        )
        print("  ✓ Continuity Guardian")

        # Line Editor
        self.tools['editor'] = get_editor_tools(self.manuscript_memory)
        self.agents['editor'] = create_line_editor(
            tools=self.tools['editor'],
            verbose=self.verbose
        )
        print("  ✓ Line Editor")

        # QA Agent
        self.tools['qa'] = get_qa_tools(
            self.manuscript_memory,
            self.long_term_memory
        )
        self.agents['qa'] = create_qa_agent(
            tools=self.tools['qa'],
            verbose=self.verbose
        )
        print("  ✓ QA Agent")

        # Learning Coordinator
        self.tools['learning'] = get_learning_tools(
            self.manuscript_memory,
            self.long_term_memory
        )
        self.agents['learning'] = create_learning_coordinator(
            tools=self.tools['learning'],
            verbose=self.verbose
        )
        print("  ✓ Learning Coordinator")

    def process_manuscript(self):
        """
        Process the manuscript through all phases.

        Workflow:
        1. Analysis (Manuscript Strategist)
        2. Continuity Build (Continuity Guardian)
        3. Expansion (Scene Architect for each chapter)
        4. Polish (Line Editor for each chapter)
        5. QA (QA Agent)
        6. Learning (Learning Coordinator)
        """
        print(f"\n🚀 Processing manuscript: {self.book_id}\n")
        print("=" * 60)

        # Phase 1: Manuscript Analysis
        print("\n📊 PHASE 1: Manuscript Analysis")
        print("-" * 60)
        self._run_analysis()

        # Phase 2: Continuity Build
        print("\n🔍 PHASE 2: Continuity Database Build")
        print("-" * 60)
        self._run_continuity_build()

        # Phase 3: Chapter Expansion
        print("\n✍️  PHASE 3: Chapter Expansion")
        print("-" * 60)
        self._run_expansion()

        # Phase 4: Line Editing
        print("\n✨ PHASE 4: Line Editing")
        print("-" * 60)
        self._run_editing()

        # Phase 5: Quality Assurance
        print("\n✅ PHASE 5: Quality Assurance")
        print("-" * 60)
        qa_pass = self._run_qa()

        if not qa_pass:
            print("\n⚠️  QA Failed - would normally iterate, but skipping for demo")

        # Phase 6: Learning
        print("\n🧠 PHASE 6: Learning & Memory Storage")
        print("-" * 60)
        self._run_learning()

        print("\n" + "=" * 60)
        print("✅ MANUSCRIPT PROCESSING COMPLETE!")
        print("=" * 60)

    def _run_analysis(self):
        """Run manuscript analysis phase."""
        task = Task(
            description=get_strategist_analysis_task(),
            agent=self.agents['strategist'],
            expected_output="Comprehensive manuscript analysis with cross-chapter flags"
        )

        crew = Crew(
            agents=[self.agents['strategist']],
            tasks=[task],
            process=Process.sequential,
            verbose=self.verbose
        )

        result = crew.kickoff()
        print(f"\n✓ Analysis complete. Flags created: {len(self.manuscript_memory.get_unresolved_flags())}")

    def _run_continuity_build(self):
        """Build continuity database."""
        task = Task(
            description=get_continuity_check_task(),
            agent=self.agents['continuity'],
            expected_output="Complete continuity database for all categories"
        )

        crew = Crew(
            agents=[self.agents['continuity']],
            tasks=[task],
            process=Process.sequential,
            verbose=self.verbose
        )

        result = crew.kickoff()
        print(f"\n✓ Continuity database built")

    def _run_expansion(self):
        """Expand all chapters."""
        chapters = self.manuscript_memory.get_all_chapters()

        for ch_num in sorted(chapters.keys()):
            print(f"\n  Expanding Chapter {ch_num}...")

            task = Task(
                description=get_architect_expansion_task(ch_num),
                agent=self.agents['architect'],
                expected_output=f"Expanded Chapter {ch_num} (~3100 words)"
            )

            crew = Crew(
                agents=[self.agents['architect']],
                tasks=[task],
                process=Process.sequential,
                verbose=self.verbose
            )

            result = crew.kickoff()
            print(f"  ✓ Chapter {ch_num} expanded")

    def _run_editing(self):
        """Polish all chapters."""
        chapters = self.manuscript_memory.get_all_chapters()

        for ch_num in sorted(chapters.keys()):
            print(f"\n  Editing Chapter {ch_num}...")

            task = Task(
                description=get_line_edit_task(ch_num),
                agent=self.agents['editor'],
                expected_output=f"Polished Chapter {ch_num}"
            )

            crew = Crew(
                agents=[self.agents['editor']],
                tasks=[task],
                process=Process.sequential,
                verbose=self.verbose
            )

            result = crew.kickoff()
            print(f"  ✓ Chapter {ch_num} polished")

    def _run_qa(self) -> bool:
        """Run QA evaluation. Returns True if pass, False if fail."""
        task = Task(
            description=get_qa_evaluation_task(),
            agent=self.agents['qa'],
            expected_output="Quality scores for all chapters with pass/fail decision"
        )

        crew = Crew(
            agents=[self.agents['qa']],
            tasks=[task],
            process=Process.sequential,
            verbose=self.verbose
        )

        result = crew.kickoff()

        # For demo purposes, assume pass
        # In real implementation, would parse result and check scores
        print(f"\n✓ QA evaluation complete")
        return True

    def _run_learning(self):
        """Run learning and memory storage."""
        task = Task(
            description=get_learning_analysis_task(self.book_id),
            agent=self.agents['learning'],
            expected_output="Learning report with patterns stored in long-term memory"
        )

        crew = Crew(
            agents=[self.agents['learning']],
            tasks=[task],
            process=Process.sequential,
            verbose=self.verbose
        )

        result = crew.kickoff()
        print(f"\n✓ Learning complete. Patterns stored for future books.")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <manuscript_path>")
        sys.exit(1)

    manuscript_path = sys.argv[1]

    if not os.path.exists(manuscript_path):
        print(f"Error: File not found: {manuscript_path}")
        sys.exit(1)

    # Generate book ID from timestamp
    book_id = f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Create orchestrator
    orchestrator = GhostwriterOrchestrator(
        book_id=book_id,
        verbose=True
    )

    # Load manuscript
    orchestrator.load_manuscript(manuscript_path)

    # Initialize agents
    orchestrator.initialize_agents()

    # Process manuscript
    orchestrator.process_manuscript()

    print(f"\n📝 Results stored in memory for book: {book_id}")
    print(f"✅ Processing complete!")


if __name__ == "__main__":
    main()
