# Architecture Explanation Prompt for GPT

Use this prompt with GPT to get a detailed explanation of the architecture:

---

## Prompt

I'm building a CrewAI-based multi-agent system for autonomous fiction ghostwriting. I've completed Week 1 (Infrastructure) and need you to explain the architecture that was implemented.

### Context

**Previous System:**
- n8n workflow with sequential API calls
- 5 phases: Plan → Expand → Polish → Validate → Critique
- Processing: 22,600 words → 47,000 words (Romantasy genre)
- Time: 3 hours (sequential, one chapter at a time)
- No agent reasoning, no memory, no cross-chapter awareness

**Target System:**
- CrewAI multi-agent system with 6 specialized agents
- Non-linear editing (agent on Ch 15 can flag Ch 1 for fixing)
- Dual memory: Redis (short-term) + ChromaDB (long-term learning)
- Async parallel processing (5-10x faster)
- Long-term learning across multiple books in same niche

### What Was Implemented (Week 1)

**1. Short-Term Memory (`manuscript_memory.py`)**
```python
class ManuscriptMemory:
    # Stores during single book processing:
    - All 15 chapters in Redis
    - Cross-chapter flags (Ch 15 → Ch 1 issues)
    - Continuity database (characters, magic, timeline)
    - Iteration counter (safety guard)

    # Key method:
    def flag_cross_chapter_issue(discovered_in, affects_chapter, issue):
        # Agent working on Ch 15 flags issue in Ch 1
        # Creates flag with "open" status
        # Stores in Redis list
```

**2. Long-Term Memory (`long_term_memory.py`)**
```python
class GhostwriterLongTermMemory:
    # ChromaDB collections:
    - style_patterns: High-quality scenes (score ≥9)
    - plot_solutions: Successful plot fixes
    - reader_feedback: Amazon review learnings
    - niche_knowledge: Romantasy-specific patterns

    # Key methods:
    def store_successful_scene(scene_data, quality_score):
        # Store scenes with score ≥9 for future reference

    def retrieve_similar_scenes(query_text, n_results=3):
        # Vector search for similar high-quality examples

    def analyze_niche_patterns(genre="romantasy"):
        # After 10 books: "Banter in first 3 chapters" (90% confidence)
```

**3. Workflow State Manager (`state_manager.py`)**
```python
class WorkflowStateManager:
    # Manages:
    - Task states (pending/blocked/ready/in_progress/complete)
    - Dependencies between tasks
    - Wave-based organization for parallel execution

    # Key feature:
    def add_flag(discovered_in, affects_chapter, issue):
        # Automatically creates fix task with dependency
        # Fix task waits for discovering chapter to complete

    def get_ready_tasks():
        # Returns tasks whose dependencies are satisfied
        # Ready for parallel execution

    def get_tasks_by_wave():
        # Wave 1: Independent tasks (can run in parallel)
        # Wave 2: Tasks depending on Wave 1
        # Wave 3: Tasks depending on Wave 1 or 2
```

**4. Infrastructure**
- Docker Compose with Redis (6379) and ChromaDB (8000)
- Full package structure with proper imports
- Test suite demonstrating all features
- Configuration templates

### Key Architectural Innovation: Non-Linear Editing

**Traditional Sequential Flow:**
```
Ch 1 → Ch 2 → Ch 3 → ... → Ch 15
(Each chapter processed in order, no looking back)
```

**New Non-Linear Flow:**
```
Wave 1: Analyze Ch 1-15 in parallel
        ↓
Agent on Ch 15: "Wait, Ch 1 needs to foreshadow this!"
        ↓
        Creates FLAG: discovered_in=15, affects_chapter=1
        ↓
Wave 2: Process independent chapters
        ↓
Wave 3: Fix Ch 1 (now has context from Ch 15)
```

**How It Works:**

1. **Analysis Phase** - All 15 chapters analyzed simultaneously
2. **Flag Creation** - Agent realizes Ch 1 needs changes based on Ch 15 content
3. **Dependency Graph** - System creates Ch 1 fix task that depends on Ch 15 analysis completing
4. **Ordered Execution** - Ch 1 fix waits for Ch 15 to finish, then executes with full context

### Task Flow Example

**Standard Workflow Initialization:**
```python
state_manager.initialize_standard_workflow(15)
# Creates 4 phases × 15 chapters = 60 tasks:
# - analyze_1 through analyze_15 (no dependencies)
# - expand_1 through expand_15 (each depends on own analyze)
# - polish_1 through polish_15 (each depends on own expand)
# - validate_1 through validate_15 (each depends on own polish)
```

**Adding Cross-Chapter Flag:**
```python
# During analyze_15, agent discovers issue
state_manager.add_flag(
    discovered_in=15,
    affects_chapter=1,
    issue={"type": "foreshadowing", "detail": "..."}
)
# Automatically creates: fix_1 task with dependency on analyze_15
```

**Wave-Based Execution:**
```
Wave 1: analyze_1 through analyze_15 (15 tasks in parallel)
Wave 2: expand_1 through expand_15 (after analyses complete)
        + fix_1 (only after analyze_15 completes)
Wave 3: polish_1 through polish_15
Wave 4: validate_1 through validate_15
```

### Memory Integration

**Short-Term (Per Book):**
```python
memory = ManuscriptMemory("book_001")
memory.store_chapter(15, "Chapter 15 text...")
memory.flag_cross_chapter_issue(15, 1, {...})
# All agents share this memory during book processing
```

**Long-Term (Across Books):**
```python
ltm = GhostwriterLongTermMemory()

# After Book 1: Store successful banter scene
ltm.store_successful_scene(scene_data, quality_score=9.5)

# During Book 2: Find similar examples
similar = ltm.retrieve_similar_scenes("Writing banter...")
# Agent learns from Book 1's success
```

### Safety Guards

**1. Max Iterations:** Prevent infinite loops (limit: 50)
**2. Circular Dependency Detection:** `has_circular_dependency(task_id)`
**3. No Progress Detection:** If no tasks complete in 10 iterations → error
**4. Flag Explosion Guard:** Max 100 open flags

### Future Agents (Week 2-3)

The memory system is ready for these agents:

1. **Manuscript Strategist** (gpt-4o) - Uses ManuscriptMemory to create flags
2. **Scene Architect** (gpt-4o) - Queries LTM for similar high-quality scenes
3. **Continuity Guardian** (gpt-4o-mini) - Checks ManuscriptMemory continuity_db
4. **Line Editor** (gpt-4o) - Polishes text
5. **QA Agent** (claude-sonnet-4-5) - Scores quality, triggers LTM storage
6. **Learning Coordinator** (gpt-4o-mini) - Analyzes LTM patterns

### Questions to Answer

Please explain:

1. **How does the cross-chapter flagging solve the non-linear editing problem?**
   - Why is this better than sequential processing?
   - What specific problem from the old n8n system does this solve?

2. **How does the dependency graph enable parallel execution?**
   - How do waves work?
   - Why is Wave 1 faster than sequential?

3. **How does long-term memory enable learning across books?**
   - What happens after processing 10 romantasy books?
   - How does quality improve over time?

4. **What's the data flow when an agent discovers a cross-chapter issue?**
   - Step-by-step from flag creation to fix execution
   - How does Redis coordinate this?

5. **Why split memory into short-term (Redis) and long-term (ChromaDB)?**
   - What are the performance benefits?
   - What would break if we only had one?

6. **How will the 6 agents interact with this architecture?**
   - Which agents create flags?
   - Which agents consume LTM data?
   - How does the Manuscript Strategist orchestrate everything?

### Code Locations

- Short-term memory: `crewai_ghostwriter/core/memory/manuscript_memory.py`
- Long-term memory: `crewai_ghostwriter/core/memory/long_term_memory.py`
- State manager: `crewai_ghostwriter/core/orchestration/state_manager.py`
- Tests demonstrating features: `tests/test_memory.py`
- Docker setup: `docker/docker-compose.yml`

### Expected Performance

- **Time:** 45 minutes (vs 3 hours sequential)
- **Cost:** $12-18 per book
- **Quality:** 8.5/10 (vs 7.0/10 for n8n)
- **Learning:** Improves with each book in same niche

Please provide a comprehensive architectural explanation covering all these aspects.

---

## Expected Response Structure

GPT should explain:

1. **Problem being solved** (n8n limitations)
2. **Core architectural components** (3 classes + infrastructure)
3. **Non-linear editing innovation** (the "killer feature")
4. **Memory hierarchy** (short vs long term)
5. **Dependency graph mechanics** (waves, parallel execution)
6. **Data flow examples** (concrete scenarios)
7. **Integration with future agents** (how pieces fit together)
8. **Performance benefits** (why 4x faster)

Save this prompt to share with GPT or other team members.
