# Provider Denial Workup

An AI-powered skill that **analyzes** insurance claim denials, **evaluates** medical-necessity criteria, **determines** appeal posture, and **drafts** review-ready appeal letters for healthcare provider revenue-cycle teams.

## What it does

Paste a claim denial (or let the skill pull it from the 835 ERA MCP) → the skill:

1. **Classifies** the denial type (medical necessity, timely filing, prior auth, coding, etc.)
2. **Evaluates** the case against payer criteria (via MCP or bundled references)
3. **Determines** the appeal posture:
   - **OVERTURN** — criteria met, strong appeal (drafts a confident letter)
   - **PEND** — fixable gap, request reconsideration (drafts a documentation-request letter)
   - **ADVISE** — genuinely unmet, won't manufacture a weak argument (produces an internal memo instead)
4. **Drafts** the appeal letter with clinical narrative, policy citation, and reviewer checklist
5. **Flags** anything it can't verify — never fabricates clinical facts or policy numbers

**Draft-and-review only.** A human verifies and signs off before anything is submitted.

## Target users

The denial-appeal workflow **already lives outside the EHR** — analysts work in Word, payer portals, and spreadsheets. This skill fits naturally into that workspace without requiring a context-switch.

| Persona | Scenario | Why it fits |
|---|---|---|
| **Denials & appeals analyst** | Stack of denied claims to work through | 30–45 min per case today → 3–5 min. They're already outside the EHR for this work. |
| **Physician advisor** | Preparing for a peer-to-peer call with a payer medical director | Needs a criteria-grounded argument brief quickly. |
| **Revenue cycle manager / director** | Evaluating high-dollar denials — which to fight? | Strategic triage (OVERTURN/PEND/ADVISE), not just letter-writing. |
| **Small practice / billing service** | No enterprise PA tools (Cohere, Myndshft) | This is their AI analyst — affordable and immediate. |

**Not a fit:** frontline auth coordinators in a high-volume queue inside Epic/CoverMyMeds. That work is EHR-embedded; adding another tool adds friction.

## How to use

**Trigger:** Say "draft denial appeal", "denial workup", or paste a denial with a CARC code.

**Demo mode:** Say "use the sample case" for a synthetic CO-50 lumbar MRI denial (no real PHI needed).

**With MCP servers configured:** the skill pulls denial data and validates criteria automatically. **Without MCP:** works from bundled references — still structured and policy-grounded, with an honest caveat in the audit trail.

## Denial types supported

| CARC | Denial Type | Appeal Strategy |
|------|-------------|-----------------|
| CO-50/55/56/57 | Medical necessity | Criteria mapping + clinical documentation |
| CO-197/198 | Prior authorization absent | Submission proof + retroactive auth request |
| CO-29 | Timely filing | Proof of timely transmission |
| CO-97/4/16 | Coding / bundling | Distinct services + modifier support |
| CO-96 / PR-204 | Non-covered benefit | Misclassification or exception argument |
| CO-226 | Documentation | Supply requested records |

## MCP integrations (optional, enhance the skill)

| MCP Server | What it adds | Required? |
|---|---|---|
| **Medical-Necessity Criteria** | Validates case against criteria sets (InterQual/MCG-style) — formal MEETS/DOES NOT MEET determination | No — falls back to reasoning from bundled refs |
| **Claims ERA (835)** | Pulls denial details + submission history directly (no copy-paste) | No — user pastes denial text instead |

Both are available as demo servers in this repo under `mock-mcp-servers/`.

## File structure

```
provider-denial-workup/
├── SKILL.md                          ← the skill (~150 lines)
├── README.md                         ← this file
├── references/                       ← loaded only when needed
│   ├── carc-codes.md                 ← CARC/RARC → denial type classification
│   ├── argument-patterns.md          ← denial type → appeal argument + required evidence
│   ├── letter-template.md            ← appeal letter skeleton
│   └── sample-case.md                ← synthetic CO-50 demo case
└── mock-mcp-servers/
    ├── medical-necessity-criteria/   ← mock InterQual/MCG criteria engine
    └── claims-835-era/               ← mock 835 ERA / claims remittance system
```

## Install

**Claude.ai (Cowork):** Customize → Skills → + Create skill → Upload a skill → select `provider-denial-workup.zip`

**Claude Code (this project):**
```bash
./install.sh --target claude-code
```

**Claude Code (global, all projects):**
```bash
ln -sfn $(pwd)/skills/provider-denial-workup ~/.claude/skills/provider-denial-workup
```

## Design principles

- **Flag, don't fabricate** — if something isn't in the input or an MCP result, it's flagged for the reviewer
- **Can say "don't appeal"** — the ADVISE posture means the skill won't draft a strong letter for a losing case
- **MCP for live/licensed data** — InterQual/MCG content is licensed; reach it via MCP, never bundle it
- **Progressive disclosure** — SKILL.md stays lean; reference material loads only when needed
- **Audit trail** — every criteria check (MCP or fallback-reasoning) is recorded
- **Human-in-the-loop** — always draft-and-review; never auto-submit
