# Getting Started with CrewAI Ghostwriter

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd C:\Users\user\Desktop\KDP\crewai_ghostwriter
pip install -r requirements.txt
```

### 2. Start Infrastructure

The system requires Redis (short-term memory) and ChromaDB (long-term memory).

```bash
cd C:\Users\user\Desktop\KDP\docker
docker-compose up -d
```

Verify services are running:
```bash
docker-compose ps
```

You should see:
- `ghostwriter_redis` on port 6379
- `ghostwriter_chromadb` on port 8000

### 3. Configure Environment

```bash
cd C:\Users\user\Desktop\KDP\crewai_ghostwriter
cp .env.example .env
```

Edit `.env` and add your API keys:
- Get OpenAI key from: https://platform.openai.com/api-keys
- Get Anthropic key from: https://console.anthropic.com/

### 4. Run Tests

Verify the memory system works:

```bash
python tests/test_memory.py
```

You should see:
```
ALL TESTS PASSED ✓

Key Features Demonstrated:
1. ✓ Non-linear editing via cross-chapter flags
2. ✓ Automatic fix task creation from flags
3. ✓ Dependency-aware task scheduling
4. ✓ Wave-based parallel execution
5. ✓ Circular dependency detection
```

## Understanding the System

### What's Been Built (Week 1)

**Infrastructure** ✓
- Redis for short-term memory (per-book context)
- ChromaDB for long-term memory (cross-book learning)
- Docker Compose setup for easy deployment

**Core Components** ✓
1. `ManuscriptMemory` - Stores chapters, flags cross-chapter issues
2. `GhostwriterLongTermMemory` - Learns from successful scenes
3. `WorkflowStateManager` - Tracks tasks and dependencies

**Key Innovation** ✓
- Non-linear editing: Agent on Ch 15 can flag Ch 1 for fixing
- System automatically creates fix task with proper dependencies

### What's Next (Week 2+)

**Agents** (Week 2-3)
- Manuscript Strategist (analyzes, creates plans)
- Scene Architect (writes scenes)
- Continuity Guardian (checks consistency)
- Line Editor (polishes prose)
- QA Agent (scores quality)
- Learning Coordinator (improves over time)

**Orchestration** (Week 4)
- Parallel executor (5-10x faster)
- Safety guards (prevent infinite loops)
- Crash recovery

## Testing the Core Features

### Example 1: Cross-Chapter Flagging

```python
from crewai_ghostwriter.core import ManuscriptMemory

# Initialize
memory = ManuscriptMemory("test_book")

# Store chapters
memory.store_chapter(1, "Chapter 1 content...", {"word_count": 1500})
memory.store_chapter(15, "Chapter 15 content...", {"word_count": 1600})

# Agent working on Ch 15 flags Ch 1
flag_id = memory.flag_cross_chapter_issue(
    discovered_in=15,
    affects_chapter=1,
    issue={
        "type": "foreshadowing",
        "detail": "Need to foreshadow the magic reveal",
        "severity": "high"
    }
)

# Check what needs fixing
flags = memory.get_flags_for_chapter(1)
print(f"Chapter 1 has {len(flags)} issues to fix")

# Cleanup
memory.clear()
```

### Example 2: Dependency Tracking

```python
from crewai_ghostwriter.core import WorkflowStateManager

# Initialize
state = WorkflowStateManager("test_book")

# Create standard workflow (all 15 chapters)
state.initialize_standard_workflow(num_chapters=15)

# Add cross-chapter flag (creates fix task automatically)
state.add_flag(
    discovered_in=15,
    affects_chapter=1,
    issue={"type": "continuity", "detail": "Character eye color"}
)

# See what's ready to run in parallel
ready = state.get_ready_tasks()
print(f"{len(ready)} tasks ready for Wave 1")

# Organize into waves
waves = state.get_tasks_by_wave()
for wave_num, tasks in waves.items():
    print(f"Wave {wave_num}: {len(tasks)} tasks")

# Cleanup
state.clear()
```

### Example 3: Long-Term Learning

```python
from crewai_ghostwriter.core import GhostwriterLongTermMemory

# Initialize
ltm = GhostwriterLongTermMemory()

# Store successful scene
ltm.store_successful_scene(
    scene_data={
        "text": "They argued in the tavern...",
        "type": "banter",
        "techniques": ["show_dont_tell", "subtext"]
    },
    book_id="book_001",
    chapter_number=3,
    quality_score=9.5
)

# Later, when writing new book, find similar scenes
similar = ltm.retrieve_similar_scenes(
    query_text="Two characters arguing...",
    scene_type="banter",
    n_results=3
)

print(f"Found {len(similar)} similar high-quality scenes")
```

## Troubleshooting

### Redis Connection Error

If you see "Connection refused to Redis":
```bash
cd C:\Users\user\Desktop\KDP\docker
docker-compose up -d redis
```

### ChromaDB Connection Error

If you see "Connection refused to ChromaDB":
```bash
cd C:\Users\user\Desktop\KDP\docker
docker-compose up -d chromadb
```

### Check Docker Logs

```bash
docker-compose logs redis
docker-compose logs chromadb
```

### Stop Services

```bash
docker-compose down
```

## Next Steps

1. **Week 1 is complete!** Infrastructure and core memory system working
2. **Week 2-3**: Implement the 6 agents
3. **Week 4**: Add parallel execution
4. **Test with real manuscript**: Use the 22.6K word romantasy manuscript

## Resources

- Plan document: `C:\Users\user\.claude\plans\glimmering-bubbling-floyd.md`
- Test script: `tests/test_memory.py`
- Docker config: `docker/docker-compose.yml`

## Questions?

Refer to the comprehensive plan at:
`C:\Users\user\.claude\plans\glimmering-bubbling-floyd.md`
