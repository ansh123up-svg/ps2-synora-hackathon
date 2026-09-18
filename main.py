from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import router

app = FastAPI(
    title="XtreamHealthAI",
    description="""
XtreamHealthAI by TeamXtream — Comprehensive Health Intelligence Platform.

Features:
- RAG-powered responses (clinical knowledge base — 12 BioMed documents)
- LLM integration (OpenAI / Ollama / rule-based stub)
- Deterministic intent routing (wellness ⇔ triage)
- Mandatory escalation triggers & clinical safety rails (30+ keywords)
- Multimodal meal photo analysis (Vision LLM / GPT-4V)
- Real-time wearable anomaly detection (z-score + threshold)
- Health condition constraints overriding general recommendations
- Multi-turn session memory

NOT a medical device. NOT a substitute for professional medical advice.
    """,
    version="3.0.0",
    contact={"name": "TeamXtream"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health", tags=["System"])
def health():
    import config
    return {
        "status": "ok",
        "service": "XtreamHealthAI",
        "team": "TeamXtream",
        "version": "3.0.0",
        "llm_provider": config.LLM_PROVIDER,
        "vision_provider": config.VISION_PROVIDER,
        "rag_kb_size": 12,
    }
