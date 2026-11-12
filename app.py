
import html
import tempfile
from pathlib import Path
from uuid import uuid4

import streamlit as st

from config import settings


st.set_page_config(
    page_title="Operations AI | Shantanu Anand",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# DESIGN SYSTEM
# ---------------------------------------------------------

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --navy: #14213D;
    --navy-light: #1D3155;
    --indigo: #536BDA;
    --indigo-light: #7187EF;
    --background: #F5F7FC;
    --surface: #FFFFFF;
    --text: #19263F;
    --muted: #748198;
    --border: #E4E9F2;
    --green: #16A36A;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: var(--background);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: var(--navy);
    border-right: 1px solid #263A5C;
}

[data-testid="stSidebar"] * {
    color: #EAF0FF;
}

[data-testid="stSidebar"] hr {
    border-color: #344766;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #C3CFE2;
}

[data-testid="stSidebar"] button {
    border: 1px solid #405579;
    border-radius: 10px;
    background: #203657;
    color: white;
}

[data-testid="stSidebar"] button:hover {
    background: #2C4770;
    border-color: #8299EF;
}

.main .block-container {
    max-width: 1450px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

.hero {
    background: linear-gradient(120deg, #14213D 0%, #243F70 65%, #536BDA 100%);
    padding: 35px 38px;
    border-radius: 22px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 12px 35px rgba(29, 49, 85, 0.14);
}

.hero-label {
    display: inline-block;
    color: #DCE5FF;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    padding: 6px 12px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 15px;
}

.hero h1 {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(27px, 3vw, 43px);
    font-weight: 800;
    line-height: 1.2;
    color: white;
    margin: 0 0 12px 0;
}

.hero p {
    font-size: 15px;
    line-height: 1.7;
    color: #D8E2F5;
    max-width: 720px;
    margin: 0;
}

.creator-line {
    margin-top: 22px;
    padding-top: 15px;
    border-top: 1px solid rgba(255,255,255,0.2);
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.2px;
}

.section-heading {
    font-family: 'Manrope', sans-serif;
    color: var(--text);
    font-size: 21px;
    font-weight: 800;
    margin: 8px 0 5px 0;
}

.section-subtitle {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 18px;
}

.feature-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 19px;
    min-height: 132px;
    box-shadow: 0 3px 12px rgba(20,33,61,0.035);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(20,33,61,0.09);
}

.feature-icon {
    font-size: 25px;
    margin-bottom: 11px;
}

.feature-title {
    color: var(--text);
    font-size: 15px;
    font-weight: 800;
    margin-bottom: 5px;
}

.feature-description {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.6;
}

.brand-card {
    background: #1D3155;
    border: 1px solid #405579;
    padding: 17px;
    border-radius: 15px;
    margin-bottom: 15px;
}

.brand-name {
    font-family: 'Manrope', sans-serif;
    font-size: 17px;
    font-weight: 800;
    color: white;
    line-height: 1.3;
}

.brand-caption {
    color: #AEBED8;
    font-size: 11px;
    margin-top: 5px;
}

.creator-badge {
    display: inline-block;
    background: rgba(113,135,239,0.17);
    color: #DCE5FF;
    border: 1px solid rgba(113,135,239,0.45);
    border-radius: 30px;
    padding: 7px 11px;
    font-size: 11px;
    font-weight: 700;
    margin-top: 13px;
}

.status-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 9px 0;
    border-bottom: 1px solid #344766;
    font-size: 12px;
}

.status-pill {
    border-radius: 30px;
    padding: 4px 9px;
    font-size: 10px;
    font-weight: 700;
}

.status-ok {
    color: #9CF0C8;
    background: rgba(22,163,106,0.16);
}

.status-missing {
    color: #FFD0C9;
    background: rgba(220,70,70,0.18);
}

.stButton > button {
    border-radius: 10px;
    border: 1px solid var(--border);
    min-height: 43px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"] {
    background: var(--indigo);
    border-color: var(--indigo);
    color: white;
}

.stButton > button:hover {
    border-color: var(--indigo);
    color: var(--indigo);
}

.stButton > button[kind="primary"]:hover {
    background: #4058C5;
    color: white;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 9px;
    border-bottom: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 9px 9px 0 0;
    padding: 12px 17px;
    font-weight: 700;
}

.stTabs [aria-selected="true"] {
    color: var(--indigo) !important;
}

[data-testid="stChatMessage"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 16px;
    margin-bottom: 12px;
}

[data-testid="stChatInput"] {
    border-radius: 13px;
}

[data-testid="stFileUploader"] {
    background: white;
    border: 1px dashed #AAB8D3;
    border-radius: 14px;
    padding: 12px;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 13px;
    padding: 14px;
}

.creator-footer {
    text-align: center;
    border-top: 1px solid var(--border);
    padding: 20px 8px 5px 8px;
    margin-top: 40px;
    color: #8490A4;
    font-size: 11px;
    line-height: 1.8;
}

.creator-footer strong {
    color: #536BDA;
}

@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem 1rem 2rem 1rem;
    }
    .hero {
        padding: 25px 21px;
        border-radius: 16px;
    }
    .hero h1 {
        font-size: 27px;
    }
}
</style>
"""


# ---------------------------------------------------------
# SESSION MANAGEMENT
# ---------------------------------------------------------

def initialize_session() -> None:
    """Initialize conversation and demo-user session state."""

    if "user_id" not in st.session_state:
        st.session_state.user_id = f"demo-{uuid4()}"

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "latest_run" not in st.session_state:
        st.session_state.latest_run = None


@st.cache_resource
def get_vector_store():
    from rag.vector_store import OperationsVectorStore
    return OperationsVectorStore()


@st.cache_resource
def get_memory_store():
    from memory.store import LongTermMemoryStore
    return LongTermMemoryStore()


# ---------------------------------------------------------
# REUSABLE UI COMPONENTS
# ---------------------------------------------------------

def render_sources(sources: list[dict]) -> None:
    """Display document citations returned by the agent."""

    if not sources:
        return

    with st.expander(f"📚 Sources and evidence ({len(sources)})"):
        for index, source in enumerate(sources, start=1):
            filename = source.get("source", "Unknown source")
            page = source.get("page")
            chunk = source.get("chunk")
            citation = source.get("citation", "")

            st.markdown(f"**{index}. {filename}**")

            details = []
            if page is not None:
                details.append(f"Page: {page}")
            if chunk is not None:
                details.append(f"Chunk: {chunk}")

            if details:
                st.caption(" · ".join(details))

            if citation:
                st.caption(citation)

            st.divider()


def render_run_details(run_details: dict) -> None:
    """Display agent execution information."""

    if not run_details:
        return

    with st.expander("⚙️ Agent execution and observability"):
        col1, col2 = st.columns(2)

        col1.metric(
            "Tool steps",
            run_details.get("tool_steps", 0),
        )

        col2.metric(
            "Latency",
            f'{run_details.get("latency_ms", 0)} ms',
        )

        selected_tools = run_details.get("selected_tools", [])

        st.markdown("**Selected tools**")

        if selected_tools:
            for tool_name in selected_tools:
                st.write(f"• `{tool_name}`")
        else:
            st.caption("No tools were selected.")

        errors = run_details.get("errors", [])

        if errors:
            st.markdown("**Execution warnings**")
            for error in errors:
                st.warning(error)

        st.caption(
            f'Run ID: {run_details.get("run_id", "Unavailable")}'
        )


def render_feature_card(icon: str, title: str, description: str) -> None:
    """Render a consistent homepage feature card."""

    st.markdown(
        f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# DOCUMENT INGESTION
# ---------------------------------------------------------

def process_upload(uploaded_file) -> None:
    """Extract, chunk and index an uploaded operations document."""

    from rag.ingest import (
        extract_document_text,
        split_document_into_chunks,
    )

    original_name = Path(uploaded_file.name).name
    suffix = Path(original_name).suffix.lower()

    if suffix not in {".pdf", ".docx", ".txt"}:
        st.error("Only PDF, DOCX and TXT files are supported.")
        return

    if uploaded_file.size > 10 * 1024 * 1024:
        st.error("Maximum document size is 10 MB.")
        return

    try:
        with st.spinner("Extracting, chunking and indexing document..."):
            with tempfile.TemporaryDirectory() as temp_dir:
                temporary_path = Path(temp_dir) / original_name
                temporary_path.write_bytes(uploaded_file.getvalue())

                pages = extract_document_text(temporary_path)

                if not pages:
                    st.warning("No readable text was found in this document.")
                    return

                chunks = split_document_into_chunks(pages)
                vector_store = get_vector_store()
                indexed_count = vector_store.add_documents(chunks)

        st.success(
            f"Successfully indexed {indexed_count} chunks "
            f"from {original_name}."
        )

    except Exception:
        st.error(
            "Document processing failed. Check the file format "
            "and Qdrant connection."
        )


# ---------------------------------------------------------
# AI COPILOT
# ---------------------------------------------------------

def render_chat_tab() -> None:
    st.markdown(
        '<div class="section-heading">Your AI Operations Assistant</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Ask about internal policies, tickets, SLA performance '
        'or current information from the web.'
        '</div>',
        unsafe_allow_html=True,
    )

    sample_questions = [
        "How many annual leave days are available to employees?",
        "Look up ticket TCK-1001.",
        "Show November 2026 SLA metrics for Platform Support.",
        "Calculate 15% of 2400.",
    ]

    st.markdown("**Explore with a sample question**")

    sample_columns = st.columns(2)

    for index, question in enumerate(sample_questions):
        if sample_columns[index % 2].button(
            question,
            key=f"sample_{index}",
            use_container_width=True,
        ):
            st.session_state.pending_question = question

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                render_sources(message.get("sources", []))
                render_run_details(message.get("run_details", {}))

    pending_question = st.session_state.pop(
        "pending_question",
        None,
    )

    question = st.chat_input(
        "Ask your operations question..."
    )

    if pending_question:
        question = pending_question

    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question,
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Your AI Copilot is analyzing the request..."):
                try:
                    from agent.graph import run_agent

                    result = run_agent(
                        question=question,
                        thread_id=st.session_state.thread_id,
                        user_id=st.session_state.user_id,
                    )

                    if result.get("success"):
                        answer = result.get(
                            "answer",
                            "The agent returned no answer.",
                        )

                        run_details = result.get("run_details", {})
                        sources = run_details.get("sources", [])

                        st.markdown(answer)
                        render_sources(sources)
                        render_run_details(run_details)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                            "run_details": run_details,
                        })

                        st.session_state.latest_run = run_details

                    else:
                        error_message = result.get(
                            "error",
                            "The request could not be completed.",
                        )

                        st.error(error_message)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_message,
                            "sources": [],
                            "run_details": result.get("run_details", {}),
                        })

                except Exception:
                    error_message = (
                        "The AI Copilot encountered an error. "
                        "Check the application configuration and logs."
                    )

                    st.error(error_message)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message,
                        "sources": [],
                        "run_details": {},
                    })


# ---------------------------------------------------------
# KNOWLEDGE BASE
# ---------------------------------------------------------

def render_knowledge_tab() -> None:
    st.markdown(
        '<div class="section-heading">Knowledge Base</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Build your searchable enterprise knowledge workspace '
        'using internal SOPs and operational documents.'
        '</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        render_feature_card(
            "📄",
            "PDF documents",
            "Upload company policies and standard operating procedures.",
        )

    with col2:
        render_feature_card(
            "📝",
            "DOCX files",
            "Extract and index Word documents for semantic search.",
        )

    with col3:
        render_feature_card(
            "📃",
            "TXT files",
            "Process lightweight text-based operational documents.",
        )

    st.markdown("### Add a knowledge document")

    st.info(
        "Supported formats: PDF, DOCX and TXT. "
        "Maximum upload size: 10 MB."
    )

    uploaded_file = st.file_uploader(
        "Choose an operations document",
        type=["pdf", "docx", "txt"],
        key="knowledge_upload",
    )

    if uploaded_file:
        st.write(f"Selected file: **{uploaded_file.name}**")

        if st.button(
            "Process and index document",
            type="primary",
            use_container_width=True,
        ):
            process_upload(uploaded_file)


# ---------------------------------------------------------
# LONG-TERM MEMORY
# ---------------------------------------------------------

def render_memory_tab() -> None:
    st.markdown(
        '<div class="section-heading">Long-Term Memory</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Manage reusable operational preferences and context '
        'for your demo user.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "Memories are scoped to this browser session's demo user. "
        "Do not save passwords, API keys or sensitive personal data."
    )

    with st.form("save_memory_form"):
        memory_text = st.text_area(
            "Memory content",
            placeholder=(
                "Example: Our support team prefers concise "
                "operational summaries."
            ),
        )

        category = st.selectbox(
            "Category",
            ["preference", "context", "workflow"],
        )

        save_clicked = st.form_submit_button(
            "Save memory",
            type="primary",
        )

    if save_clicked:
        if not memory_text.strip():
            st.warning("Enter memory content before saving.")
        else:
            try:
                result = get_memory_store().save_memory(
                    user_id=st.session_state.user_id,
                    memory=memory_text,
                    category=category,
                )

                if result.get("success"):
                    st.success("Memory saved successfully.")
                else:
                    st.error(
                        result.get(
                            "error",
                            "Memory could not be saved.",
                        )
                    )

            except Exception:
                st.error("Memory storage is currently unavailable.")

    st.divider()
    st.markdown("### Saved memories")

    try:
        memories = get_memory_store().list_memories(
            user_id=st.session_state.user_id,
        )

        if not memories:
            st.info("No saved memories in this session.")
            return

        for memory in memories:
            memory_id = memory["memory_id"]

            with st.container(border=True):
                st.markdown(
                    f"**{memory.get('category', 'context')}**"
                )

                st.write(memory.get("memory", ""))

                st.caption(
                    f"Created: {memory.get('created_at', 'Unknown')}"
                )

                if st.button(
                    "Delete memory",
                    key=f"delete_{memory_id}",
                ):
                    result = get_memory_store().delete_memory(
                        user_id=st.session_state.user_id,
                        memory_id=memory_id,
                    )

                    if result.get("success"):
                        st.success("Memory deleted.")
                        st.rerun()
                    else:
                        st.error(
                            result.get(
                                "error",
                                "Memory deletion failed.",
                            )
                        )

    except Exception:
        st.error("Could not retrieve long-term memories.")


# ---------------------------------------------------------
# APPLICATION SHELL
# ---------------------------------------------------------

def render_sidebar() -> None:
    """Render branded navigation and service status."""

    with st.sidebar:
        st.markdown(
            """
            <div class="brand-card">
                <div style="font-size:28px;margin-bottom:9px;">◈ 🤖</div>
                <div class="brand-name">OPERATIONS AI</div>
                <div class="brand-caption">
                    Enterprise Intelligence Workspace
                </div>
                <div class="creator-badge">
                    BUILT BY SHANTANU ANAND
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("**SYSTEM STATUS**")

        services = [
            ("Groq LLM", bool(settings.groq_api_key)),
            (
                "Qdrant",
                bool(settings.qdrant_url and settings.qdrant_api_key),
            ),
            ("Tavily", bool(settings.tavily_api_key)),
        ]

        for service, configured in services:
            status_class = "status-ok" if configured else "status-missing"
            status_label = "CONNECTED" if configured else "MISSING"

            st.markdown(
                f"""
                <div class="status-row">
                    <span>{service}</span>
                    <span class="status-pill {status_class}">
                        {status_label}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        if st.button(
            "＋  New conversation",
            use_container_width=True,
        ):
            st.session_state.thread_id = str(uuid4())
            st.session_state.messages = []
            st.session_state.latest_run = None
            st.rerun()

        st.divider()

        st.markdown(
            """
            <div style="color:#AEBED8;font-size:11px;line-height:1.8;">
                POWERED BY<br>
                LangGraph · Groq · Qdrant<br>
                Tavily · Sentence Transformers
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="
                margin-top:25px;
                padding-top:15px;
                border-top:1px solid #344766;
                color:#DCE5FF;
                font-size:11px;
                line-height:1.8;
            ">
                <strong>Designed & Developed</strong><br>
                by Shantanu Anand
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_homepage_header() -> None:
    """Render the main branded hero section."""

    st.markdown(
        """
        <div class="hero">
            <div class="hero-label">
                ENTERPRISE AI WORKSPACE
            </div>
            <h1>Autonomous Agentic RAG</h1>
            <p>
                Your intelligent operations copilot for enterprise knowledge,
                live research, support workflows and contextual memory.
            </p>
            <div class="creator-line">
                ✦ Designed & Developed by Shantanu Anand
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_homepage_features() -> None:
    st.markdown(
        '<div class="section-heading">Your operations workspace</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'One intelligent workspace. Multiple operational capabilities.'
        '</div>',
        unsafe_allow_html=True,
    )

    columns = st.columns(4)

    features = [
        (
            "📚",
            "Policy Assistant",
            "Search internal SOPs and get grounded answers with citations.",
        ),
        (
            "🎫",
            "Ticket Intelligence",
            "Look up synthetic support tickets and their status.",
        ),
        (
            "📊",
            "SLA Analytics",
            "Explore operational performance using read-only SQL.",
        ),
        (
            "🌐",
            "Live Research",
            "Bring current web information into operational workflows.",
        ),
    ]

    for column, feature in zip(columns, features):
        with column:
            render_feature_card(*feature)


def main() -> None:
    initialize_session()

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    render_sidebar()
    render_homepage_header()
    render_homepage_features()

    st.markdown("---")

    chat_tab, knowledge_tab, memory_tab = st.tabs([
        "💬  AI Copilot",
        "📚  Knowledge Base",
        "🧠  Long-Term Memory",
    ])

    with chat_tab:
        render_chat_tab()

    with knowledge_tab:
        render_knowledge_tab()

    with memory_tab:
        render_memory_tab()

    st.markdown(
        """
        <div class="creator-footer">
            <strong>Autonomous Agentic RAG</strong><br>
            Enterprise Operations AI Copilot<br>
            Designed & Developed by
            <strong>Shantanu Anand</strong><br>
            LangGraph · Groq · Qdrant · Tavily · Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
