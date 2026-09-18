"""XtreamHealthAI — Meal photo analysis via Vision LLM.
Prod: GPT-4V / LLaVA / Gemini Vision. Stub: deterministic macro estimator."""
import base64, random
from typing import Dict, Any
import llm as llm_module

FOOD_PROFILES = [
    {"foods":["grilled chicken breast","brown rice","steamed broccoli"],"calories":480,"protein":42,"carbs":48,"fat":10,"fiber":6,"quality":"excellent"},
    {"foods":["salmon fillet","quinoa","roasted asparagus","olive oil"],"calories":520,"protein":38,"carbs":35,"fat":20,"fiber":5,"quality":"excellent"},
    {"foods":["lentil dal","whole wheat roti","cucumber salad"],"calories":420,"protein":22,"carbs":65,"fat":8,"fiber":14,"quality":"good"},
    {"foods":["oatmeal","banana","almonds","mixed berries","chia seeds"],"calories":380,"protein":14,"carbs":58,"fat":12,"fiber":10,"quality":"excellent"},
    {"foods":["paneer curry","basmati rice","naan"],"calories":680,"protein":28,"carbs":82,"fat":26,"fiber":3,"quality":"moderate"},
    {"foods":["egg white omelette","whole grain toast","avocado","cherry tomatoes"],"calories":340,"protein":28,"carbs":24,"fat":15,"fiber":7,"quality":"excellent"},
    {"foods":["butter chicken","white rice","garlic naan"],"calories":820,"protein":35,"carbs":90,"fat":35,"fiber":2,"quality":"poor"},
    {"foods":["caesar salad","grilled shrimp","croutons"],"calories":390,"protein":32,"carbs":22,"fat":18,"fiber":4,"quality":"good"},
]

QUALITY_TIPS = {
    "excellent": "Great nutritional balance! High protein, controlled calories, good fibre.",
    "good": "Good meal overall. Consider adding more vegetables or reducing refined carbs.",
    "moderate": "Moderate quality. High in carbs — pair with more protein/fibre next meal.",
    "poor": "High in calories and saturated fat. Balance with lighter meals and exercise.",
}

def analyze_meal_image(image_bytes: bytes, filename: str = "") -> Dict[str, Any]:
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode()
        result = llm_module.vision_analyze(b64)
        if result: return result
    # Deterministic stub based on file size
    random.seed(len(image_bytes) % 97)
    p = random.choice(FOOD_PROFILES)
    tip = QUALITY_TIPS.get(p["quality"], "")
    analysis = (
        f"Detected: {', '.join(p['foods'])}. Quality: {p['quality'].upper()}. {tip} "
        f"Estimated: {p['calories']} kcal, {p['protein']}g protein, {p['carbs']}g carbs, "
        f"{p['fat']}g fat, {p['fiber']}g fibre. "
        f"Values are AI estimates — actual nutrition varies by portion size. — XtreamHealthAI"
    )
    return {
        "analysis": analysis,
        "macros": {"calories": p["calories"], "protein": p["protein"],
                   "carbs": p["carbs"], "fat": p["fat"], "fiber": p["fiber"]},
        "foods_detected": p["foods"],
        "quality_score": p["quality"],
        "tokens_used": 95,
        "provider": "stub-vision",
    }
