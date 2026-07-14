# 835 ERA Claims MCP Server (Demo)

A mock MCP server simulating a payer remittance and claims system. **All data is synthetic** — claim IDs, member IDs, and provider details are fabricated for demo purposes only.

## Tools exposed

| Tool | What it does |
|------|-------------|
| `list_claims(member_id, date_range_start, date_range_end)` | Search denied claims by member or DOS range |
| `get_denial_details(claim_id)` | Full denial: CARC/RARC, rationale, policy cited, appeal deadline |
| `get_remittance(claim_id)` | Full 835 ERA: provider, member, service lines, adjustments |
| `get_claim_submissions(claim_id)` | Submission history: dates, channels, delivery status, confirmations |

## Demo claims included

| Claim ID | Scenario | CARC |
|---|---|---|
| CLM-2026-778213 | CO-50 lumbar MRI — medical necessity (Meridian) | CO-50 |
| CLM-2026-991042 | CO-197 prior auth — nuclear stress test (BlueCrest) | CO-197 |
| CLM-2026-554317 | CO-29 timely filing — appendectomy (UnitedHealthcare) | CO-29 |

## Demo flow

```
User: "Run a denial workup on claim CLM-2026-554317"
  → Skill calls get_denial_details("CLM-2026-554317")
      → returns CO-29, timely filing, deadline Aug 24 2026
  → Skill calls get_claim_submissions("CLM-2026-554317")
      → returns 3 submission attempts with fax failure + late EDI
  → Skill assesses posture → ADVISE
  → Drafts reviewer memo
```

## Setup

```bash
pip install mcp
python claims_mcp_server.py
```

Register in Claude Desktop: Settings → Capabilities → MCP → + Add → Local
Command: `python`
Args: `/path/to/skills/provider-denial-workup/mock-mcp-servers/claims-835-era/claims_mcp_server.py`
