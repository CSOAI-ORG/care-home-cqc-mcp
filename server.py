#!/usr/bin/env python3
"""
Care Home CQC Compliance MCP Server
====================================
By MEOK AI Labs | https://meok.ai

CQC Single Assessment Framework (SAF) compliance for adult social care + care homes.
Maps Quality Statements to evidence + AI-tool governance.

Install: pip install care-home-cqc-mcp
Run:     python server.py
"""

import json
import re
import time
import os
from collections import defaultdict
from typing import Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("care-home-cqc", instructions="MEOK AI Labs MCP Server")

_MEOK_API_KEY = os.environ.get("MEOK_API_KEY", "")

_call_counts: dict[str, list[float]] = defaultdict(list)
FREE_TIER_LIMIT = 10
WINDOW = 86400


def check_access(api_key: str = ""):
    """Fallback auth check when shared auth engine is not available."""
    if _MEOK_API_KEY and api_key and api_key == _MEOK_API_KEY:
        return True, "OK", "pro"
    if _MEOK_API_KEY and api_key and api_key != _MEOK_API_KEY:
        return False, "Invalid API key.", "free"
    return True, "OK, Pro at https://www.csoai.org/checkout", "free"


def _check_rate_limit(tool_name: str) -> None:
    now = time.time()
    _call_counts[tool_name] = [t for t in _call_counts[tool_name] if now - t < WINDOW]
    if len(_call_counts[tool_name]) >= FREE_TIER_LIMIT:
        raise ValueError(f"Rate limit exceeded for {tool_name}. Free tier: {FREE_TIER_LIMIT}/day. Upgrade at https://councilof.ai")
    _call_counts[tool_name].append(now)


@mcp.tool()
def map_to_quality_statement(evidence: str, domain: str = "Safe", api_key: str = "") -> dict:
    """Map evidence to CQC Quality Statements (Safe/Effective/Caring/Responsive/Well-led).

    Args:
        evidence: Free-text evidence description
        domain: One of Safe, Effective, Caring, Responsive, Well-led
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/5kQ6oJ0xS3ce8sl7ew8k91j"}
    _check_rate_limit("map_to_quality_statement")

    domains = {"Safe": ["S1", "S2", "S3", "S4", "S5", "S6"],
               "Effective": ["E1", "E2", "E3", "E4", "E5", "E6", "E7"],
               "Caring": ["C1", "C2", "C3"],
               "Responsive": ["R1", "R2", "R3"],
               "Well-led": ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9"]}

    statements = domains.get(domain, domains["Safe"])
    # Simple keyword mapping
    mapped = []
    evidence_lower = evidence.lower()
    keywords = {
        "S1": ["safeguard", "abuse", "protect"],
        "S2": ["risk", "assessment", "hazard"],
        "S3": ["infection", "clean", "hygiene"],
        "S4": ["medicine", "medication", "drug"],
        "S5": ["incident", "accident", "report"],
        "S6": ["staff", "training", "competency"],
    }
    for stmt, kws in keywords.items():
        score = sum(1 for kw in kws if kw in evidence_lower)
        if score > 0:
            mapped.append({"statement": stmt, "score": score, "keywords_matched": kws})

    return {"domain": domain, "statements": statements, "mapped_evidence": mapped,
            "evidence_summary": evidence[:200], "tier": tier}


@mcp.tool()
def ai_tool_governance_check(tool_name: str, purpose: str, data_types: list, api_key: str = "") -> dict:
    """AI-tool governance gap-check under SAF 'use of technology' theme.

    Args:
        tool_name: Name of the AI tool
        purpose: Intended purpose description
        data_types: List of personal data types processed
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/5kQ6oJ0xS3ce8sl7ew8k91j"}
    _check_rate_limit("ai_tool_governance_check")

    gaps = []
    if "consent" not in purpose.lower():
        gaps.append("Consent mechanism not explicitly documented")
    if len(data_types) > 2 and "anonymisation" not in purpose.lower():
        gaps.append("High data volume — consider anonymisation/pseudonymisation")
    if "access control" not in purpose.lower() and "role" not in purpose.lower():
        gaps.append("Access controls should be defined")

    return {"tool_name": tool_name, "gaps": gaps, "gap_count": len(gaps),
            "compliant": len(gaps) == 0, "tier": tier}


@mcp.tool()
def notifications_audit(notification_type: str, last_30_days: int = 0, api_key: str = "") -> dict:
    """Audit CQC statutory notifications coverage.

    Args:
        notification_type: e.g. 'death', 'abuse', ' safeguarding', 'infection'
        last_30_days: Number of notifications in last 30 days
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/5kQ6oJ0xS3ce8sl7ew8k91j"}
    _check_rate_limit("notifications_audit")

    required_types = ["death", "abuse", "safeguarding", "infection", "medication_error", "incident"]
    is_required = notification_type.lower() in required_types

    return {"notification_type": notification_type, "count_last_30d": last_30_days,
            "is_statutory": is_required, "required_types": required_types, "tier": tier}


@mcp.tool()
def mcap_template(care_home_name: str, service_user_count: int, api_key: str = "") -> dict:
    """Mock Comprehensive Assessment template.

    Args:
        care_home_name: Name of the care home
        service_user_count: Number of service users
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/5kQ6oJ0xS3ce8sl7ew8k91j"}
    _check_rate_limit("mcap_template")

    template = {
        "provider_name": care_home_name,
        "service_users": service_user_count,
        "key_lines": ["Safe", "Effective", "Caring", "Responsive", "Well-led"],
        "evidence_required": [
            "Safeguarding policy + logs",
            "Medication management audit",
            "Staff training matrix",
            "Infection prevention plan",
            "Complaints + compliments log",
        ],
    }
    return {"template": template, "tier": tier}


@mcp.tool()
def medication_administration_log_check(mar_entries: list, api_key: str = "") -> dict:
    """MAR chart governance audit.

    Args:
        mar_entries: List of MAR entry dicts with keys: date, time, medication, dose, signed_by
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/5kQ6oJ0xS3ce8sl7ew8k91j"}
    _check_rate_limit("medication_administration_log_check")

    issues = []
    for entry in mar_entries:
        if not entry.get("signed_by"):
            issues.append(f"Entry missing signature: {entry.get('medication', 'unknown')}")
        if not entry.get("dose"):
            issues.append(f"Entry missing dose: {entry.get('medication', 'unknown')}")

    return {"entries_checked": len(mar_entries), "issues": issues,
            "issue_count": len(issues), "compliant": len(issues) == 0, "tier": tier}


def main():
    mcp.run()


if __name__ == "__main__":
    main()


# ── MEOK monetization layer (Stripe upgrade · PAYG · pricing) ──────────
# Free tier is zero-config. Upgrade to Pro (unlimited) or pay-as-you-go per call.
import os as _meok_os
MEOK_STRIPE_UPGRADE = "https://buy.stripe.com/5kQ6oJ0xS3ce8sl7ew8k91j"  # Pro (unlimited)
MEOK_PAYG_KEY = _meok_os.environ.get("MEOK_PAYG_KEY", "")  # set to enable PAYG (x402 / ~GBP0.05 per call)
MEOK_PRICING = "https://meok.ai/pricing"


def meok_upsell(tier: str = "free") -> dict:
    """Monetization options for free-tier callers: Pro upgrade, PAYG, or pricing page."""
    if tier != "free":
        return {}
    return {"upgrade_url": MEOK_STRIPE_UPGRADE,
            "payg_enabled": bool(MEOK_PAYG_KEY),
            "pricing": MEOK_PRICING}
