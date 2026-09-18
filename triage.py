"""XtreamHealthAI — Intent routing + clinical safety + escalation."""
import re
from typing import Dict, Tuple, List
import config

TRIAGE_SIGNALS = [
    "symptom","pain","hurt","ache","fever","sick","ill","diagnose","diagnosis",
    "medicine","medication","drug","dose","prescription","treatment","cure",
    "doctor","hospital","clinic","emergency","urgent","bleed","rash","swell",
    "vomit","nausea","diarrhea","dizziness","faint","infection","virus","bacteria",
    "cough","cold","flu","covid","allergy","allergic","breathe","breathing",
    "heart","chest","blood","pressure","sugar","glucose","diabetes","thyroid",
]

WELLNESS_SIGNALS = [
    "workout","exercise","fitness","gym","run","yoga","meditation","mindfulness",
    "diet","nutrition","eat","food","meal","calorie","protein","carb","fat","vitamin",
    "sleep better","sleep tips","energy","hydration","water","supplement",
    "weight loss","muscle","strength","cardio","stretch","recovery",
    "stress relief","relax","wellbeing","wellness","healthy habit",
]

def classify_intent(message: str, current_mode: str) -> Tuple[str, float]:
    msg = message.lower()
    if check_escalation(msg):
        return "triage", 1.0
    triage_score = sum(1 for kw in TRIAGE_SIGNALS if kw in msg)
    wellness_score = sum(1 for kw in WELLNESS_SIGNALS if kw in msg)
    total = triage_score + wellness_score
    if total == 0:
        return current_mode, 0.5
    if triage_score > wellness_score:
        return "triage", round(min(0.6 + (triage_score - wellness_score) * 0.1, 0.99), 2)
    elif wellness_score > triage_score:
        return "wellness", round(min(0.6 + (wellness_score - triage_score) * 0.1, 0.99), 2)
    return current_mode, 0.55

def check_escalation(text: str) -> bool:
    return any(kw in text.lower() for kw in config.ESCALATION_HARD_KEYWORDS)

def escalation_response() -> str:
    return (
        "🚨 EMERGENCY DETECTED — Please call emergency services (112 / 911) immediately "
        "or go to your nearest emergency room. Do NOT drive yourself. "
        "XtreamHealthAI cannot handle medical emergencies. "
        "\n\nIf you or someone else is in immediate danger, call emergency services NOW."
    )

CONDITION_OVERRIDES: Dict[str, List[str]] = {
    "diabetes": [
        "Avoid high-glycaemic foods (white rice, sugary drinks, refined carbs).",
        "Monitor blood glucose before and after exercise.",
        "Do not fast without medical supervision."
    ],
    "hypertension": [
        "Limit sodium to <1.5g/day (stricter than general 2.3g recommendation).",
        "Avoid high-intensity exercise without clearance.",
        "Monitor BP before and after workouts."
    ],
    "heart disease": [
        "Avoid isometric exercises (heavy lifting, planks held long).",
        "Target HR zone: 50-70% max HR only.",
        "Any chest pain during exercise: STOP immediately."
    ],
    "asthma": [
        "Always carry rescue inhaler during exercise.",
        "Warm up slowly; cold/dry air triggers bronchospasm.",
        "Swimming is often better tolerated than running."
    ],
    "kidney disease": [
        "High protein diets (>1.2g/kg) contraindicated — consult nephrologist.",
        "Monitor potassium and phosphorus intake.",
        "Adjust hydration based on fluid restriction orders."
    ],
}

def apply_condition_constraints(response: str, conditions: List[str]) -> str:
    warnings = []
    for cond in conditions:
        for key, overrides in CONDITION_OVERRIDES.items():
            if key in cond.lower():
                warnings.extend(overrides)
    if warnings:
        return response + "\n\n⚠️ Health Condition Constraints: " + " | ".join(warnings)
    return response

def rule_based_response(message: str, mode: str) -> str:
    msg = message.lower()
    if any(w in msg for w in ["sleep","insomnia","tired","fatigue"]):
        return ("CBT-I is the gold-standard for chronic insomnia. Sleep hygiene: consistent bedtime/wake time, "
                "dark cool room (16-19\u00b0C), no screens 60 min before bed, avoid caffeine after noon. "
                "Adults need 7-9h. Persistent insomnia >3 weeks: GP evaluation recommended. — XtreamHealthAI")
    if any(w in msg for w in ["headache","migraine","head pain"]):
        return (("Triage: Mild tension headaches → paracetamol 1g, rest, hydration. "
                 "Seek urgent care for: thunderclap onset, headache+fever+neck stiffness, "
                 "focal neuro signs, or headache after head injury. NOT a diagnosis. — XtreamHealthAI")
                if mode=="triage" else
                "Tension headaches: paracetamol or ibuprofen, hydration, rest in a dark quiet room. "
                "Frequent migraines (>4/month) warrant a neurology review. — XtreamHealthAI")
    if any(w in msg for w in ["diet","nutrition","eat","food","weight","calorie"]):
        return ("Evidence-based nutrition: prioritise whole foods — vegetables, fruits, legumes, whole grains, lean proteins. "
                "Macros: 45-65% carbs, 10-35% protein, 20-35% fat (Dietary Guidelines 2025). "
                "For weight management: 500 kcal/day deficit → ~0.5kg/week. — XtreamHealthAI")
    if any(w in msg for w in ["exercise","workout","fitness","gym","run","cardio"]):
        return ("WHO recommendation: 150-300 min/week moderate aerobic + 2x muscle-strengthening weekly. "
                "Progressive overload for strength: increase load ~5-10%/week. "
                "Rest days are essential — muscles grow during recovery. — XtreamHealthAI")
    if any(w in msg for w in ["stress","anxiety","anxious","overwhelm"]):
        return ("Evidence-based stress reduction: 150 min/week aerobic exercise reduces anxiety ~30% (NICE 2023). "
                "4-7-8 breathing activates parasympathetic response. CBT is first-line for GAD. "
                "Persistent anxiety >2 weeks: GP referral. — XtreamHealthAI")
    if any(w in msg for w in ["fever","temperature","chills"]):
        return ("Fever triage: <38.5\u00b0C + mild URI → self-care (paracetamol, fluids, rest). "
                "Seek urgent care: fever >40\u00b0C, fever+rash+confusion, or fever >5 days. NOT a diagnosis. — XtreamHealthAI")
    if any(w in msg for w in ["heart","pulse","palpitation"]):
        return ("Normal resting HR: 60-100 bpm. HRV >50ms indicates good autonomic function. "
                "Palpitations with chest pain/dizziness/syncope: seek ECG evaluation. — XtreamHealthAI")
    return ("Thank you for your health question. XtreamHealthAI provides evidence-based wellness guidance "
            "and non-diagnostic triage support. Could you share more details about your concern? "
            "For medical decisions, always consult a qualified healthcare provider.")
