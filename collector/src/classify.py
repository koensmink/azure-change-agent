from .config import SECURITY_KEYWORDS

def classify_security(event: dict) -> dict:
    hay = " ".join([
        event.get("title") or "",
        event.get("summary") or "",
        event.get("product") or "",
        event.get("body_text") or "",
        " ".join(event.get("tags") or []),
    ]).lower()

    hits = [k for k in SECURITY_KEYWORDS if k.lower() in hay]

    if hits:
        event["security_relevant"] = True
        event["security_reason"] = f"keyword_hit={','.join(hits[:12])}"
        event["category"] = _guess_category(hay)
        event["impact"] = "Unknown"
        event["recommended_action"] = "Review change; assess impact on policies, identity, endpoints, logging."
    else:
        event["security_relevant"] = False
        event["security_reason"] = None
        event["category"] = "Other"
        event["impact"] = "Unknown"
        event["recommended_action"] = None

    return event

def _guess_category(hay: str) -> str:
    if any(w in hay for w in ["entra", "conditional access", "mfa", "fido", "passkey", "identity", "pim", "rbac"]):
        return "Identity"
    if any(w in hay for w in ["intune", "endpoint", "device", "compliance", "autopilot"]):
        return "Endpoint"
    if any(w in hay for w in ["defender", "xdr", "sentinel", "siem", "soar"]):
        return "Security"
    if any(w in hay for w in ["firewall", "private endpoint", "vnet", "network", "dns", "ddos"]):
        return "Networking"
    if any(w in hay for w in ["policy", "audit", "logging", "compliance", "governance"]):
        return "Compliance"
    return "Other"
PY
