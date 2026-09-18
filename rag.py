"""XtreamHealthAI Clinical RAG — BioMedical knowledge retrieval.
In production: replace vector_search() with PubMed API / BioMistral embeddings / ChromaDB."""
from typing import List, Dict, Tuple
import re

CLINICAL_KB: List[Dict] = [
    {"id":"kb001","title":"Tension Headache Management","source":"UpToDate 2024",
     "content":"Tension-type headaches are the most common primary headache. First-line: paracetamol 1g or ibuprofen 400mg. Avoid opioids. Red flags: thunderclap onset, fever+neck stiffness, focal neuro signs → urgent referral.",
     "tags":["headache","pain","tension","analgesic"]},
    {"id":"kb002","title":"Fever Assessment & Triage","source":"BMJ Best Practice 2024",
     "content":"Fever (>38.3°C) triage: adults with fever + rash + confusion → ER immediately. Simple fever with URI: paracetamol/ibuprofen, fluids, rest. Fever >5 days or >40°C warrants clinical evaluation.",
     "tags":["fever","temperature","triage","infection"]},
    {"id":"kb003","title":"Hypertension Lifestyle Interventions","source":"AHA/ACC 2023",
     "content":"Lifestyle: DASH diet, sodium <2.3g/day, 150min/week aerobic exercise, weight loss (1mmHg per kg), limit alcohol. These can reduce SBP 4-11mmHg. Do not replace pharmacotherapy in stage 2 HTN.",
     "tags":["hypertension","blood pressure","diet","exercise","lifestyle"]},
    {"id":"kb004","title":"Sleep Hygiene Evidence-Based Guidelines","source":"AASM 2023",
     "content":"CBT-I is first-line for chronic insomnia (superior to pharmacotherapy). Sleep hygiene: consistent schedule, dark/cool room (16-19°C), no screens 60min before bed, avoid caffeine after noon, limit alcohol. Recommended duration: 7-9h adults.",
     "tags":["sleep","insomnia","cbti","fatigue","rest"]},
    {"id":"kb005","title":"Nutritional Protein Requirements","source":"WHO/FAO 2023",
     "content":"Protein RDA: 0.8g/kg/day sedentary adults. Active individuals: 1.2-2.0g/kg. For muscle gain: 1.6-2.2g/kg. Sources: lean meat, fish, eggs, legumes, dairy. Complete proteins contain all essential amino acids.",
     "tags":["protein","nutrition","diet","muscle","amino acids"]},
    {"id":"kb006","title":"Chest Pain Emergency Triage","source":"ESC Guidelines 2023",
     "content":"STEMI/ACS red flags: crushing/pressure chest pain, radiation to arm/jaw, diaphoresis, dyspnoea. Action: immediate 999/112 call, aspirin 300mg (if not allergic), do NOT drive self. Any unexplained chest pain warrants ECG within 10 minutes.",
     "tags":["chest pain","acs","stemi","cardiac","emergency","heart"]},
    {"id":"kb007","title":"Heart Rate & HRV Interpretation","source":"AHA 2024",
     "content":"Normal resting HR: 60-100 bpm. Athletes: 40-60 bpm normal. Resting HR >100 (tachycardia): dehydration, anaemia, infection, anxiety, hyperthyroidism. HRV >50ms generally good autonomic function. Low HRV associated with stress, poor recovery, cardiovascular risk.",
     "tags":["heart rate","hrv","tachycardia","wearable","vitals"]},
    {"id":"kb008","title":"SpO2 / Oxygen Saturation Norms","source":"NHS Clinical Guidelines 2024",
     "content":"Normal SpO2: 95-100%. 94%: borderline, investigate cause. <94%: supplemental oxygen may be needed, seek medical evaluation. <90%: medical emergency. COPD patients may have lower baseline; use clinical context.",
     "tags":["spo2","oxygen","saturation","respiratory","pulse oximeter"]},
    {"id":"kb009","title":"Dietary Macronutrient Ratios","source":"Dietary Guidelines 2020-2025",
     "content":"Recommended macros: carbohydrates 45-65% of calories, protein 10-35%, fats 20-35%. Mediterranean diet: high vegetables, whole grains, legumes, fish, olive oil. Low-glycaemic diets improve metabolic markers.",
     "tags":["macros","carbohydrates","fat","nutrition","diet","calories"]},
    {"id":"kb010","title":"Stress & Anxiety Management","source":"NICE Guidelines 2023",
     "content":"First-line for mild-moderate anxiety: CBT, exercise (150min/week reduces anxiety 30%), mindfulness-based stress reduction. 4-7-8 breathing technique shown to activate parasympathetic response. Persistent anxiety >2 weeks: GP evaluation recommended.",
     "tags":["stress","anxiety","mental health","breathing","mindfulness"]},
    {"id":"kb011","title":"Dehydration Recognition & Management","source":"WHO Hydration Guidelines",
     "content":"Signs of dehydration: dark urine, dry mouth, dizziness, headache, reduced urine output. Mild-moderate: oral rehydration. Severe: IV fluids, urgent care. Daily water: 2.7L women, 3.7L men.",
     "tags":["dehydration","hydration","water","electrolytes"]},
    {"id":"kb012","title":"Exercise Prescriptions for Chronic Disease","source":"ACSM 2023",
     "content":"Diabetes type 2: 150min/week aerobic + 2x resistance. Hypertension: 150min/week moderate aerobic. Heart failure: supervised cardiac rehab. Obesity: 250-300min/week for weight loss. Always: medical clearance before high-intensity program.",
     "tags":["exercise","chronic disease","diabetes","hypertension","fitness"]},
]

def _keyword_score(query: str, doc: Dict) -> float:
    q_words = set(re.findall(r'\w+', query.lower()))
    d_words = set(re.findall(r'\w+', (doc['content']+' '+' '.join(doc['tags'])).lower()))
    stop = {'the','a','an','is','are','was','were','and','or','of','to','in','for','with','that','this','it','on'}
    q_words -= stop; d_words -= stop
    if not q_words: return 0.0
    overlap = q_words & d_words
    tag_matches = sum(1 for t in doc['tags'] if t in query.lower())
    return (len(overlap) / len(q_words)) * 0.7 + min(tag_matches * 0.15, 0.3)

def retrieve(query: str, top_k: int = 3, min_score: float = 0.2) -> List[Dict]:
    scored = [(doc, _keyword_score(query, doc)) for doc in CLINICAL_KB]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [{**doc, 'score': round(score, 3)} for doc, score in scored if score >= min_score][:top_k]

def format_context(docs: List[Dict]) -> str:
    if not docs: return ""
    return "\n\n".join(f"[REF-{i+1}] {d['title']} ({d['source']}):\n{d['content']}" for i, d in enumerate(docs))

def format_citations(docs: List[Dict]) -> List[Dict]:
    return [{"id": f"REF-{i+1}", "title": d['title'], "source": d['source'], "score": d.get('score',0)} for i, d in enumerate(docs)]
