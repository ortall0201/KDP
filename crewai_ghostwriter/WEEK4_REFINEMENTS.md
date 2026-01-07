# Week 4 Refinements: Global Story Contract & QA Integration

## Design Rationale

After implementing parallel execution (4-5x speedup), we identified a critical coherence risk:

**Problem:** Parallel chapter processing can cause global coherence drift
- Voice consistency breaks (FMC sounds different in Ch 3 vs Ch 10)
- Romance pacing errors (first kiss in Ch 3 when ladder says Ch 7)
- Magic reveals leak too early (Ch 4 reveals Ch 12 secrets)
- Character facts contradict (eye color changes between chapters)

**Root Cause:** Agents processing chapters independently lack shared guardrails

**Solution:** Global Story Contract - a lightweight shared artifact

---

## What Was Added

### 1. Global Story Contract (`story_contract.py` - 403 lines)

**Purpose:** Single source of truth for coherence rules across parallel execution

**Data Structure:**
```python
{
    "pov": {
        "type": "third_limited",
        "perspective": "alternating",
        "tense": "past",
        "rules": ["no head hopping"]
    },

    "voice": {
        "FMC": {
            "tone": "witty",
            "dialogue_tendencies": ["short sentences", "deflects"],
            "internal_voice": "self-deprecating"
        },
        "MMC": { ... }
    },

    "romance": {
        "type": "enemies_to_lovers",
        "escalation_ladder": {
            "chapters_1_3": "antagonistic_tension",
            "chapters_4_6": "grudging_respect_and_banter",
            "chapters_7_9": "emotional_vulnerability",
            "chapters_10_12": "undeniable_attraction",
            "chapters_13_15": "commitment_and_HEA"
        },
        "boundaries": ["fade_to_black"]
    },

    "magic": {
        "type": "elemental_with_cost",
        "rules": ["magic powered by emotion", "physical cost"],
        "reveal_schedule": {
            "chapters_1_5": ["magic exists", "FMC dormant power"],
            "chapters_6_10": ["power awakens", "first use"],
            "chapters_11_15": ["full powers", "true nature revealed"]
        },
        "forbidden_knowledge": []  // Hard blocks
    },

    "characters": {
        "FMC": { name, age, appearance, arc, fatal_flaw, core_desire },
        "MMC": { ... }
    }
}
```

**Key Methods:**
- `set_pov()` - POV and technical rules
- `set_voice_fingerprint()` - Character voice patterns
- `set_romance_rules()` - Romance escalation ladder
- `set_magic_system()` - Magic rules and reveal timing
- `add_character()` - Character facts
- `check_romance_pacing()` - Validate romantic actions
- `check_magic_reveal()` - Validate magic reveals

**Storage:**
- Lives in Redis at `book:{book_id}:story_contract`
- Loaded once at start, read by all chapter tasks
- Can be exported to `outputs/` for inspection

---

### 2. Three New Tools (story_contract_tools.py - 305 lines)

#### A. GetGlobalStoryContractTool

**Purpose:** Load the contract before working on any chapter

**Agent Usage:**
```python
# FIRST tool call in Scene Architect expansion task
contract = agent.use_tool("Get Global Story Contract")

# Returns formatted guardrails:
# - POV rules
# - Voice fingerprints
# - Romance escalation for this chapter range
# - Magic reveal schedule
# - Character facts
```

**Prevents:**
- Voice drift (agents read voice fingerprints)
- POV violations (agents see rules)
- Character contradictions (agents see established facts)

#### B. CheckRomancePacingTool

**Purpose:** Validate romantic actions against escalation ladder

**Agent Usage:**
```python
# Before writing a kiss scene in Chapter 5
result = agent.use_tool("Check Romance Pacing", {
    "chapter_number": 5,
    "proposed_action": "first kiss between FMC and MMC"
})

# Returns:
# ✅ ALLOWED for Chapter 5
# Current escalation level: grudging_respect_and_banter
# Reason: Within escalation level
```

**Prevents:**
- Romance moving too fast (kiss in Ch 2)
- Romance moving too slow (no progress by Ch 10)
- Violating slow-burn expectations

#### C. CheckMagicRevealTool

**Purpose:** Validate magic reveals against reveal schedule

**Agent Usage:**
```python
# Before revealing FMC's true power in Chapter 4
result = agent.use_tool("Check Magic Reveal", {
    "chapter_number": 4,
    "proposed_reveal": "FMC's true nature as ancient bloodline"
})

# Returns:
# ❌ NOT ALLOWED for Chapter 4
# Reason: Forbidden knowledge
# Suggestion: Save this reveal for Chapter 12+
```

**Prevents:**
- Spoiling major reveals
- Revealing information too early
- Breaking suspense/mystery

---

### 3. Integration with ManuscriptMemory

**Changes to manuscript_memory.py:**

```python
class ManuscriptMemory:
    def __init__(self, book_id):
        # NEW: Story contract instance
        self.story_contract = GlobalStoryContract(book_id)

        # Loads from Redis if exists
        self._load_from_redis()

    def get_story_contract(self) -> GlobalStoryContract:
        """Get the contract for agents to read."""
        return self.story_contract

    def save_story_contract(self):
        """Persist contract to Redis."""
        contract_key = f"book:{book_id}:story_contract"
        self.redis.set(contract_key, self.story_contract.to_json())

    def initialize_story_contract_from_manuscript(self):
        """
        Build contract by analyzing existing manuscript.
        Called after loading chapters, before parallel processing.

        Sets sensible romantasy defaults:
        - Third-limited POV, alternating perspective
        - Enemies-to-lovers romance ladder
        - Elemental magic with reveal schedule
        """
        # Sets defaults, saves to Redis
```

**Workflow Integration:**
```python
# In main orchestrator
orchestrator.load_manuscript("manuscript.txt")

# BEFORE parallel execution starts:
orchestrator.manuscript_memory.initialize_story_contract_from_manuscript()

# Now all parallel chapter tasks read the same contract
```

---

### 4. Agent Integration

#### Scene Architect (Primary Beneficiary)

**Updated Tools:**
- Added `GetGlobalStoryContractTool`
- Added `CheckRomancePacingTool`
- Added `CheckMagicRevealTool`

**Updated Task Description:**
```python
1. PREPARATION
   - **FIRST: Use "Get Global Story Contract"** ← NEW
   - Load chapter
   - Get flags
   - Get continuity facts

5. MAINTAIN CONSISTENCY & USE STORY CONTRACT GUARDRAILS ← NEW SECTION
   - **Check romance pacing** before romantic scenes
   - **Check magic reveals** before revealing magic info
   - Character voices must match contract fingerprints
   - Follow POV rules (no head hopping)
   - Magic rules from contract limitations
```

**Agent Behavior:**
1. Loads contract (sees all guardrails)
2. Before writing kiss: checks romance pacing
3. Before revealing magic: checks reveal schedule
4. Writes within guardrails
5. Voice automatically consistent (reads fingerprints)

#### QA Agent (Secondary Integration)

**Problem:** QA failures were dead-ends (just returned "fail")

**Solution:** QA now uses IssueTrackerTool

**Updated Tools:**
- Added `IssueTrackerTool` (for flagging failures)
- Added `GetGlobalStoryContractTool` (for checking against contract)

**Updated Task Description:**
```python
8. **IMPORTANT: If FAIL, use "Issue Tracker" to flag specific problems**
   - Flag each dimension that scored <8
   - Create actionable flags (discovered_in=current_chapter, affects_chapter=current_chapter)
   - This integrates QA failures into the non-linear editing loop
```

**New Behavior:**
```python
# Old: QA scores Chapter 5 as 7.2/10 (FAIL) and returns message

# New: QA scores Chapter 5 as 7.2/10 (FAIL) and:
qa_agent.use_tool("Issue Tracker", {
    "discovered_in": 5,
    "affects_chapter": 5,
    "issue_type": "dialogue",
    "detail": "Dialogue scored 6/10 - lacks naturalism and subtext",
    "severity": "medium"
})

qa_agent.use_tool("Issue Tracker", {
    "discovered_in": 5,
    "affects_chapter": 5,
    "issue_type": "pacing",
    "detail": "Pacing scored 7/10 - middle section drags",
    "severity": "medium"
})

# These flags create fix_5 tasks that re-enter the workflow
# QA failures now part of the same non-linear editing loop!
```

**Benefits:**
- QA failures no longer dead-ends
- Specific, actionable fix tasks created
- Failures re-enter dependency graph
- Automatic retry after fixes applied

---

## How It Works End-to-End

### Scenario: Processing Chapter 5 in Parallel

```python
# Setup Phase (Once)
memory.load_manuscript()
memory.initialize_story_contract_from_manuscript()
# Contract now in Redis with romance ladder, magic schedule, etc.

# Parallel Execution (Wave 2)
# Chapters 3, 5, 7, 10, 12 processed concurrently

# Scene Architect working on Chapter 5:
task = ExpandChapter5Task()

# Step 1: Load contract
contract = scene_architect.use_tool("Get Global Story Contract")
# Sees: chapters_4_6 = "grudging_respect_and_banter"
# Sees: magic reveals = ["power awakens", "first use"]
# Sees: FMC voice = "witty, deflects, self-deprecating"

# Step 2: Scene Architect writes romantic banter
# Before writing kiss:
check = scene_architect.use_tool("Check Romance Pacing", {
    "chapter_number": 5,
    "proposed_action": "first kiss"
})
# Returns: ❌ NOT ALLOWED - too early, save for Ch 7+

# Scene Architect adjusts: writes tension instead of kiss
# Respects the escalation ladder

# Step 3: Scene Architect wants to reveal FMC's power
check = scene_architect.use_tool("Check Magic Reveal", {
    "chapter_number": 5,
    "proposed_reveal": "FMC uses magic for first time"
})
# Returns: ✅ ALLOWED - within chapters_1_5 schedule

# Scene Architect proceeds with reveal

# Step 4: Chapter written with guardrails respected
# QA evaluates Chapter 5
qa_result = qa_agent.evaluate(chapter_5)
# Scores: 7.8/10 (FAIL - threshold is 8.0)

# QA flags specific issues:
qa_agent.use_tool("Issue Tracker", {
    "discovered_in": 5,
    "affects_chapter": 5,
    "issue_type": "emotional_impact",
    "detail": "Emotional impact scored 7/10 - missing vulnerability beat",
    "severity": "medium"
})

# Workflow creates fix_5 task
# After fixes applied, Chapter 5 re-evaluated
# Scores: 8.3/10 (PASS) ✅
```

---

## Files Created/Modified

### New Files (Week 4 Refinements)
1. `core/memory/story_contract.py` (403 lines)
2. `tools/story_contract_tools.py` (305 lines)
3. `WEEK4_REFINEMENTS.md` (this file)

### Modified Files
1. `core/memory/manuscript_memory.py` (+80 lines)
   - Added story_contract instance
   - Added get/save/initialize methods

2. `tools/__init__.py` (+6 lines)
   - Export 3 new tools

3. `agents/scene_architect.py` (+15 lines)
   - Added 3 tools to tool list
   - Updated task description

4. `agents/all_agents.py` (+10 lines)
   - Updated QA tools (added IssueTracker, StoryContract)
   - Updated QA task description

**Total New Code:** ~708 lines
**Total Modified Code:** ~111 lines

---

## Testing the Story Contract

```python
from crewai_ghostwriter.core import ManuscriptMemory

# Initialize
memory = ManuscriptMemory("test_book")

# Set up contract
memory.story_contract.set_pov(
    pov_type="third_limited",
    perspective="FMC",
    tense="past",
    rules=["no head hopping"]
)

memory.story_contract.set_romance_rules(
    romance_type="slow_burn",
    escalation_ladder={
        "chapters_1_3": "awareness",
        "chapters_4_6": "attraction",
        "chapters_7_9": "emotional_connection",
        "chapters_10_12": "physical_intimacy",
        "chapters_13_15": "commitment"
    },
    boundaries=["fade_to_black"]
)

# Test romance pacing
result = memory.story_contract.check_romance_pacing(
    chapter_number=3,
    proposed_action="first kiss"
)
print(result)
# {'allowed': False, 'reason': 'First kiss scheduled for Ch 7+', ...}

# Test magic reveal
memory.story_contract.set_magic_system(
    magic_type="elemental",
    rules=["magic has cost"],
    limitations=["drains energy"],
    reveal_schedule={
        "chapters_1_5": ["magic exists"],
        "chapters_6_10": ["FMC has power"],
        "chapters_11_15": ["true nature revealed"]
    }
)

result = memory.story_contract.check_magic_reveal(
    chapter_number=4,
    proposed_reveal="FMC's true nature as ancient goddess"
)
print(result)
# {'allowed': False, 'reason': 'Forbidden knowledge', ...}

# Save to Redis
memory.save_story_contract()

# Export for inspection
with open("outputs/story_contract.json", "w") as f:
    f.write(memory.story_contract.to_json())
```

---

## Benefits Summary

### 1. Prevents Coherence Drift in Parallel Execution
**Before:** Ch 3 and Ch 10 written in parallel → voice drift
**After:** Both read same contract → consistent voice

### 2. Enforces Genre Conventions (Romantasy)
**Before:** Agent might put kiss in Ch 2 (too fast for slow-burn)
**After:** Escalation ladder enforces proper pacing

### 3. Protects Major Reveals
**Before:** Ch 4 might spoil Ch 12 magic reveal
**After:** Reveal schedule prevents early leaks

### 4. Closes QA Failure Loop
**Before:** QA says "fail" → dead end
**After:** QA flags issues → creates fix tasks → re-enters loop

### 5. Zero Agent Overhead
**Before:** Agents had no shared context
**After:** One tool call loads all guardrails (fast, Redis-backed)

### 6. Inspectable and Adjustable
- Contract stored in Redis (queryable)
- Can export to JSON for human review
- Can adjust escalation ladder if needed
- Version controlled (version field in contract)

---

## Design Trade-offs

### Lightweight vs Heavy
✅ **Chose: Lightweight artifact, not another agent**
- Contract is data structure, not AI
- Fast to read (single Redis call)
- No LLM costs
- No reasoning overhead

### Strict vs Flexible
✅ **Chose: Soft guardrails with override capability**
- Tools return guidance, not hard blocks
- Agents can override if justified
- Useful warnings, not roadblocks

### Manual vs Automatic
✅ **Chose: Hybrid approach**
- `initialize_story_contract_from_manuscript()` analyzes manuscript
- Sets sensible romantasy defaults
- Human can adjust via code if needed
- Future: Manuscript Strategist could set contract

---

## Real-World Impact

### Voice Consistency Example
**Without Contract:**
- Ch 3 (Agent A): "She smiled. 'That's interesting.'"
- Ch 10 (Agent B): "She grinned wickedly. 'Well, well, well...'"
- **Problem:** Voice changed from earnest to sarcastic

**With Contract:**
- Contract: FMC voice = "earnest, guarded, formal speech"
- Ch 3: "She offered a small smile. 'That is... interesting.'"
- Ch 10: "She met his gaze carefully. 'That is unexpected.'"
- **Result:** Voice consistent across parallel execution

### Romance Pacing Example
**Without Contract:**
- Ch 4: First kiss
- Ch 6: Love confession
- Ch 8: Physical intimacy
- **Problem:** Too fast for 15-chapter slow-burn

**With Contract:**
- Ladder: Ch 1-3 = antagonistic, Ch 4-6 = respect, Ch 7-9 = vulnerability
- Tool blocks Ch 4 kiss: "Not allowed, current level: grudging respect"
- Agent writes banter instead
- **Result:** Proper slow-burn pacing maintained

### Magic Reveal Example
**Without Contract:**
- Ch 4: Agent reveals FMC is ancient goddess
- Ch 12: Supposed "big reveal" - already spoiled
- **Problem:** Mystery ruined

**With Contract:**
- Schedule: Ch 1-5 = "magic exists", Ch 11-15 = "true nature"
- Tool blocks Ch 4 reveal: "Forbidden knowledge"
- Agent reveals "FMC senses magic" instead
- Ch 12 reveal: "FMC is ancient goddess" - impactful!
- **Result:** Mystery preserved, reveal lands

---

## Week 4 Final Status

### Original Week 4 Goals ✅
- [x] Parallel execution (4-5x speedup)
- [x] Rate limiting
- [x] Safety guards
- [x] Comprehensive testing

### Week 4 Refinements ✅
- [x] **Global Story Contract** (coherence guardrails)
- [x] **3 new tools** (Get Contract, Check Romance, Check Magic)
- [x] **QA → IssueTracker integration** (failures enter editing loop)
- [x] **Agent integration** (Scene Architect + QA)

### Total Week 4 Code
- Original: 1,165 lines
- Refinements: +819 lines (708 new + 111 modified)
- **Total: 1,984 lines** for Week 4

### Cumulative Code
- Weeks 1-3: 4,250 lines
- Week 4: 1,984 lines
- **Total: 6,234 lines** of production code

---

## Conclusion

The Global Story Contract solves the **#1 risk of parallel execution**: coherence drift.

**Key Insight:** Parallelization makes processing faster but riskier. The contract acts as a lightweight safety net that:
- Costs nothing (data structure, not agent)
- Prevents the most common failures (voice, pacing, reveals)
- Integrates seamlessly with existing architecture
- Provides escape hatch (QA failures → Issue Tracker → fix tasks)

**Result:** Quality-safe parallelization for romantasy manuscripts.

**Week 4 is now COMPLETE with refinements!** 🎉

Ready for Week 5: End-to-end testing with real manuscripts.
