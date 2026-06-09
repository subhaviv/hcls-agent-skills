# Healthcare Ops Chatbot Demo: Skills + Code Exploration on Tuva

## Purpose

Demonstrates the chatbot frontend running against a real healthcare analytics codebase ([Tuva](https://github.com/tuva-health/tuva)), showing how HCLS skills combine with code exploration to validate implementations and guide new feature development.

## Setup

### Prerequisites

- Node.js 18+
- `kiro-cli` installed and authenticated
- Tuva repo cloned to `~/Repositories/tuva/`

### Install Skills

```bash
cd ~/Repositories/awesome-kiro-agent-skills-for-hcls
./install.sh --target kiro --mode multiagent --path ~/Repositories/tuva/
```

This installs 38 HCLS skills + 9 multiagent configs into `~/Repositories/tuva/.kiro/`.

### Start the Demo

```bash
# Terminal 1 — frontend
cd demo && npm run dev

# Terminal 2 — backend (pointed at Tuva)
cd demo && DEMO_CWD=~/Repositories/tuva npm run server
```

Open http://localhost:5173 and select `hcls-multiagent` in the agent dropdown.

---

## Prompt 1: Validate CMS-HCC V28 Hierarchy Implementation

```
What are the correct CMS-HCC V28 disease hierarchy rules? Check if Tuva's int_hcc_hierarchy.sql implements them correctly — specifically the diabetes hierarchy (HCC 17→18→19) and the CHF hierarchy (HCC 85→86→87→88).
```

### What Happens

1. **Task list created** — agent plans: find the SQL, research V28 rules, validate
2. **Code exploration** — finds `models/data_marts/cms_hcc/intermediate/cms_hcc__int_hcc_hierarchy.sql`, reads the hierarchy resolution logic
3. **Skill activation** — loads `risk-adjustment-strategy` and/or `risk-adjustment` for V28-specific hierarchy rules
4. **Subagent delegation** (multiagent mode) — routes to `hcls-healthcare-ops` specialist with domain skills
5. **Key finding** — the agent corrects the premise: HCC 17→18→19 and 85→86→87→88 are V24 codes. V28 renumbered everything (diabetes is HCC 35→36→37→38, heart failure is HCC 221→222→...→227)

### Skills Triggered

| Skill | Why |
|-------|-----|
| `risk-adjustment-strategy` | V28 hierarchy rules, disease interaction logic |
| `risk-adjustment` | ICD-10-to-HCC crosswalk, hierarchy resolution code patterns |

### What to Observe in the UI

- Inline tool chips showing file reads and searches
- Sticky task list tracking progress
- Subagent card with `hcls-healthcare-ops` specialist streaming
- Skill badges appearing inside the subagent tab
- Markdown tables rendering the V28 hierarchy rules

---

## Prompt 2: Add a New HEDIS Measure

```
Add a new HEDIS measure (Breast Cancer Screening - BCS) to the Tuva quality measures data mart. Show me the existing measure structure and what models/seeds I need to create.
```

### What Happens

1. **Code exploration** — discovers the quality measures data mart structure at `models/data_marts/quality_measures/`
2. **Pattern analysis** — reads existing measures (e.g., NQF 0034 Colorectal Cancer Screening) to understand the model pattern
3. **Skill activation** — loads `hedis-measure-specification` for BCS measure logic (denominator, numerator, exclusions)
4. **Implementation guidance** — produces the list of models and seeds needed, following Tuva's conventions

### Skills Triggered

| Skill | Why |
|-------|-----|
| `hedis-measure-specification` | BCS measure definition, denominator/numerator/exclusion logic, age/gender criteria |
| `quality-measures` | HEDIS calculation patterns, continuous enrollment checks, value set structure |

### What to Observe in the UI

- Agent exploring multiple directories to understand the pattern
- Skill badges for HEDIS-specific knowledge
- Structured output with file paths and SQL patterns matching Tuva's conventions

---

## Key Takeaways

1. **Skills + code exploration = validated answers.** The agent doesn't just recite V28 rules — it reads the actual SQL and validates correctness.
2. **Domain correction.** The agent catches that V24 and V28 use different HCC numbering, preventing a common confusion.
3. **Pattern-following.** For new features, the agent discovers existing conventions and produces code that matches the project's style.
4. **Multiagent routing.** The coordinator delegates to `hcls-healthcare-ops` which has the relevant skills loaded, keeping context efficient.
