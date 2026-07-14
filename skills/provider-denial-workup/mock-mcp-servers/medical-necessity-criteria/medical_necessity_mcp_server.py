"""
Local MCP Server for Medical-Necessity Criteria (DEMO / SYNTHETIC)
===================================================================
A minimal MCP server that simulates a licensed medical-necessity criteria
service (InterQual / MCG style) for demoing the denial-appeal-drafter skill
end-to-end WITHOUT any real, licensed, or copyrighted criteria content.

⚠️  All criteria in criteria_data.json are FABRICATED for demonstration.
    They mimic the STRUCTURE of medical-necessity criteria (criterion set ->
    requirements -> meets/does-not-meet), not the content of any real product.
    Not for clinical or coverage use.

Setup:
    pip install mcp
    python medical_necessity_mcp_server.py

Then in Quick Desktop:
    Settings -> Capabilities -> MCP -> + Add
    Connection type: Local
    Command: python
    Args: /path/to/skills/provider-denial-workup/mock-mcp-servers/medical-necessity-criteria/medical_necessity_mcp_server.py
"""

import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Load the synthetic criteria data
DATA_PATH = Path(__file__).parent / "criteria_data.json"
with open(DATA_PATH) as f:
    _DATA = json.load(f)

CRITERIA_SETS = _DATA["criteria_sets"]

# Create the MCP server
mcp = FastMCP("Medical Necessity Criteria (Demo)")


def _find_by_id(criteria_id: str):
    for c in CRITERIA_SETS:
        if c["criteria_id"].upper() == criteria_id.upper():
            return c
    return None


@mcp.tool()
def list_criteria_sets() -> str:
    """List all available medical-necessity criteria sets with their ID, title,
    category, and associated CPT codes. Use this to discover which criteria exist
    before looking one up in detail."""
    lines = ["| Criteria ID | Title | Category | CPT Codes |", "|---|---|---|---|"]
    for c in CRITERIA_SETS:
        cpts = ", ".join(c["cpt_codes"]) if c["cpt_codes"] else "—"
        lines.append(f"| {c['criteria_id']} | {c['title']} | {c['category']} | {cpts} |")
    return "\n".join(lines) + "\n\n(Synthetic demo criteria — not real InterQual/MCG content.)"


@mcp.tool()
def lookup_criteria(criteria_id: str = "", cpt_code: str = "") -> str:
    """Look up a medical-necessity criteria set by its criteria_id (e.g. 'MN-RAD-014')
    or by CPT code (e.g. '72148'). Returns the full requirement list the service must
    meet, plus any red-flag conditions that bypass the standard criteria.

    Provide either criteria_id or cpt_code."""
    match = None
    if criteria_id:
        match = _find_by_id(criteria_id)
    elif cpt_code:
        for c in CRITERIA_SETS:
            if cpt_code in c["cpt_codes"]:
                match = c
                break

    if not match:
        avail = ", ".join(c["criteria_id"] for c in CRITERIA_SETS)
        return f"No criteria set found. Available: {avail}"

    out = [
        f"# {match['criteria_id']} — {match['title']}",
        f"**Category:** {match['category']}",
        f"**CPT codes:** {', '.join(match['cpt_codes']) if match['cpt_codes'] else '—'}",
        f"**Applicable diagnoses:** {', '.join(match['applicable_diagnoses'])}",
        "",
        "## Requirements (all required must be met)",
    ]
    for r in match["requirements"]:
        flag = "REQUIRED" if r.get("required") else "optional"
        out.append(f"- **{r['id']}** ({flag}): {r['description']}")
    if match.get("red_flags_bypass"):
        out.append("")
        out.append("## Red-flag conditions (bypass standard criteria — auto-justify)")
        for rf in match["red_flags_bypass"]:
            out.append(f"- {rf}")
    out.append("")
    out.append("_Synthetic demo criteria — not real InterQual/MCG content._")
    return "\n".join(out)


@mcp.tool()
def evaluate_medical_necessity(criteria_id: str, met_requirement_ids: str = "",
                               red_flags_present: str = "") -> str:
    """Evaluate whether a case meets a medical-necessity criteria set.

    Args:
        criteria_id: the criteria set to evaluate against (e.g. 'MN-RAD-014').
        met_requirement_ids: comma-separated requirement IDs the documentation
            supports (e.g. 'R1,R2,R3').
        red_flags_present: comma-separated red-flag conditions documented, if any.
            Any red flag auto-satisfies medical necessity.

    Returns a MEETS / DOES NOT MEET determination with the gap list — mirroring
    what a payer's criteria engine would return."""
    match = _find_by_id(criteria_id)
    if not match:
        avail = ", ".join(c["criteria_id"] for c in CRITERIA_SETS)
        return f"No criteria set found for '{criteria_id}'. Available: {avail}"

    met = {x.strip().upper() for x in met_requirement_ids.split(",") if x.strip()}
    red_flags = [x.strip() for x in red_flags_present.split(",") if x.strip()]

    # Red flag bypass
    if red_flags:
        return (
            f"# Determination: MEETS (red-flag bypass)\n"
            f"**Criteria:** {match['criteria_id']} — {match['title']}\n"
            f"**Reason:** Documented red-flag condition(s): {', '.join(red_flags)}. "
            f"These bypass the standard criteria and independently justify medical necessity.\n\n"
            f"_Synthetic demo determination._"
        )

    required = [r["id"] for r in match["requirements"] if r.get("required")]
    missing = [rid for rid in required if rid not in met]

    if not missing:
        verdict = "MEETS"
        detail = "All required criteria are satisfied by the documentation provided."
    else:
        verdict = "DOES NOT MEET"
        missing_desc = []
        for r in match["requirements"]:
            if r["id"] in missing:
                missing_desc.append(f"- **{r['id']}**: {r['description']}")
        detail = "The following required criteria are NOT supported by the documentation:\n" + "\n".join(missing_desc)

    return (
        f"# Determination: {verdict}\n"
        f"**Criteria:** {match['criteria_id']} — {match['title']}\n"
        f"**Requirements met:** {', '.join(sorted(met)) if met else 'none'}\n\n"
        f"{detail}\n\n"
        f"_Synthetic demo determination — mirrors a payer criteria-engine result. "
        f"Not real InterQual/MCG content._"
    )


if __name__ == "__main__":
    mcp.run()
