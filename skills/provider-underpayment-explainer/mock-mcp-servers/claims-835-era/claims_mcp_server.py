"""
Local MCP Server for 835 ERA / Claims (DEMO / SYNTHETIC)
=========================================================
A mock MCP server simulating a payer remittance and claims system for demoing
the provider-denial-workup skill end-to-end without real claims data.

All claims, member IDs, and provider details are FABRICATED for demonstration.
Not for clinical, billing, or coverage use.

Setup:
    pip install mcp
    python claims_mcp_server.py

Then in Claude Desktop / Quick Desktop:
    Settings -> Capabilities -> MCP -> + Add
    Connection type: Local
    Command: python
    Args: /path/to/skills/provider-denial-workup/mock-mcp-servers/claims-835-era/claims_mcp_server.py
"""

import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

DATA_PATH = Path(__file__).parent / "claims_data.json"
with open(DATA_PATH) as f:
    _DATA = json.load(f)

CLAIMS = {c["claim_id"]: c for c in _DATA["claims"]}
SUBMISSIONS = {s["claim_id"]: s for s in _DATA["submission_history"]}

mcp = FastMCP("835 ERA Claims (Demo)")


def _claim_not_found(claim_id: str) -> str:
    available = ", ".join(CLAIMS.keys())
    return f"No claim found for '{claim_id}'. Available demo claims: {available}"


@mcp.tool()
def list_claims(member_id: str = "", date_range_start: str = "", date_range_end: str = "") -> str:
    """List denied claims, optionally filtered by member ID or date of service range.

    Args:
        member_id: Filter by payer member ID (e.g. 'UHC-3319047'). Optional.
        date_range_start: Filter by DOS on or after this date (YYYY-MM-DD). Optional.
        date_range_end: Filter by DOS on or before this date (YYYY-MM-DD). Optional.

    Returns a summary table of matching denied claims."""
    results = list(CLAIMS.values())

    if member_id:
        results = [c for c in results if c["member_id"].upper() == member_id.upper()]
    if date_range_start:
        results = [c for c in results if c["date_of_service"] >= date_range_start]
    if date_range_end:
        results = [c for c in results if c["date_of_service"] <= date_range_end]

    if not results:
        return "No claims match the specified filters."

    lines = ["| Claim ID | Member ID | DOS | Payer | CARC | Billed | Status |",
             "|---|---|---|---|---|---|---|"]
    for c in results:
        carc = c["service_lines"][0]["carc"]
        billed = f"${c['service_lines'][0]['billed_amount']:,.2f}"
        lines.append(f"| {c['claim_id']} | {c['member_id']} | {c['date_of_service']} | "
                     f"{c['payer']} | {carc} | {billed} | DENIED |")

    lines.append("\n_(Synthetic demo data — not real claims.)_")
    return "\n".join(lines)


@mcp.tool()
def get_denial_details(claim_id: str) -> str:
    """Get the full denial details for a claim from the 835 ERA — CARC/RARC codes,
    denial rationale, policy cited, billed/paid amounts, and appeal rights with deadline.

    Args:
        claim_id: The claim identifier (e.g. 'CLM-2026-778213')."""
    claim = CLAIMS.get(claim_id)
    if not claim:
        return _claim_not_found(claim_id)

    claim_type = claim.get("claim_type", "denial")
    lines = [
        f"# {'Underpayment' if claim_type == 'underpayment' else 'Denial'} Details — {claim_id}",
        f"**Member:** {claim['member_name']} (ID: {claim['member_id']}, DOB: {claim['member_dob']})",
        f"**Payer:** {claim['payer']} ({claim['payer_type'].replace('_', ' ')})",
        f"**Date of Service:** {claim['date_of_service']}",
    ]
    if claim_type == "underpayment":
        lines += [
            f"**Payment Date:** {claim.get('payment_date', '—')}",
            f"**Dispute Deadline:** {claim.get('dispute_deadline', '—')} ({claim.get('dispute_deadline_days', 90)} days from payment)",
        ]
    else:
        lines += [
            f"**Denial Date:** {claim.get('denial_date', '—')}",
            f"**Appeal Deadline:** {claim.get('appeal_deadline', '—')} ({claim.get('appeal_deadline_days', 60)} days from denial)",
        ]
    lines += ["", "## Service Lines"]
    for sl in claim["service_lines"]:
        lines += [
            f"- **CPT:** {sl['cpt']} — {sl['cpt_description']}",
            f"- **Diagnosis:** {', '.join(sl['icd10'])} — {', '.join(sl['icd10_descriptions'])}",
            f"- **Billed:** ${sl['billed_amount']:,.2f} | **Expected:** ${sl.get('expected_amount', sl.get('allowed_amount', 0)):,.2f} | **Paid:** ${sl['paid_amount']:,.2f}",
            f"- **CARC:** {sl['carc']} — {sl['carc_description']}",
            f"- **RARC:** {sl.get('rarc', '')} — {sl.get('rarc_description', '')}",
            f"- **Modifier:** {sl.get('modifier', '') or '—'}",
        ]
    lines += [""]
    if claim_type == "underpayment":
        lines += [
            "## Underpayment Rationale",
            claim.get("underpayment_rationale", "—"),
            "",
            "## Contract Reference",
            claim.get("contract_reference", "—"),
            "",
            "## Dispute Address",
            claim.get("dispute_address", "—"),
        ]
    else:
        lines += [
            "## Denial Rationale",
            claim.get("denial_rationale", "—"),
            f"**Policy cited:** {claim.get('policy_cited', '—')}",
            "",
            "## Appeal Rights",
            claim.get("appeal_rights", "—"),
        ]
    lines.append("\n_Synthetic demo data — not real claims._")
    return "\n".join(lines)


@mcp.tool()
def get_remittance(claim_id: str) -> str:
    """Get the full 835 ERA remittance detail for a claim — provider info, member info,
    all service lines with adjustments, and payment summary.

    Args:
        claim_id: The claim identifier (e.g. 'CLM-2026-778213')."""
    claim = CLAIMS.get(claim_id)
    if not claim:
        return _claim_not_found(claim_id)

    total_billed = sum(sl["billed_amount"] for sl in claim["service_lines"])
    total_paid = sum(sl["paid_amount"] for sl in claim["service_lines"])

    lines = [
        f"# 835 ERA Remittance — {claim_id}",
        "",
        "## Provider",
        f"**Name:** {claim['provider_name']}",
        f"**NPI:** {claim['provider_npi']} | **Tax ID:** {claim['provider_tax_id']}",
        f"**Address:** {claim['provider_address']}",
        f"**Phone:** {claim['provider_phone']} | **Fax:** {claim['provider_fax']}",
        "",
        "## Member / Patient",
        f"**Name:** {claim['member_name']} | **DOB:** {claim['member_dob']}",
        f"**Member ID:** {claim['member_id']}",
        f"**Payer:** {claim['payer']}",
        "",
        "## Claim",
        f"**Claim ID:** {claim_id}",
        f"**DOS:** {claim['date_of_service']} | **Payment/Denial Date:** {claim.get('payment_date', claim.get('denial_date', '—'))}",
        f"**Total Billed:** ${total_billed:,.2f} | **Total Paid:** ${total_paid:,.2f}",
        "",
        "## Service Line Adjustments",
    ]
    for sl in claim["service_lines"]:
        adjustment = sl["billed_amount"] - sl["paid_amount"]
        lines += [
            f"| CPT | Description | Billed | Expected | Paid | Adjustment | CARC | RARC | Modifier |",
            f"|---|---|---|---|---|---|---|---|---|",
            f"| {sl['cpt']} | {sl['cpt_description']} | ${sl['billed_amount']:,.2f} | "
            f"${sl.get('expected_amount', sl['paid_amount']):,.2f} | ${sl['paid_amount']:,.2f} | ${adjustment:,.2f} | {sl['carc']} | {sl.get('rarc', '')} | {sl.get('modifier', '') or '—'} |",
        ]
    lines.append("\n_Synthetic demo data — not real remittance._")
    return "\n".join(lines)


@mcp.tool()
def get_claim_submissions(claim_id: str) -> str:
    """Get the full submission history for a claim — all submission attempts with dates,
    channels (fax/EDI/portal), delivery status, and confirmation numbers.
    Also returns prior authorization history if applicable.

    Args:
        claim_id: The claim identifier (e.g. 'CLM-2026-554317')."""
    if claim_id not in CLAIMS:
        return _claim_not_found(claim_id)

    history = SUBMISSIONS.get(claim_id)
    if not history:
        return f"No submission history found for {claim_id}."

    lines = [f"# Submission History — {claim_id}", "", "## Claim Submissions"]
    for i, s in enumerate(history.get("submissions", []), 1):
        conf = s["confirmation"] or "— none —"
        lines += [
            f"### Attempt {i} — {s['submission_date']}",
            f"- **Channel:** {s['channel'].replace('_', ' ')}",
            f"- **Status:** {s['status'].upper()}",
            f"- **Confirmation:** {conf}",
            f"- **Notes:** {s['notes']}",
        ]

    if history.get("prior_auth_history"):
        lines += ["", "## Prior Authorization History"]
        for pa in history["prior_auth_history"]:
            conf = pa["confirmation"] or "— none —"
            lines += [
                f"- **Submitted:** {pa['submission_date']} via {pa['channel'].replace('_', ' ')}",
                f"- **Status:** {pa['status'].upper()} | **Confirmation:** {conf}",
                f"- **Notes:** {pa['notes']}",
            ]

    lines.append("\n_Synthetic demo data — not real submission records._")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
