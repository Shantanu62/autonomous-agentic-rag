
import os
from dataclasses import dataclass
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

# Load local environment variables.
load_dotenv(BASE_DIR / ".env")


def get_setting(key: str, default: str = "") -> str:
    """Read configuration from Streamlit Secrets or environment variables."""
    try:
        secret_value = st.secrets.get(key)
        if secret_value is not None:
            return str(secret_value)
    except Exception:
        pass

    return os.getenv(key, default)


@dataclass(frozen=True)
class Settings:
    app_name: str = get_setting(
        "APP_NAME",
        "Autonomous Agentic RAG with Live Data and Memory",
    )
    app_env: str = get_setting("APP_ENV", "development")

    groq_api_key: str = get_setting("GROQ_API_KEY")
    groq_model: str = get_setting("GROQ_MODEL")

    tavily_api_key: str = get_setting("TAVILY_API_KEY")

    qdrant_url: str = get_setting("QDRANT_URL")
    qdrant_api_key: str = get_setting("QDRANT_API_KEY")

    document_collection: str = get_setting(
        "QDRANT_DOCUMENT_COLLECTION",
        "operations_documents",
    )
    memory_collection: str = get_setting(
        "QDRANT_MEMORY_COLLECTION",
        "user_long_term_memory",
    )

    embedding_model: str = get_setting(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )

    retrieval_limit: int = int(get_setting("RETRIEVAL_LIMIT", "5"))
    final_source_limit: int = int(get_setting("FINAL_SOURCE_LIMIT", "3"))
    max_agent_steps: int = int(get_setting("MAX_AGENT_STEPS", "4"))

    database_path: str = get_setting(
        "DATABASE_PATH",
        "data/demo_ops.db",
    )
    checkpoint_database_path: str = get_setting(
        "CHECKPOINT_DATABASE_PATH",
        "data/agent_checkpoints.sqlite",
    )


settings = Settings()
