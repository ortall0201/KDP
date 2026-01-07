"""
Streamlit Web App for CrewAI Ghostwriter

A visual interface for manuscript processing with real-time progress tracking.
Can be packaged as desktop app for app stores later.
"""

import streamlit as st
import asyncio
from pathlib import Path
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Ghostwriter",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .phase-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        background-color: #f0f2f6;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-running {
        color: #007bff;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .status-pending {
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'current_phase' not in st.session_state:
        st.session_state.current_phase = None
    if 'phase_status' not in st.session_state:
        st.session_state.phase_status = {
            "Analysis": "pending",
            "Continuity": "pending",
            "Expansion": "pending",
            "Editing": "pending",
            "QA": "pending",
            "Learning": "pending"
        }
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'progress' not in st.session_state:
        st.session_state.progress = 0
    if 'chapter_progress' not in st.session_state:
        st.session_state.chapter_progress = {}
    if 'errors' not in st.session_state:
        st.session_state.errors = []
    if 'completed_manuscript' not in st.session_state:
        st.session_state.completed_manuscript = None
    if 'book_id' not in st.session_state:
        st.session_state.book_id = None
    if 'uploaded_file_path' not in st.session_state:
        st.session_state.uploaded_file_path = None

def add_log(message: str, level: str = "info"):
    """Add a log message."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append({
        "timestamp": timestamp,
        "message": message,
        "level": level
    })
    # Keep only last 100 logs
    if len(st.session_state.logs) > 100:
        st.session_state.logs = st.session_state.logs[-100:]

def update_phase_status(phase: str, status: str):
    """Update phase status."""
    st.session_state.phase_status[phase] = status
    st.session_state.current_phase = phase

def render_sidebar():
    """Render the sidebar with settings."""
    with st.sidebar:
        st.markdown("## ⚙️ Settings")

        # API Keys status
        st.markdown("### API Keys")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

        if openai_key and openai_key.startswith("sk-"):
            st.success("✅ OpenAI API Key configured")
        else:
            st.error("❌ OpenAI API Key missing")
            st.info("Add OPENAI_API_KEY to .env file")

        if anthropic_key and anthropic_key.startswith("sk-ant-"):
            st.success("✅ Anthropic API Key configured")
        else:
            st.error("❌ Anthropic API Key missing")
            st.info("Add ANTHROPIC_API_KEY to .env file")

        st.markdown("---")

        # Infrastructure status
        st.markdown("### Infrastructure")

        # Check Redis
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, socket_timeout=1)
            r.ping()
            st.success("✅ Redis connected")
        except:
            st.error("❌ Redis not running")
            st.info("Start: `docker-compose up -d redis`")

        # Check ChromaDB
        try:
            import chromadb
            client = chromadb.HttpClient(host="localhost", port=8000)
            client.heartbeat()
            st.success("✅ ChromaDB connected")
        except:
            st.error("❌ ChromaDB not running")
            st.info("Start: `docker-compose up -d chromadb`")

        st.markdown("---")

        # Processing options
        st.markdown("### Processing Options")
        parallel = st.checkbox("Enable Parallel Processing", value=True,
                              help="4-5x faster, uses Story Contract for coherence")
        max_concurrent = st.slider("Max Concurrent Tasks", 1, 10, 5)

        st.markdown("---")

        # About
        st.markdown("### About")
        st.info("""
        **CrewAI Ghostwriter**

        Multi-agent system for fiction ghostwriting with:
        - Non-linear editing
        - Long-term learning
        - Quality gating (≥8.0/10)

        Version: 1.0.0
        """)

def render_progress_section():
    """Render the progress tracking section."""
    st.markdown("## 📊 Progress")

    # Overall progress bar
    progress_col1, progress_col2 = st.columns([4, 1])
    with progress_col1:
        st.progress(st.session_state.progress / 100)
    with progress_col2:
        st.metric("Overall", f"{st.session_state.progress}%")

    # Phase status
    st.markdown("### Phases")

    phase_cols = st.columns(3)
    phases = list(st.session_state.phase_status.items())

    for i, (phase, status) in enumerate(phases):
        col_idx = i % 3
        with phase_cols[col_idx]:
            # Status icon
            if status == "completed":
                icon = "✅"
                css_class = "status-success"
            elif status == "running":
                icon = "▶️"
                css_class = "status-running"
            elif status == "error":
                icon = "❌"
                css_class = "status-error"
            else:
                icon = "⏸️"
                css_class = "status-pending"

            st.markdown(f'<div class="phase-box">'
                       f'{icon} <span class="{css_class}">{phase}</span>'
                       f'</div>', unsafe_allow_html=True)

    # Chapter progress (if in expansion/editing phase)
    if st.session_state.chapter_progress:
        st.markdown("### Chapter Progress")

        completed_chapters = sum(1 for status in st.session_state.chapter_progress.values()
                                if status == "completed")
        total_chapters = len(st.session_state.chapter_progress)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Completed", f"{completed_chapters}/{total_chapters}")
        with col2:
            st.metric("In Progress",
                     sum(1 for s in st.session_state.chapter_progress.values() if s == "running"))
        with col3:
            st.metric("Pending",
                     sum(1 for s in st.session_state.chapter_progress.values() if s == "pending"))

def render_logs_section():
    """Render the logs section."""
    st.markdown("## 📝 Activity Log")

    # Log container with scrolling
    log_container = st.container()

    with log_container:
        if st.session_state.logs:
            # Reverse to show newest first
            for log in reversed(st.session_state.logs[-20:]):  # Show last 20
                timestamp = log["timestamp"]
                message = log["message"]
                level = log["level"]

                if level == "error":
                    st.error(f"**[{timestamp}]** {message}")
                elif level == "warning":
                    st.warning(f"**[{timestamp}]** {message}")
                elif level == "success":
                    st.success(f"**[{timestamp}]** {message}")
                else:
                    st.info(f"**[{timestamp}]** {message}")
        else:
            st.info("No activity yet. Upload a manuscript to begin.")

def render_errors_section():
    """Render errors if any."""
    if st.session_state.errors:
        st.markdown("## ⚠️ Errors")
        for error in st.session_state.errors:
            st.error(f"**{error['phase']}:** {error['message']}")

def main():
    """Main app."""
    initialize_session_state()

    # Header
    st.markdown('<div class="main-header">📚 AI Ghostwriter</div>', unsafe_allow_html=True)
    st.markdown("### Transform your manuscript with AI-powered multi-agent editing")

    # Sidebar
    render_sidebar()

    # Main content
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("## 📤 Upload Manuscript")

        uploaded_file = st.file_uploader(
            "Choose a .txt manuscript file",
            type=['txt'],
            help="Upload your manuscript in plain text format",
            disabled=st.session_state.processing
        )

        if uploaded_file and not st.session_state.processing:
            # Save uploaded file
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)

            file_path = upload_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.session_state.uploaded_file_path = str(file_path)

            # Show file info
            file_size = file_path.stat().st_size / 1024  # KB
            word_count = len(uploaded_file.getvalue().decode().split())

            st.success(f"✅ File uploaded: {uploaded_file.name}")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("File Size", f"{file_size:.1f} KB")
            with col_b:
                st.metric("Word Count", f"{word_count:,}")

            # Start processing button
            if st.button("🚀 Start Processing", type="primary", use_container_width=True):
                st.session_state.processing = True
                st.session_state.book_id = f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                add_log("Starting manuscript processing...", "info")
                st.rerun()

        elif st.session_state.processing:
            st.info("⏳ Processing in progress...")

            if st.button("⏹️ Stop Processing", type="secondary", use_container_width=True):
                st.session_state.processing = False
                add_log("Processing stopped by user", "warning")
                st.rerun()

    with col2:
        st.markdown("## 📥 Download")

        if st.session_state.completed_manuscript:
            st.success("✅ Manuscript processing complete!")

            # Download button
            st.download_button(
                label="⬇️ Download Completed Manuscript",
                data=st.session_state.completed_manuscript,
                file_name=f"ghostwritten_{st.session_state.book_id}.txt",
                mime="text/plain",
                type="primary",
                use_container_width=True
            )

            # Show stats
            word_count = len(st.session_state.completed_manuscript.split())
            st.metric("Final Word Count", f"{word_count:,}")
        else:
            st.info("Completed manuscript will appear here")

    # Progress section
    if st.session_state.processing or st.session_state.completed_manuscript:
        render_progress_section()

    # Logs section
    render_logs_section()

    # Errors section
    render_errors_section()

    # If processing, run the orchestrator
    if st.session_state.processing and st.session_state.uploaded_file_path:
        try:
            # Import here to avoid circular imports
            from app_orchestrator import run_ghostwriter_app

            # Run async orchestrator
            asyncio.run(run_ghostwriter_app(
                manuscript_path=st.session_state.uploaded_file_path,
                book_id=st.session_state.book_id
            ))

        except Exception as e:
            st.session_state.errors.append({
                "phase": "System",
                "message": str(e)
            })
            add_log(f"Error: {str(e)}", "error")
            st.session_state.processing = False

if __name__ == "__main__":
    main()
