
import tempfile
from pathlib import Path
from uuid import uuid4

import streamlit as st

from config import settings


st.set_page_config(
    page_title="Enterprise Operations AI Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


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


def render_sources(sources: list[dict]) -> None:
    """Display document citations returned by the agent."""
    if not sources:
        return

    with st.expander(f"📚 Sources ({len(sources)})"):
        for index, source in enumerate(sources, start=1):
            filename = source.get("source", "Unknown source")
            page = source.get("page")
            chunk = source.get("chunk")
            citation = source.get("citation", "")

            st.markdown(f"**{index}. {filename}**")

            if page is not None:
                st.caption(f"Page: {page}")

            if chunk is not None:
                st.caption(f"Chunk: {chunk}")

            if citation:
                st.caption(citation)

            st.divider()


def render_run_details(run_details: dict) -> None:
    """Display agent execution information."""
    if not run_details:
        return

    with st.expander("⚙️ Agent execution details"):
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

    try:
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
            f"from **{original_name}**."
        )

    except Exception:
        st.error(
            "Document processing failed. Check the file format "
            "and Qdrant connection."
        )


def render_chat_tab() -> None:
    st.subheader("Enterprise Operations AI Copilot")

    st.markdown(
        "Ask questions about internal SOPs, support tickets, "
        "SLA performance or current information from the web."
    )

    sample_questions = [
        "How many annual leave days are available to employees?",
        "Look up ticket TCK-1001.",
        "Show November 2026 SLA metrics for Platform Support.",
        "Calculate 15% of 2400.",
    ]

    st.markdown("**Try a sample question**")

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
            with st.spinner("Analyzing your request..."):
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
                            "run_details": result.get(
                                "run_details",
                                {},
                            ),
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


def render_knowledge_tab() -> None:
    st.subheader("Operations Knowledge Base")

    st.markdown(
        "Upload internal SOPs and policies to make them searchable "
        "through the RAG assistant."
    )

    st.info(
        "Supported formats: PDF, DOCX and TXT. "
        "Maximum upload size should be kept within the configured "
        "application limit."
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
        ):
            process_upload(uploaded_file)


def render_memory_tab() -> None:
    st.subheader("Long-Term Memory")

    st.caption(
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
                    st.error(result.get("error", "Memory could not be saved."))

            except Exception:
                st.error("Memory storage is currently unavailable.")

    st.divider()
    st.markdown("**Saved memories**")

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
                st.markdown(f"**{memory.get('category', 'context')}**")
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
                            result.get("error", "Memory deletion failed.")
                        )

    except Exception:
        st.error("Could not retrieve long-term memories.")


def main() -> None:
    initialize_session()

    with st.sidebar:
        st.title("🤖 Operations Copilot")
        st.caption("Autonomous Agentic RAG")

        st.divider()

        st.markdown("**System configuration**")

        st.write(
            "Groq LLM: "
            + ("🟢 Configured" if settings.groq_api_key else "🔴 Missing")
        )

        st.write(
            "Qdrant: "
            + (
                "🟢 Configured"
                if settings.qdrant_url and settings.qdrant_api_key
                else "🔴 Missing"
            )
        )

        st.write(
            "Tavily: "
            + ("🟢 Configured" if settings.tavily_api_key else "🟡 Optional")
        )

        st.divider()

        if st.button("＋ New conversation", use_container_width=True):
            st.session_state.thread_id = str(uuid4())
            st.session_state.messages = []
            st.session_state.latest_run = None
            st.rerun()

        st.caption("Powered by LangGraph · Groq · Qdrant")

    st.title("Enterprise Operations AI Copilot")

    st.markdown(
        "A bounded AI assistant for internal knowledge, "
        "live research and operational workflows."
    )

    chat_tab, knowledge_tab, memory_tab = st.tabs([
        "💬 AI Copilot",
        "📚 Knowledge Base",
        "🧠 Long-Term Memory",
    ])

    with chat_tab:
        render_chat_tab()

    with knowledge_tab:
        render_knowledge_tab()

    with memory_tab:
        render_memory_tab()


if __name__ == "__main__":
    main()
