# 835 ERA Claims MCP Server (Demo)

A mock MCP server simulating a payer remittance and claims system. **All data is synthetic** — claim IDs, member IDs, and provider details are fabricated for demo purposes only.

## Tools exposed

| Tool | What it does |
|------|-------------|
| `list_claims(member_id, date_range_start, date_range_end)` | Search claims by member or DOS range |
| `get_denial_details(claim_id)` | Full detail: CARC/RARC, rationale, payment/denial date, dispute or appeal deadline |
| `get_remittance(claim_id)` | Full 835 ERA: provider, member, service lines with expected vs paid, adjustments |
| `get_claim_submissions(claim_id)` | Submission history: dates, channels, delivery status, confirmations |

## Demo claims included

### Underpayment claims

| Claim ID | Payer | CPT | CARC | Scenario |
|---|---|---|---|---|
| CLM-2026-661488 | BlueCross BlueShield of Ohio | 27447 | CO-45 | Rate escalator not applied — paid at 2025 rate |
| CLM-2026-884201 | Aetna Better Health | 22612/22614/22840/99232 | CO-45 + OA-23 | Wrong % of MPFS on 4-line lumbar fusion |
| CLM-2026-447731 | Humana Gold Plus (Medicare Advantage) | 45378 | CO-45 + N362 | Downcode — colonoscopy paid at sigmoidoscopy rate |
| CLM-2026-552904 | Cigna HealthCare | 93306 | CO-97 | Modifier error — global billed, -26 applied |
| CLM-2026-339017 | Anthem Blue Cross | 47562 | CO-22 | COB applied in error — no secondary insurance |

### Paid correctly (baseline)

| Claim ID | Payer | CPT | Scenario |
|---|---|---|---|
| CLM-2026-712084 | UnitedHealthcare | 99214 | Office visit, correct contracted rate |
| CLM-2026-803345 | BCBS Illinois | 59400 | Global OB, correct rate |
| CLM-2026-921667 | Aetna Medicare Advantage | 29881 | Knee arthroscopy, correct MA rate |

## Demo prompts

```
"We have claim CLM-2026-884201 from Aetna — 4 service lines, all CO-45. Can you pull it up, work out what's underpaid vs correct, and draft a dispute letter?"

"Pull up CLM-2026-661488 and tell me why BCBS Ohio paid so much less than expected."

"CLM-2026-447731 — Humana is showing CO-45 and N362 on a colonoscopy. Is this disputable?"

"We got a CO-97 on CLM-2026-552904 from Cigna. Pull the remittance and explain the variance."

"CLM-2026-339017 — Anthem applied a CO-22 but this patient has no secondary coverage. What do we do?"
```

## Setup

```bash
pip install mcp
python claims_mcp_server.py
```

Register in Claude Desktop: Settings → Capabilities → MCP → + Add → Local  
Command: `python`  
Args: `/path/to/skills/provider-underpayment-explainer/mock-mcp-servers/claims-835-era/claims_mcp_server.py`
