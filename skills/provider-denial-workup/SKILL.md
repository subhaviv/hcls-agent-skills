---
name: provider-denial-workup
description: 'Draft a payer-ready insurance claim denial appeal letter for healthcare revenue cycle staff. Use when asked to "appeal a claim denial", "draft denial appeal", "write appeal letter", "CO-50 denial", "medical necessity denial", "CARC code appeal", "RARC code", "overturn denial", "prior auth denial", "timely filing denial", "denial workup", "payer denial response", "claim denial overturn".'
usage: Invoke when the user provides a denial letter, EOB, or CARC/RARC code and asks to draft an appeal.
version: 1.0.0
tags: [skill, category:reasoning, revenue-cycle, hcls]
---

# Provider Denial Workup

## When to Use

- User pastes a denial letter, EOB, or CARC/RARC code and asks to respond or appeal
- User says "draft denial appeal", "denial workup", "appeal this CO-50", or similar
- User wants to know if a denial is worth fighting and what the argument is
- Say "use the sample case" to run a demo with no real PHI

## Framework Selection

| Denial type | CARC | Appeal strategy |
|---|---|---|
| Medical necessity | CO-50/55/56/57 | Criteria mapping + clinical documentation |
| Prior auth absent | CO-197/198 | Submission proof + retroactive auth request |
| Timely filing | CO-29 | Proof of timely transmission (fax confirm / clearinghouse) |
| Coding / bundling | CO-97/4/16 | Distinct services + modifier support |
| Non-covered benefit | CO-96/PR-204 | Misclassification or exception — not necessity |
| Documentation | CO-226 | Supply requested records |

## Response Structure

When executing this skill, structure each response as:

1. **Classification** — denial type + CARC code identified
2. **Determination** — MEETS/DOES NOT MEET with specific requirements mapped
3. **Posture** — OVERTURN / PEND / ADVISE with rationale
4. **Draft** — the letter (or memo if ADVISE)
5. **Checklist** — reviewer items + appeal deadline

The workflow steps, decision trees, thresholds, and posture definitions below are for **internal reasoning only**. Do not reference them, quote them, or explain how you arrived at conclusions. The user does not need to know which step you are on or how the skill works. Deliver results directly — classification, determination, posture, letter, checklist. Nothing else.

## Workflow

### Step 1: Check MCP & collect inputs

- **Mode**: `agentic`
- **Input**: Available tools, user-provided denial + clinical context
- **Output**: `mcp_mode` (live/fallback), parsed inputs
- **On failure**: Default to fallback; ask for missing inputs

**835 ERA MCP (claims system):** Try `get_denial_details` with the provided claim ID. If available → pull denial details, member info, provider info, and appeal deadline automatically. Also call `get_claim_submissions` to retrieve submission history. If unavailable → proceed with user-provided input.

**Medical-Necessity Criteria MCP:** Try `list_criteria_sets`. If available → `mcp_mode = "live"`. If not → `mcp_mode = "fallback"`.

If the 835 MCP is live, fields retrieved from it satisfy the Step 2 input requirements automatically — skip asking the user for those fields.

### Step 2: Validate inputs — ask for anything missing

- **Mode**: `agentic`
- **Input**: User-provided denial text + clinical context
- **Output**: Confirmed inputs or clarifying questions

Extract the following from the denial text. For any field that cannot be found, ask the user before proceeding — do not guess or leave bracketed:

| Field | Source | Required? |
|---|---|---|
| Denial date | EOB / denial letter | Yes — needed to calculate appeal deadline |
| CARC / reason code | EOB | Yes — drives the entire appeal strategy |
| Payer name | EOB / letter header | Yes |
| Claim number | EOB | Yes |
| Member ID | EOB | Yes |
| Date of service | EOB / claim | Yes |
| CPT code(s) | EOB / claim | Yes |
| Payer's stated rationale | Denial letter verbatim | Yes |
| Patient name | EOB / letter | Preferred — skip if unavailable |
| ICD-10 diagnosis code(s) | EOB / claim | Preferred — skip if unavailable |

If any required fields are missing, **stop here**. Ask for all missing required fields in a single message. Do not proceed to Step 3 until the user has responded with the missing information.

### Step 3: Parse & assess the denial

- **Mode**: `agentic`
- **Tool**: MCP tools (live) or reasoning (fallback)
- **Input**: Validated denial text + clinical context
- **Output**: Denial type, determination, appeal posture
- **On failure**: Default to PEND posture

Classify denial type via `references/carc-codes.md`. Then apply the decision tree:

```
Is this a medical-necessity denial (CO-50/55/56/57)?
├─ Yes → Call MCP or reason from the stated criterion
│  ├─ Red flag present (cauda equina, progressive deficit, etc.)? → OVERTURN
│  ├─ All requirements met? → OVERTURN
│  ├─ Gap is fixable (documentation exists but wasn't submitted)? → PEND
│  └─ Genuinely unmet? → ADVISE
├─ Prior-auth (CO-197/198)? → See references/argument-patterns.md
├─ Timely filing (CO-29)? → Check proof of submission; ⚠️ appeal deadline is itself time-sensitive
├─ Coding/bundling (CO-97/4/16)? → Argue distinct services + modifier support
├─ Non-covered (CO-96/PR-204)? → Misclassification or exception; if genuinely excluded → ADVISE
└─ Documentation (CO-226)? → Supply what was requested; straightforward

```

**Key thresholds:**

- Conservative therapy requirement: ≥6 weeks (most imaging policies)
- Appeal window (commercial): 60–180 days from denial date
- Appeal window (Medicare Advantage): 60 calendar days
- Expedited appeal decision: 72 hours
- Extraction confidence <60% → warn user before proceeding
- Payer decision deadline (standard): 30 days from appeal receipt

### Step 4: Collect missing letter details

- **Mode**: `agentic`
- **Input**: Assessment from Step 2
- **Output**: Provider address, signer, attestations

Ask for letterhead details + whether key clinical dates are verified. Skip what they can't provide.

### Step 5: Draft the letter

- **Mode**: `agentic`
- **Input**: Assessment + collected details
- **Output**: Appeal letter + reviewer checklist
- **On failure**: If ADVISE posture, produce a memo instead

Use `references/letter-template.md` structure and `references/argument-patterns.md` argument. **Never fabricate** facts, codes, or policy citations — flag gaps instead.

### Step 6: Present for review

- **Mode**: `agentic`
- **Input**: Draft letter
- **Output**: Saved file or revision
- **Validate**: User explicitly approves

Show draft. Offer: save / edit / start over. Remind about human sign-off + appeal deadline.

## Worked Example (CO-50 — Medical Necessity)

**Denial:** Meridian Health Plan, CO-50, CPT 72148 (lumbar MRI), DOS 2026-06-10, denial date 2026-06-28. Rationale: "conservative treatment not documented prior to advanced imaging per policy RAD-014."

**Clinical context:** 47-year-old, 8 weeks low back pain with left leg radiation + L5-dermatomal numbness. PT 6 weeks (Apr 22–Jun 3, 2×/wk) + NSAIDs + activity modification — no improvement. Positive left SLR Jun 5. MRI ordered for surgical candidacy.

**Workup:**
- Classification: CO-50 medical-necessity imaging denial
- Determination: MEETS — ≥6-week PT threshold satisfied (6 weeks documented), neurological finding present (L5 numbness + positive SLR), failure of conservative management documented
- Posture: **OVERTURN** — payer rationale ("not documented") is a submission gap, not a clinical gap; PT records exist and must be attached
- Key argument: Quote RAD-014's ≥6-week requirement verbatim, attach PT session notes Apr 22–Jun 3, attach Jun 5 exam note with SLR finding

## Common Mistakes

- **Wrong:** Arguing medical necessity for a CO-96/PR-204 (benefit exclusion) denial. **Right:** CO-96 is non-covered — argue misclassification or exception, not necessity.
- **Wrong:** Citing a payer policy number without verifying it's current. **Right:** Leave unverified policy numbers bracketed and add to reviewer checklist.
- **Wrong:** Treating "does not meet" as always unappealable. **Right:** Check if the gap is fixable (documentation exists but wasn't attached). That's PEND, not ADVISE.
- **Wrong:** Drafting a strong overturn letter when the criteria genuinely aren't met. **Right:** Use ADVISE posture — tell the reviewer it's weak. Never manufacture arguments.
- **Wrong:** Ignoring the appeal filing deadline. **Right:** Always surface the deadline from the denial letter. If <14 days remaining, flag as urgent.
- **Wrong:** Using total gnomAD AF instead of filtering AF... just kidding. Using generic language like "please reconsider" without mapping to the specific denial reason. **Right:** Quote the denial code + rationale verbatim, then refute point-by-point.
- **Wrong:** Fabricating clinical dates or procedure details not in the supplied documentation. **Right:** If a fact isn't in the input, flag it as "needed from reviewer" — never invent.
- **Wrong:** Bundling multiple denial reasons into one vague appeal paragraph. **Right:** Address each CARC code separately under BASIS FOR APPEAL with its own argument.

## Guardrails

- No fabrication — flag, don't invent
- Human-in-the-loop — never auto-submit
- PHI — echo only what the letter needs
- Licensed criteria — reach via MCP, never bundle
- Audit trail — record every MCP call or fallback-reasoning step

## References (read only when needed)

- `references/carc-codes.md` — CARC/RARC code → denial type classification
- `references/argument-patterns.md` — denial type → appeal argument + required evidence
- `references/letter-template.md` — appeal letter structure to populate
- `references/sample-case.md` — synthetic CO-50 lumbar MRI denial for demos

