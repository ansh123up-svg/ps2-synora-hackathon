# XtreamHealthAI v3 — by TeamXtream

> **Comprehensive Health Intelligence Platform** combining Chronic Health Monitoring,
> Symptom Triage, and Personal Wellness Coaching (Fitness + Nutrition) in one unified AI system.

---

## 🚀 Quick Start

```bash
cd xtreamhealthai
pip install -r requirements.txt
cp .env.example .env          # set LLM_PROVIDER=stub to run offline
uvicorn main:app --reload
```
Then open `frontend.html` in your browser — no extra server needed.

---

## 📦 File Map

| File | Purpose |
|---|---|
| `main.py` | FastAPI app entry point — XtreamHealthAI |
| `router.py` | All REST endpoints |
| `rag.py` | Clinical RAG — 12-doc BioMed knowledge base |
| `llm.py` | LLM layer — OpenAI / Ollama / stub |
| `triage.py` | Intent routing + clinical safety + escalation |
| `anomaly.py` | Wearable anomaly detection (z-score + threshold) |
| `vision.py` | Meal photo analysis (Vision LLM / GPT-4V) |
| `state.py` | Multi-turn session memory |
| `config.py` | Environment configuration |
| `frontend.html` | 3-panel premium UI |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | System status + provider info |
| `/chat` | POST | RAG + LLM + intent routing + safety |
| `/meal-photo` | POST | Meal image → macros + quality |
| `/wearable-stream` | POST | Vitals → anomaly detection |
| `/rag/search?q=...` | GET | Direct clinical KB search |
| `/classify` | POST | Intent classification only |
| `/session/{id}/reset` | POST | Reset conversation |
| `/docs` | GET | Auto-generated Swagger UI |

---

## 🧠 LLM Providers

| Provider | `.env` setting | Notes |
|---|---|---|
| **Stub** (default) | `LLM_PROVIDER=stub` | Works offline, no key needed |
| **OpenAI GPT-4o** | `LLM_PROVIDER=openai` | Set `OPENAI_API_KEY` |
| **Ollama (local)** | `LLM_PROVIDER=ollama` | Run `ollama pull mistral` first |

---

## 🛡️ Safety Features

- **30+ emergency keywords** → hard escalation → 🚨 call 112/911 alert
- **Non-diagnostic outputs** enforced in every system prompt
- **Health condition constraints** override general advice (diabetes, hypertension, asthma, heart disease, kidney disease)
- **Mandatory urgency classification** on all triage responses

---

*XtreamHealthAI by TeamXtream — Not a medical device. Not a substitute for professional medical advice.*
