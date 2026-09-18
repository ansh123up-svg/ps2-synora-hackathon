"""XtreamHealthAI — Wearable Stream Processor — real-time anomaly detection.
Z-score + threshold rules (Kafka/Flink-ready for production)."""
from typing import Dict, Any, List
import math, time
from collections import deque

_windows: Dict[str, deque] = {}
WINDOW_SIZE = 20

THRESHOLDS = {
    "heart_rate":  {"low": 60,  "high": 100, "unit": "bpm", "critical_low": 40,  "critical_high": 130},
    "spo2":        {"low": 95,  "high": 100, "unit": "%",  "critical_low": 90,  "critical_high": 101},
    "temperature": {"low": 36.0,"high": 37.5,"unit": "\u00b0C","critical_low": 35.0,"critical_high": 39.5},
    "hrv":         {"low": 20,  "high": 200, "unit": "ms", "critical_low": 10,  "critical_high": 300},
    "sleep_hours": {"low": 5,   "high": 10,  "unit": "h",  "critical_low": 3,   "critical_high": 14},
}

def _get_window(metric: str) -> deque:
    if metric not in _windows:
        _windows[metric] = deque(maxlen=WINDOW_SIZE)
    return _windows[metric]

def _z_score(value: float, window: deque) -> float:
    if len(window) < 3: return 0.0
    vals = list(window)
    mean = sum(vals) / len(vals)
    std = math.sqrt(sum((v - mean)**2 for v in vals) / len(vals))
    return 0.0 if std == 0 else abs((value - mean) / std)

def detect_anomalies(data: Dict[str, Any]) -> List[Dict]:
    findings = []
    for metric, bounds in THRESHOLDS.items():
        val = data.get(metric)
        if val is None: continue
        try: val = float(val)
        except: continue
        window = _get_window(metric)
        z = _z_score(val, window)
        window.append(val)
        severity, message = "normal", None
        if val <= bounds["critical_low"]:
            severity = "critical"
            message = f"\ud83d\udea8 CRITICAL: {metric.replace('_',' ').title()} dangerously LOW ({val}{bounds['unit']})"
        elif val >= bounds["critical_high"] and metric != "spo2":
            severity = "critical"
            message = f"\ud83d\udea8 CRITICAL: {metric.replace('_',' ').title()} dangerously HIGH ({val}{bounds['unit']})"
        elif val < bounds["low"]:
            severity = "warning"
            message = f"\u26a0\ufe0f {metric.replace('_',' ').title()} LOW: {val}{bounds['unit']} (normal \u2265{bounds['low']})"
        elif val > bounds["high"] and metric != "spo2":
            severity = "warning"
            message = f"\u26a0\ufe0f {metric.replace('_',' ').title()} HIGH: {val}{bounds['unit']} (normal \u2264{bounds['high']})"
        elif z > 2.5:
            severity = "anomaly"
            message = f"\ud83d\udd04 Anomaly: {metric.replace('_',' ').title()} = {val}{bounds['unit']} (z={z:.1f})"
        if message:
            findings.append({"metric": metric, "value": val, "unit": bounds["unit"],
                             "severity": severity, "message": message, "z_score": round(z, 2),
                             "timestamp": time.time()})
    return findings

def anomaly_summary(findings: List[Dict]) -> str:
    if not findings: return "All metrics within normal ranges."
    critical = [f for f in findings if f["severity"] == "critical"]
    if critical:
        return "\ud83d\udea8 CRITICAL: " + "; ".join(f["message"] for f in critical)
    return "Anomalies: " + " | ".join(f["message"] for f in findings)
