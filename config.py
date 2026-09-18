import os
from dotenv import load_dotenv

load_dotenv()

# LLM Provider: "openai" | "ollama" | "stub"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "stub")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

# Vision Provider: "openai" | "stub"
VISION_PROVIDER = os.getenv("VISION_PROVIDER", "stub")

# RAG
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
RAG_MIN_SCORE = float(os.getenv("RAG_MIN_SCORE", "0.3"))

# Safety
ESCALATION_HARD_KEYWORDS = [
    "chest pain", "can't breathe", "cannot breathe", "shortness of breath",
    "stroke", "heart attack", "unconscious", "unresponsive", "seizure",
    "severe bleeding", "suicidal", "suicide", "overdose", "poisoning",
    "anaphylaxis", "anaphylactic", "thunderclap headache", "face drooping",
    "sudden numbness", "sudden weakness", "crushing pain", "can not breathe"
]
