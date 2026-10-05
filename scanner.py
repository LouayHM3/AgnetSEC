from __future__ import annotations

from collections.abc import Iterator

SEVERITIES = ("critical", "high", "medium", "low")
PENALTIES = {"critical": 45, "high": 22, "medium": 8, "low": 3}


def calculate_score(findings: list[dict]) -> int:
    score = 100 - sum(PENALTIES.get(item["severity"], 0) for item in findings if not item.get("false_positive"))
    return max(0, min(100, score))


def risk_level(score: int) -> str:
    if score <= 40:
        return "CRITICAL"
    if score <= 65:
        return "HIGH"
    if score <= 85:
        return "MEDIUM"
    return "LOW"


class DemoScanner:
    def run(self, target: str, ports: str) -> Iterator[dict]:
        findings = [
            {"title": "SSH service exposed to the network", "severity": "high", "tool": "nmap", "evidence": f"{target}:22/tcp open", "remediation": "Restrict SSH to an administration network and require key-based authentication."},
            {"title": "HTTP service lacks transport encryption", "severity": "medium", "tool": "nikto", "evidence": f"{target}:80/tcp responds over HTTP", "remediation": "Redirect HTTP to HTTPS and enable HSTS after validation."},
            {"title": "Security headers are incomplete", "severity": "low", "tool": "whatweb", "evidence": "X-Content-Type-Options was not observed", "remediation": "Add baseline browser security headers at the reverse proxy."},
        ]
        steps = [(18, "Reconnaissance complete"), (44, "Service inventory normalized"), (70, "Findings correlated across tools"), (90, "Risk score calculated"), (100, "Report ready")]
        for progress, message in steps:
            yield {"progress": progress, "logs": [message]}
        score = calculate_score(findings)
        yield {"result": {"score": score, "risk": risk_level(score), "findings": findings, "services": ports.split(","), "summary": f"Demo evidence for {target} shows an exposed administration service and an unencrypted web endpoint. Prioritize network exposure reduction before hardening headers.", "action_plan": {"immediate": ["Restrict SSH access", "Confirm the target is authorized"], "short_term": ["Enforce HTTPS", "Review service inventory"], "medium_term": ["Automate recurring scans", "Track remediation ownership"]}}}
