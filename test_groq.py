
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from .env")

llm = ChatGroq(
    model=model_name,
    api_key=api_key,
    temperature=0,
    max_tokens=200,
    timeout=30,
    max_retries=2,
)

print("Testing Groq API...")
print("Model:", model_name)

response = llm.invoke(
    "Reply with exactly: Groq API connection successful!"
)

print("Groq connection successful!")
print("Response:", response.content)
