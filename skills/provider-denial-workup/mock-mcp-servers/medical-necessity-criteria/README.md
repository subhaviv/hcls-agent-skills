# Medical-Necessity Criteria MCP Server (Demo)

A mock MCP server simulating a licensed medical-necessity criteria engine (InterQual/MCG-style). **All criteria are synthetic** — they mimic the structure, not the content, of real products.

## Tools exposed

| Tool | What it does |
|------|-------------|
| `list_criteria_sets()` | List available criteria sets (ID, title, CPT codes) |
| `lookup_criteria(criteria_id / cpt_code)` | Full requirement list + red-flag bypass conditions |
| `evaluate_medical_necessity(criteria_id, met_requirement_ids, red_flags_present)` | MEETS / DOES NOT MEET determination with gap list |

## Criteria sets included

| ID | Title | CPT |
|----|-------|-----|
| MN-RAD-014 | Lumbar MRI (w/o contrast) | 72148 |
| MN-CARD-021 | Nuclear cardiac stress test (SPECT MPI) | 78452 |
| MN-ADM-100 | Inpatient vs. Observation (general medical) | — |

## Setup

```bash
pip install mcp
python medical_necessity_mcp_server.py
```

Register in Amazon Quick: Settings → Capabilities → Connectors → + Add → Local → Command: `python`, Args: path to this file.
