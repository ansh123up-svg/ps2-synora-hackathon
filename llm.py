"""XtreamHealthAI — LLM integration layer.
Supports: openai (GPT-4o/GPT-4o-mini), ollama (Mistral/BioMistral local), stub (rule-based fallback).
Set LLM_PROVIDER in .env to switch."""
from typing import List, Dict
import config

SYSTEM_WELLNESS = """You are XtreamHealthAI, an evidence-based wellness coach and health advisor built by TeamXtream.
You provide practical, science-backed advice on nutrition, fitness, sleep, stress management, and wellbeing.
Always cite the provided clinical references when relevant.
IMPORTANT: You are NOT a doctor. Always recommend consulting a licensed healthcare provider for medical concerns.
Keep responses concise (3-5 sentences) unless detail is requested. Never diagnose."""

SYSTEM_TRIAGE = """You are XtreamHealthAI in clinical triage mode — a non-diagnostic symptom assessment assistant built by TeamXtream.
You help users determine urgency level (self-care / routine GP / urgent care / emergency) based on symptoms.
You DO NOT diagnose, prescribe, or replace clinical judgement.
Use the provided clinical references to support your assessment.
Always end with the appropriate urgency recommendation and a disclaimer.
If you detect emergency keywords, your response MUST start with a 🚨 EMERGENCY alert."""

def _build_messages(system: str, history: List[Dict], user_msg: str, context: str) -> List[Dict]:
    msgs = [{"role": "system", "content": system}]
    if context:
        msgs.append({"role": "system", "content": f"CLINICAL REFERENCES:\n{context}"})
    for h in history[-8:]:
        msgs.append(h)
    msgs.append({"role": "user", "content": user_msg})
    return msgs

def _call_openai(messages: List[Dict]) -> Dict:
    try:
        import openai
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=config.OPENAI_MODEL, messages=messages, max_tokens=512, temperature=0.4)
        return {"text": resp.choices[0].message.content, "tokens": resp.usage.total_tokens,
                "provider": "openai", "model": config.OPENAI_MODEL}
    except Exception as e:
        return {"text": f"[OpenAI error: {e}]", "tokens": 0, "provider": "openai_error", "model": ""}

def _call_ollama(messages: List[Dict]) -> Dict:
    try:
        import httpx
        resp = httpx.post(f"{config.OLLAMA_BASE_URL}/api/chat",
            json={"model": config.OLLAMA_MODEL, "messages": messages, "stream": False}, timeout=30.0)
        data = resp.json()
        content = data.get("message", {}).get("content", "")
        return {"text": content, "tokens": data.get("eval_count", len(content)//4),
                "provider": "ollama", "model": config.OLLAMA_MODEL}
    except Exception as e:
        return {"text": f"[Ollama error: {e}]", "tokens": 0, "provider": "ollama_error", "model": ""}

def _stub_response(user_msg: str, mode: str, context: str) -> Dict:
    import triage as tr
    base = tr.rule_based_response(user_msg, mode)
    if context:
        first_ref = context.split("\n\n")[0] if "\n\n" in context else context
        snippet = first_ref.split(":")[-1].strip()[:180] if ":" in first_ref else ""
        if snippet and snippet not in base:
            base += f" (Clinical reference: {snippet}...)"
    return {"text": base, "tokens": max(20, len(base)//4), "provider": "stub", "model": "rule-based"}

def generate(user_msg: str, mode: str, history: List[Dict], context: str = "") -> Dict:
    system = SYSTEM_TRIAGE if mode == "triage" else SYSTEM_WELLNESS
    msgs = _build_messages(system, history, user_msg, context)
    if config.LLM_PROVIDER == "openai" and config.OPENAI_API_KEY:
        return _call_openai(msgs)
    elif config.LLM_PROVIDER == "ollama":
        return _call_ollama(msgs)
    return _stub_response(user_msg, mode, context)

def vision_analyze(image_b64: str) -> Dict:
    """Vision LLM for meal photo analysis."""
    if config.VISION_PROVIDER == "openai" and config.OPENAI_API_KEY:
        try:
            import openai, json
            client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role":"user","content":[
                    {"type":"text","text":"Analyse this meal. Identify foods, estimate: calories, protein(g), carbs(g), fat(g), fiber(g). Respond in JSON: {foods:[],calories:int,protein:int,carbs:int,fat:int,fiber:float,analysis:string,quality:string}"},
                    {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{image_b64}"}}
                ]}], max_tokens=400)
            raw = resp.choices[0].message.content
            try: data = json.loads(raw.strip('`').replace('json\n',''))
            except: data = {"analysis":raw,"calories":350,"protein":25,"carbs":40,"fat":12,"fiber":4,"quality":"good","foods":[]}
            data["tokens"] = resp.usage.total_tokens
            data["provider"] = "gpt-4o-vision"
            return data
        except: pass
    return None
