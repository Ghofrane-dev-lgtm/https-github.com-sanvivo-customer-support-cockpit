"""Triage and trust signals for the cockpit.

Computed on the server because the trace endpoint is slow (up to 2.5 s per ticket):
ranking the queue needs every trace, so we read the stored trace here instead.
"""

import os
import re
from datetime import datetime

# Words that mean "the patient is running out of medicine".
URGENT = re.compile(r"dringend|vorräte|aufgebraucht|therapie", re.IGNORECASE)
# Words that mean "the customer asks for medical advice".
MEDICAL = re.compile(r"dosis|dosier|wie viel|welche sorte|empfehl|noch nehmen", re.IGNORECASE)


def _now() -> datetime:
    # The demo data is from March 2026, so COCKPIT_NOW (in .env) can pin "today".
    fixed = os.getenv("COCKPIT_NOW")
    return datetime.fromisoformat(fixed) if fixed else datetime.now()


def _flag(label: str, severity: str, step: int | None = None) -> dict:
    # severity "danger" = the agent did something wrong, "warn" = Lena should look closer.
    # step = which trace step the warning belongs to, so the UI can highlight it.
    return {"code": f"{label}-{step}", "label": label, "severity": severity, "step": step}


def analyze(messages, trace, status, priority, assignee, escalated) -> dict:
    customer_text = " ".join(m["text"] for m in messages if m["role"] == "customer")
    flags = []

    # ---- Part 1: TRUST — can Lena trust the agent's answer? (bet W2) ----
    if trace:
        tool_failed = False
        for i, step in enumerate(trace["steps"]):
            if step["type"] == "tool_call" and step["status"] == "error":
                tool_failed = True
                flags.append(_flag(f"Tool-Fehler: {step['tool']}", "warn", i))
            if step["type"] == "retrieval":
                best = max((hit["score"] for hit in step["hits"]), default=0)
                if best < 0.6:
                    flags.append(_flag("Keine oder nur schwache Quelle", "warn", i))
            if step["type"] == "answer" and tool_failed:
                flags.append(_flag("Antwort trotz Tool-Fehler – vermutlich erfunden", "danger", i))
        if trace["confidence"] < 0.5:
            flags.append(_flag("Agent war sich unsicher", "warn"))
        if MEDICAL.search(customer_text) and not escalated:
            flags.append(_flag("Medizinische Frage vom Agenten beantwortet", "danger"))

    if not trace:
        trust = {"level": "none", "label": "Ohne Agent"}
    elif any(f["severity"] == "danger" for f in flags):
        trust = {"level": "wrong", "label": "Nicht vertrauen"}
    elif flags:
        trust = {"level": "check", "label": "Prüfen"}
    else:
        trust = {"level": "ok", "label": "Plausibel"}

    # ---- Part 2: TRIAGE — how urgent is this ticket? (bet W1) ----
    score = 0
    reasons = []

    for f in flags:
        if f["severity"] == "danger":
            score += 40
            reasons.append(f["label"])

    if status != "closed":
        if any(f["severity"] == "warn" for f in flags):
            score += 10
            reasons.append("Agent-Antwort prüfen")
        if priority == "high":
            score += 20
            reasons.append("Hohe Priorität")
        if URGENT.search(customer_text):
            score += 25
            reasons.append("Therapie/Versorgung dringend")
        if sum(1 for m in messages if m["role"] == "customer") >= 4:
            score += 25
            reasons.append("Kunde fragt wiederholt nach")
        if messages and messages[-1]["role"] == "customer":
            hours = int((_now() - datetime.fromisoformat(messages[-1]["created_at"])).total_seconds() // 3600)
            score += min(max(hours, 0), 30)
            reasons.append(f"Unbeantwortet seit {hours} h")
        if escalated and not assignee:
            score += 15
            reasons.append("Eskaliert, aber niemand zuständig")
        if status == "waiting_customer":
            score -= 20

    return {
        "flags": flags,
        "trust": trust,
        "confidence": trace["confidence"] if trace else None,
        "triage": {"score": max(score, 0), "reasons": reasons},
    }