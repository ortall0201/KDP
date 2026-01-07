"""
FastAPI Backend for CrewAI Ghostwriter Mobile App

This server exposes REST API endpoints and WebSocket for real-time updates.
"""

from fastapi import FastAPI, File, UploadFile, WebSocket, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import json
from datetime import datetime
from pathlib import Path
import uuid

from crewai_ghostwriter.main import GhostwriterOrchestrator
from crewai import Crew, Task, Process
from crewai_ghostwriter.agents import (
    get_architect_expansion_task,
    get_line_edit_task
)


# Initialize FastAPI app
app = FastAPI(
    title="CrewAI Ghostwriter API",
    description="Multi-agent ghostwriting system for fiction manuscripts",
    version="1.0.0"
)

# Enable CORS for React Native app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your mobile app's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# DATA MODELS
# ============================================================================

class JobStatus(BaseModel):
    """Status of a processing job."""
    job_id: str
    status: str  # "queued", "processing", "completed", "failed"
    progress: int  # 0-100
    current_phase: Optional[str] = None
    phase_status: Dict[str, str] = {}
    chapter_progress: Dict[int, str] = {}
    logs: List[Dict] = []
    errors: List[Dict] = []
    completed_at: Optional[str] = None
    word_count: Optional[int] = None


class SystemHealth(BaseModel):
    """System health check."""
    status: str
    redis_connected: bool
    chromadb_connected: bool
    openai_api_configured: bool
    anthropic_api_configured: bool


# ============================================================================
# IN-MEMORY JOB STORAGE
# ============================================================================

# In production, use Redis or database
jobs: Dict[str, JobStatus] = {}

# WebSocket connections for real-time updates
active_connections: Dict[str, List[WebSocket]] = {}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_job(job_id: str) -> JobStatus:
    """Create a new processing job."""
    job = JobStatus(
        job_id=job_id,
        status="queued",
        progress=0,
        phase_status={
            "Analysis": "pending",
            "Continuity": "pending",
            "Expansion": "pending",
            "Editing": "pending",
            "QA": "pending",
            "Learning": "pending"
        },
        chapter_progress={},
        logs=[],
        errors=[]
    )
    jobs[job_id] = job
    return job


def update_job(
    job_id: str,
    status: Optional[str] = None,
    progress: Optional[int] = None,
    current_phase: Optional[str] = None,
    phase_status: Optional[Dict] = None,
    log_message: Optional[str] = None,
    log_level: str = "info",
    error_message: Optional[str] = None,
    error_phase: Optional[str] = None,
    chapter_progress: Optional[Dict] = None,
    word_count: Optional[int] = None
):
    """Update job status and notify connected clients."""
    if job_id not in jobs:
        return

    job = jobs[job_id]

    if status:
        job.status = status
    if progress is not None:
        job.progress = progress
    if current_phase:
        job.current_phase = current_phase
    if phase_status:
        job.phase_status.update(phase_status)
    if log_message:
        timestamp = datetime.now().strftime("%H:%M:%S")
        job.logs.append({
            "timestamp": timestamp,
            "message": log_message,
            "level": log_level
        })
        # Keep last 100 logs
        if len(job.logs) > 100:
            job.logs = job.logs[-100:]
    if error_message and error_phase:
        job.errors.append({
            "phase": error_phase,
            "message": error_message
        })
    if chapter_progress:
        job.chapter_progress.update(chapter_progress)
    if word_count:
        job.word_count = word_count

    if status == "completed":
        job.completed_at = datetime.now().isoformat()

    # Broadcast update to connected WebSocket clients
    asyncio.create_task(broadcast_job_update(job_id, job))


async def broadcast_job_update(job_id: str, job: JobStatus):
    """Send job update to all connected WebSocket clients."""
    if job_id in active_connections:
        message = json.dumps(job.dict())

        # Send to all connections for this job
        disconnected = []
        for websocket in active_connections[job_id]:
            try:
                await websocket.send_text(message)
            except:
                disconnected.append(websocket)

        # Remove disconnected clients
        for ws in disconnected:
            active_connections[job_id].remove(ws)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "app": "CrewAI Ghostwriter API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=SystemHealth)
def health_check():
    """Check system health."""
    import os

    # Check Redis
    redis_connected = False
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, socket_timeout=1)
        r.ping()
        redis_connected = True
    except:
        pass

    # Check ChromaDB
    chromadb_connected = False
    try:
        import chromadb
        client = chromadb.HttpClient(host="localhost", port=8000)
        client.heartbeat()
        chromadb_connected = True
    except:
        pass

    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    all_healthy = (
        redis_connected and
        chromadb_connected and
        openai_key.startswith("sk-") and
        anthropic_key.startswith("sk-ant-")
    )

    return SystemHealth(
        status="healthy" if all_healthy else "degraded",
        redis_connected=redis_connected,
        chromadb_connected=chromadb_connected,
        openai_api_configured=openai_key.startswith("sk-"),
        anthropic_api_configured=anthropic_key.startswith("sk-ant-")
    )


@app.post("/upload")
async def upload_manuscript(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    x_openai_key: str = Header(..., alias="X-OpenAI-Key"),
    x_anthropic_key: str = Header(..., alias="X-Anthropic-Key")
):
    """
    Upload a manuscript file and start processing.

    Returns job_id for tracking progress.

    Requires user's API keys in headers:
    - X-OpenAI-Key: User's OpenAI API key
    - X-Anthropic-Key: User's Anthropic API key
    """
    # Validate file type
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    # Validate API keys
    if not x_openai_key.startswith("sk-"):
        raise HTTPException(status_code=400, detail="Invalid OpenAI API key format")
    if not x_anthropic_key.startswith("sk-ant-"):
        raise HTTPException(status_code=400, detail="Invalid Anthropic API key format")

    # Generate job ID
    job_id = str(uuid.uuid4())
    book_id = f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Save uploaded file
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / f"{job_id}_{file.filename}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Create job
    create_job(job_id)

    # Start processing in background with USER'S API keys
    background_tasks.add_task(
        process_manuscript_async,
        job_id=job_id,
        book_id=book_id,
        file_path=str(file_path),
        openai_key=x_openai_key,
        anthropic_key=x_anthropic_key
    )

    return {
        "job_id": job_id,
        "book_id": book_id,
        "message": "Processing started"
    }


@app.get("/status/{job_id}", response_model=JobStatus)
def get_job_status(job_id: str):
    """Get current status of a processing job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]


@app.get("/download/{job_id}")
def download_manuscript(job_id: str):
    """Download completed manuscript."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")

    # Get manuscript file
    output_dir = Path("outputs")
    manuscript_path = output_dir / f"{job_id}_manuscript.txt"

    if not manuscript_path.exists():
        raise HTTPException(status_code=404, detail="Manuscript file not found")

    return FileResponse(
        path=str(manuscript_path),
        filename=f"ghostwritten_{job_id}.txt",
        media_type="text/plain"
    )


@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time job updates."""
    await websocket.accept()

    # Add to active connections
    if job_id not in active_connections:
        active_connections[job_id] = []
    active_connections[job_id].append(websocket)

    try:
        # Send current status immediately
        if job_id in jobs:
            await websocket.send_text(json.dumps(jobs[job_id].dict()))

        # Keep connection alive
        while True:
            # Wait for client messages (ping/pong)
            await websocket.receive_text()

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Remove from active connections
        if job_id in active_connections:
            active_connections[job_id].remove(websocket)


# ============================================================================
# BACKGROUND PROCESSING
# ============================================================================

async def process_manuscript_async(job_id: str, book_id: str, file_path: str, openai_key: str, anthropic_key: str):
    """
    Process manuscript in background with progress updates.

    This wraps the orchestrator and updates job status at each step.

    Args:
        job_id: Unique job identifier
        book_id: Unique book identifier
        file_path: Path to uploaded manuscript
        openai_key: User's OpenAI API key
        anthropic_key: User's Anthropic API key
    """
    try:
        update_job(
            job_id,
            status="processing",
            log_message="Initializing ghostwriter system with your API keys...",
            progress=5
        )

        # Create orchestrator with USER'S API keys
        orchestrator = GhostwriterOrchestrator(
            book_id=book_id,
            openai_key=openai_key,
            anthropic_key=anthropic_key,
            verbose=False
        )

        # Load manuscript
        update_job(
            job_id,
            log_message=f"Loading manuscript...",
            progress=10
        )

        orchestrator.load_manuscript(file_path)
        stats = orchestrator.manuscript_memory.get_memory_stats()
        num_chapters = stats['chapters_stored']

        update_job(
            job_id,
            log_message=f"Loaded {num_chapters} chapters",
            log_level="success",
            progress=15,
            chapter_progress={i: "pending" for i in range(1, num_chapters + 1)}
        )

        # Initialize story contract
        update_job(job_id, log_message="Initializing Story Contract...")
        orchestrator.manuscript_memory.initialize_story_contract_from_manuscript()
        update_job(
            job_id,
            log_message="Story Contract created",
            log_level="success",
            progress=20
        )

        # Initialize agents
        update_job(job_id, log_message="Initializing 6 agents...")
        orchestrator.initialize_agents()
        update_job(
            job_id,
            log_message="Agents ready",
            log_level="success",
            progress=25
        )

        # Phase 1: Analysis
        update_job(
            job_id,
            current_phase="Analysis",
            phase_status={"Analysis": "running"},
            log_message="Running manuscript analysis...",
            progress=30
        )

        orchestrator._run_analysis()

        update_job(
            job_id,
            phase_status={"Analysis": "completed"},
            log_message="Analysis complete",
            log_level="success",
            progress=35
        )

        # Phase 2: Continuity
        update_job(
            job_id,
            current_phase="Continuity",
            phase_status={"Continuity": "running"},
            log_message="Building continuity database...",
            progress=40
        )

        orchestrator._run_continuity_build()

        update_job(
            job_id,
            phase_status={"Continuity": "completed"},
            log_message="Continuity database built",
            log_level="success",
            progress=45
        )

        # Phase 3: Expansion
        update_job(
            job_id,
            current_phase="Expansion",
            phase_status={"Expansion": "running"},
            log_message=f"Expanding {num_chapters} chapters...",
            progress=50
        )

        chapters = orchestrator.manuscript_memory.get_all_chapters()
        chapters_completed = 0

        for ch_num in sorted(chapters.keys()):
            update_job(
                job_id,
                chapter_progress={ch_num: "running"},
                log_message=f"Expanding Chapter {ch_num}..."
            )

            try:
                task = Task(
                    description=get_architect_expansion_task(ch_num),
                    agent=orchestrator.agents['architect'],
                    expected_output=f"Expanded Chapter {ch_num}"
                )

                crew = Crew(
                    agents=[orchestrator.agents['architect']],
                    tasks=[task],
                    process=Process.sequential,
                    verbose=False
                )

                crew.kickoff()

                chapters_completed += 1
                progress = 50 + int((chapters_completed / num_chapters) * 15)

                update_job(
                    job_id,
                    chapter_progress={ch_num: "completed"},
                    log_message=f"Chapter {ch_num} expanded",
                    log_level="success",
                    progress=progress
                )

            except Exception as e:
                update_job(
                    job_id,
                    chapter_progress={ch_num: "error"},
                    log_message=f"Error expanding Chapter {ch_num}",
                    log_level="error",
                    error_phase="Expansion",
                    error_message=str(e)
                )

        update_job(
            job_id,
            phase_status={"Expansion": "completed"},
            log_message="All chapters expanded",
            log_level="success",
            progress=65
        )

        # Phase 4: Editing
        update_job(
            job_id,
            current_phase="Editing",
            phase_status={"Editing": "running"},
            log_message="Polishing prose...",
            progress=70
        )

        chapters_completed = 0
        for ch_num in sorted(chapters.keys()):
            update_job(
                job_id,
                chapter_progress={ch_num: "running"},
                log_message=f"Editing Chapter {ch_num}..."
            )

            try:
                task = Task(
                    description=get_line_edit_task(ch_num),
                    agent=orchestrator.agents['editor'],
                    expected_output=f"Polished Chapter {ch_num}"
                )

                crew = Crew(
                    agents=[orchestrator.agents['editor']],
                    tasks=[task],
                    process=Process.sequential,
                    verbose=False
                )

                crew.kickoff()

                chapters_completed += 1
                progress = 70 + int((chapters_completed / num_chapters) * 10)

                update_job(
                    job_id,
                    chapter_progress={ch_num: "completed"},
                    log_message=f"Chapter {ch_num} polished",
                    log_level="success",
                    progress=progress
                )

            except Exception as e:
                update_job(
                    job_id,
                    chapter_progress={ch_num: "error"},
                    log_message=f"Error editing Chapter {ch_num}",
                    log_level="error",
                    error_phase="Editing",
                    error_message=str(e)
                )

        update_job(
            job_id,
            phase_status={"Editing": "completed"},
            log_message="All chapters polished",
            log_level="success",
            progress=80
        )

        # Phase 5: QA
        update_job(
            job_id,
            current_phase="QA",
            phase_status={"QA": "running"},
            log_message="Running quality assurance...",
            progress=85
        )

        orchestrator._run_qa()

        update_job(
            job_id,
            phase_status={"QA": "completed"},
            log_message="QA evaluation complete",
            log_level="success",
            progress=90
        )

        # Phase 6: Learning
        update_job(
            job_id,
            current_phase="Learning",
            phase_status={"Learning": "running"},
            log_message="Storing patterns in long-term memory...",
            progress=93
        )

        orchestrator._run_learning()

        update_job(
            job_id,
            phase_status={"Learning": "completed"},
            log_message="Learning complete",
            log_level="success",
            progress=95
        )

        # Compile final manuscript
        update_job(job_id, log_message="Compiling final manuscript...", progress=97)

        final_manuscript = compile_final_manuscript(orchestrator, num_chapters)
        word_count = len(final_manuscript.split())

        # Save to file
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{job_id}_manuscript.txt"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_manuscript)

        update_job(
            job_id,
            status="completed",
            progress=100,
            log_message=f"Processing complete! {word_count:,} words",
            log_level="success",
            word_count=word_count
        )

    except Exception as e:
        update_job(
            job_id,
            status="failed",
            log_message=f"Fatal error: {str(e)}",
            log_level="error",
            error_phase="System",
            error_message=str(e)
        )


def compile_final_manuscript(orchestrator: GhostwriterOrchestrator, num_chapters: int) -> str:
    """Compile all chapters into final manuscript."""
    manuscript_parts = []

    # Title page
    manuscript_parts.append("=" * 60)
    manuscript_parts.append("GHOSTWRITTEN MANUSCRIPT")
    manuscript_parts.append(f"Book ID: {orchestrator.book_id}")
    manuscript_parts.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    manuscript_parts.append("=" * 60)
    manuscript_parts.append("\n\n")

    # Chapters
    chapters = orchestrator.manuscript_memory.get_all_chapters()
    for ch_num in sorted(chapters.keys()):
        chapter_data = chapters[ch_num]
        manuscript_parts.append(f"Chapter {ch_num}")
        manuscript_parts.append("-" * 60)
        manuscript_parts.append("")
        manuscript_parts.append(chapter_data['text'])
        manuscript_parts.append("\n\n")

    # Stats
    total_words = sum(len(ch['text'].split()) for ch in chapters.values())
    manuscript_parts.append("\n")
    manuscript_parts.append("=" * 60)
    manuscript_parts.append(f"Total Chapters: {num_chapters}")
    manuscript_parts.append(f"Total Word Count: {total_words:,}")
    manuscript_parts.append("=" * 60)

    return "\n".join(manuscript_parts)


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("Starting CrewAI Ghostwriter API Server...")
    print("API Docs: http://localhost:8080/docs")
    print("Health Check: http://localhost:8080/health")

    uvicorn.run(app, host="0.0.0.0", port=8080)
