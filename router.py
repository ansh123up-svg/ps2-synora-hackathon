from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import state, triage, anomaly, vision, rag, llm as llm_module
import config, time

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    mode: Optional[str] = "wellness"
    session_id: Optional[str] = "default"
    health_conditions: Optional[List[str]] = []

class WearableData(BaseModel):
    heart_rate: Optional[float] = None
    spo2: Optional[float] = None
    temperature: Optional[float] = None
    steps: Optional[float] = None
    hrv: Optional[float] = None
    sleep_hours: Optional[float] = None

@router.post("/chat")
def chat(req: ChatRequest):
    t0 = time.time()
    sid = req.session_id or "default"
    if req.health_conditions:
        state.set_conditions(sid, req.health_conditions)
    conditions = state.get_conditions(sid)

    # 1. Hard escalation check
    if triage.check_escalation(req.message):
        return {"response": triage.escalation_response(), "mode": req.mode,
                "should_escalate": True, "escalation": True, "intent": "emergency",
                "confidence": 1.0, "citations": [], "tokens_used": 42,
                "provider": "safety-rail", "latency_ms": round((time.time()-t0)*1000)}

    # 2. Deterministic intent classification
    detected_mode, confidence = triage.classify_intent(req.message, req.mode or "wellness")
    mode = detected_mode
    state.set_mode(sid, mode)

    # 3. RAG retrieval
    docs = rag.retrieve(req.message, top_k=config.RAG_TOP_K, min_score=config.RAG_MIN_SCORE)
    context = rag.format_context(docs)
    citations = rag.format_citations(docs)

    # 4. LLM generation
    history = state.get_history(sid)
    llm_result = llm_module.generate(req.message, mode, history, context)
    response_text = llm_result["text"]

    # 5. Apply health condition constraints
    response_text = triage.apply_condition_constraints(response_text, conditions)

    # 6. Persist
    state.append_message(sid, "user", req.message)
    state.append_message(sid, "assistant", response_text)

    return {
        "response": response_text, "mode": mode, "detected_mode": detected_mode,
        "confidence": confidence, "intent": "triage" if mode == "triage" else "wellness",
        "should_escalate": False, "escalation": False, "citations": citations,
        "rag_docs_found": len(docs), "tokens_used": llm_result["tokens"],
        "provider": llm_result["provider"], "model": llm_result.get("model", ""),
        "session_id": sid, "history_length": len(state.get_history(sid)),
        "latency_ms": round((time.time()-t0)*1000),
    }

@router.post("/meal-photo")
async def meal_photo(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image (JPEG/PNG)")
    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(413, "Image too large (max 10MB)")
    return vision.analyze_meal_image(image_bytes, file.filename or "")

@router.post("/wearable-stream")
def wearable_stream(data: WearableData):
    t0 = time.time()
    payload = {k: v for k, v in data.dict().items() if v is not None}
    findings = anomaly.detect_anomalies(payload)
    summary = anomaly.anomaly_summary(findings)
    tips = []
    if data.heart_rate and data.heart_rate > 100: tips.append("Elevated HR: rest and hydrate.")
    if data.spo2 and data.spo2 < 95: tips.append("Low SpO2: try deep breathing exercises.")
    if data.temperature and data.temperature > 37.5: tips.append("Elevated temp: stay hydrated, monitor.")
    if data.sleep_hours and data.sleep_hours < 6: tips.append("Short sleep: prioritise 7-9h recovery.")
    if data.hrv and data.hrv < 25: tips.append("Low HRV: consider a rest day, stress management.")
    return {"received": payload, "anomalies": findings, "anomaly_detected": len(findings) > 0,
            "summary": summary, "wellness_tips": tips,
            "critical": any(f["severity"] == "critical" for f in findings),
            "latency_ms": round((time.time()-t0)*1000)}

@router.get("/rag/search")
def rag_search(q: str, k: int = 3):
    docs = rag.retrieve(q, top_k=k)
    return {"query": q, "results": docs, "count": len(docs)}

@router.post("/classify")
def classify(body: dict):
    msg = body.get("message", "")
    mode = body.get("current_mode", "wellness")
    detected, conf = triage.classify_intent(msg, mode)
    return {"detected_mode": detected, "confidence": conf, "escalation": triage.check_escalation(msg)}

@router.post("/session/{session_id}/reset")
def reset_session(session_id: str):
    state.reset_session(session_id)
    return {"reset": True, "session_id": session_id}

@router.get("/session/{session_id}")
def get_session(session_id: str):
    s = state.get_session(session_id)
    return {"session_id": session_id, "msg_count": s["msg_count"],
            "mode": s["last_mode"], "conditions": s["health_conditions"]}
