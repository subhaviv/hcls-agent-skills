---
name: provider-underpayment-explainer
description: 'Analyze short-paid claims for healthcare revenue cycle staff. Given a remittance (835 ERA) showing a payment below expected reimbursement, identifies the root cause of the variance and drafts a provider-to-payer dispute letter. Triggers include "underpayment", "short-pay", "short-paid", "variance analysis", "payment dispute", "underpaid claim", "reimbursement variance", "ERA discrepancy", "contract rate", "fee schedule error", "CO-45", "payment integrity", "remittance dispute", "why was this paid less".'
usage: Invoke when a user presents a claim paid below the expected contracted rate and needs root-cause analysis and a dispute letter.
version: 1.0.0
tags: [skill, category:reasoning, revenue-cycle, underpayment, hcls]
---

# Provider Underpayment Explainer

## When to Use

- A claim paid less than the contracted rate — billed amount exceeds paid amount and the remittance shows CO-45, CO-97, CO-22, or OA-23
- A billing analyst asks why a claim was short-paid, what the variance is, or whether it's worth disputing
- A user pastes an 835 ERA remittance and asks to explain the adjustments or draft a dispute letter

## Framework Selection

Pick the right dispute pathway before investigating:

```
What is the primary CARC?
├─ CO-45 → Fee schedule / rate variance (most common)
│  ├─ Check: does paid amount match an older contract rate? → Escalator not applied
│  ├─ Check: does paid amount match out-of-network rate? → Wrong network tier
│  └─ Check: CO-45 + RARC N362? → Downcode — different workflow
├─ CO-97 → Bundling / multiple-procedure reduction
│  └─ Check: were procedures genuinely distinct? → Modifier -59 challenge
├─ CO-22 / OA-22 → COB reduction
│  └─ Check: does secondary insurance actually exist? → COB applied in error
├─ OA-23 / CO-253 → Sequestration (Medicare only)
│  └─ STOP — mandatory 2% reduction, not disputable
└─ CO-4 / CO-24 → Modifier error
   └─ Check: global billed but -26 (professional only) applied? → Rate correction
```

## Response Structure

Always present these sections in order — do not skip or merge them:

**1. Variance Summary** — lead with a table showing every service line:
| CPT | Description | Expected | Paid | Variance | % | Status |

Then total row. Run `scripts/compute_variance.py` for multi-line claims.

**2. Root Cause** — one paragraph per disputable line explaining exactly why the payment is wrong, mapped to a specific CARC and cause category from `references/common-variance-causes.md`.

**3. Dispute Viability** — one sentence verdict (Pursue / Don't Pursue / Pursue if Pattern) with the dollar amount and deadline.

**4. Draft Letter** — full dispute letter using `references/dispute-letter-template.md`. Ask format question (Word vs PDF) before presenting.

**5. Next Steps** — bulleted checklist: what to attach, where to send, deadline date, follow-up timing.

Do not narrate the decision tree or investigation steps in the response — present only the conclusion with supporting evidence.

## Core Procedure

1. **Identify claim source** — check if Claims ERA MCP (`get_remittance`) is available. If yes, pull remittance directly. If not, parse what the user provides.
2. **Extract service lines** — for each line: CPT, modifier, billed amount, paid amount, CARC, RARC, ICD-10 codes.
3. **Identify contract terms** — expected rate per line (% of MPFS, fee schedule, per-diem, etc.) and effective date. If not provided, ask before proceeding.
4. **Verify contract effective date** — confirm the rate is current as of the DOS. Annual escalators are the #1 cause of CO-45 underpayments.
5. **Route each line by CARC** — apply the Framework Selection tree above to classify each line before computing variance.
6. **Flag sequestration lines immediately** — OA-23/CO-253 lines are non-disputable. Remove from variance total and note for the user.
7. **Compute per-line variance** — `Variance = Expected − Paid`, `Variance% = Variance / Expected × 100`.
8. **For multi-line claims** — run `scripts/compute_variance.py --lines '[...]'` to get accurate per-line breakdown with MPR and sequestration flags.
9. **Apply threshold check** — Variance < $25 → below threshold (not worth pursuing). $25–$100 → pursue if pattern. > $100 → always pursue.
10. **Identify root cause per disputable line** — map CARC to cause category using `references/common-variance-causes.md`. State the specific error (e.g., "payer applied 72.25% of MPFS instead of contracted 85%").
11. **Check for pattern** — if the same CARC + CPT combination appears on other claims from the same payer, flag for contract-level escalation rather than individual dispute.
12. **Check dispute window** — most payers allow 60–120 days from payment date. Surface the deadline. If the window has passed, flag for late-dispute exception.
13. **Determine dispute viability** — Pursue / Don't Pursue / Pursue if Pattern verdict with dollar amount and rationale.
14. **Ask output format** — Word (.docx) default; ask only if format is ambiguous.
15. **Draft dispute letter** — using `references/dispute-letter-template.md`. Include: claim identifiers, expected vs. paid vs. variance, CARC cited, contract exhibit and effective date, specific rate math, requested action (reprocess + remit $X).
16. **Exclude non-disputable lines** — sequestration and correctly-applied MPR lines must not appear in the letter body or the requested amount.
17. **Build enclosures checklist** — contract exhibit page, ERA remittance, MPFS rate source, operative report (if modifier dispute), eligibility verification (if COB dispute).
18. **Flag pattern escalation** — if 3+ claims show the same variance, recommend the managed-care team for a bulk reprocessing request rather than individual letters.
19. **Present next steps** — deadline date, send-to address (Provider Disputes / Payment Integrity, not Appeals), follow-up timeline (call at 30 days if no acknowledgment).

## Workflow

### Step 1: Collect inputs & check MCP
- **Mode**: `agentic`
- **Input**: Remittance data + contract/expected rate
- **Output**: Parsed claim details, `mcp_mode` (live/fallback)
- **On failure**: Ask for missing data; default to fallback

Check for Claims ERA MCP (`get_remittance`) and Contract/Fee Schedule MCP (`get_expected_rate`). If available → pull data directly. If not → use what the user provides.

### Step 2: Compute the variance
- **Mode**: `agentic`
- **Input**: Paid amount + expected amount per service line
- **Output**: Per-line and total variance amounts + percentages
- **On failure**: Ask user to confirm the expected rate

For single-line claims, compute inline:
```
Variance = Expected - Paid
Variance % = (Expected - Paid) / Expected × 100
```

For multi-line claims with complex stacking (multiple-procedure reductions, COB layers, sequestration mixed in), run `scripts/compute_variance.py` to get accurate per-line breakdown and automatically flag non-disputable lines:
```bash
python scripts/compute_variance.py --lines '[
  {"cpt":"27447","description":"...","billed":42500,"expected":38750,"paid":31200,"carc":"CO-45"},
  {"cpt":"20610","description":"...","billed":520,"expected":260,"paid":130,"carc":"CO-97","modifier":"-51"}
]'
# or from a CSV:
python scripts/compute_variance.py --csv service_lines.csv
```

The script flags:
- `NON-DISPUTABLE` — sequestration lines (OA-23/CO-253); exclude from dispute letter
- `[MPR]` — multiple-procedure reduction lines (CO-97); verify the 50% reduction is correct
- `BELOW THRESHOLD` — variance < $25; not worth pursuing individually

**Threshold check:**
- Variance < $25 → flag as likely not worth pursuing (cost of the letter > recovery)
- Variance $25–$100 → pursue if pattern/batch exists
- Variance > $100 → always pursue

### Step 3: Identify the root cause
- **Mode**: `agentic`
- **Input**: CARC/RARC codes from the ERA + contract terms + service details
- **Output**: Root cause category + explanation
- **On failure**: If cause unclear, list top 2–3 likely causes and ask user to confirm

Apply the decision tree:

```
What adjustment code(s) did the payer apply?
├─ CO-45 (charges exceed fee schedule) → Wrong fee schedule or contract rate
│  ├─ Rate matches an older contract version? → Contract rate not updated
│  ├─ Rate matches out-of-network schedule? → Wrong network tier applied
│  └─ Rate matches Medicare × % but wrong %? → Incorrect % of Medicare calculation
├─ CO-97 (bundled) → Multiple-procedure reduction
│  ├─ Modifier -51 applied? → Was secondary procedure reduction correct (50%)?
│  └─ Services genuinely distinct? → Challenge the bundle — modifier -59 may be warranted
├─ CO-45 + RARC N362 (downcoding) → Payer paid a lower-level code
│  ├─ Documentation supports the billed code? → Challenge the downcode
│  └─ Documentation ambiguous? → May not be worth disputing
├─ CO-253 / OA-23 (sequestration) → Mandatory 2% Medicare reduction
│  └─ Is patient Medicare? → If yes, sequestration is correct (not disputeable)
├─ OA-22 / CO-22 (COB) → Coordination of benefits adjustment
│  ├─ Is there truly a secondary payer? → If no, COB applied in error
│  └─ Secondary payer exists but primary should have paid more? → Recalculate
├─ CO-4 / CO-24 (modifier) → Modifier-related reduction
│  ├─ -26 (professional only) applied when global billed? → Facility vs. professional error
│  └─ -TC (technical only) reduced when facility owns equipment? → Challenge
└─ None of the above → Check references/common-variance-causes.md for less common scenarios
```

### Step 4: Assess dispute viability
- **Mode**: `agentic`
- **Input**: Root cause + variance amount + payer
- **Output**: Pursue / don't pursue recommendation
- **On failure**: Default to pursue if > threshold

Consider:
- Dollar amount vs. cost-of-effort (~$25 floor)
- Is it a pattern (same payer, same code, multiple claims)? If yes → escalate as a contract issue, not a one-off dispute
- Payer recovery history (if known)
- Time since payment (most payer dispute windows: 60–120 days)

### Step 5: Draft the dispute letter
- **Mode**: `agentic`
- **Input**: Root cause + variance + contract reference
- **Output**: Dispute letter + attachments checklist
- **On failure**: If "don't pursue," produce a brief note explaining why

Draft using `references/dispute-letter-template.md`:
- Claim identifiers
- Expected payment + contract provision cited
- Actual payment + the payer's adjustment code
- Variance amount
- Root cause explanation (why this is incorrect)
- Requested action: reprocess and remit $X difference
- Enclosures list

### Step 6: Present for review
- **Mode**: `agentic`
- **Input**: Draft letter
- **Output**: Saved file or revision
- **Validate**: User approves

Show draft. Offer: save / edit / don't pursue. Note the dispute filing deadline.

**Output format:** Default to Word (.docx) — dispute letters are typically edited before sending. If the user's intent is unclear (e.g., they said "save it" or "give me the letter" without specifying), ask:

> "What format would you like for the dispute letter — Word (.docx) for editing, or PDF for sending directly?"

Do not ask if the user already specified a format. Never default to PDF without confirmation — PDFs require additional steps if the billing team needs to fill in letterhead details.

## Common Mistakes

- **Wrong:** Disputing a 2% Medicare sequestration reduction — it's mandatory and correct.
  **Right:** Sequestration is not an error. Flag it for the user but don't draft a dispute.
- **Wrong:** Assuming the loaded contract rate is correct without checking effective dates.
  **Right:** Contract rates change (annual escalators, amendments). Ask: "Is this rate current as of the DOS?"
- **Wrong:** Disputing a $12 variance — the cost of the letter exceeds the recovery.
  **Right:** Below $25, recommend batch review or write-off unless it's a pattern across many claims.
- **Wrong:** Sending a dispute to the Appeals department.
  **Right:** Underpayments go to Provider Disputes / Payment Integrity — not the same team as denial appeals.
- **Wrong:** Citing "our contract says $X" without the specific section or exhibit.
  **Right:** Reference the contract exhibit, effective date, and fee schedule line item.
- **Wrong:** Treating a downcode as always incorrect.
  **Right:** Downcoding may be legitimate if documentation doesn't support the billed level. Check before disputing.
- **Wrong:** Missing the dispute filing deadline.
  **Right:** Most payers allow 60–120 days from payment date for disputes. Always surface this deadline.
- **Wrong:** Treating each short-pay as isolated when it's a systematic pattern.
  **Right:** If the same variance appears on 10+ claims, escalate to the contract/managed-care team — it's a rate-loading issue, not a claim-level dispute.
- **Wrong:** Including all service lines in the dispute letter regardless of CARC.
  **Right:** Only disputable lines belong in the letter. Sequestration (OA-23) and correctly-applied MPR (CO-97 at 50%) must be excluded — including them undermines the letter's credibility.
- **Wrong:** Computing variance as billed − paid.
  **Right:** Variance = expected (contracted rate) − paid. Billed amount is irrelevant — the contract sets the ceiling, not the charge description file.

## Worked Example

**Claim:** CLM-2026-884201, Aetna Better Health, 4 service lines, DOS 2026-04-22

| CPT | Description | Expected | Paid | Variance | % | Status |
|-----|-------------|----------|------|----------|---|--------|
| 22612 | Lumbar fusion, single level | $52,400 | $44,540 | **$7,860** | 15.0% | **PURSUE** |
| 22614 | Fusion, additional level (-51) | $14,250 | $14,250 | $0 | 0% | MPR correct |
| 22840 | Posterior instrumentation (-51) | $9,100 | $9,100 | $0 | 0% | MPR correct |
| 99232 | Subsequent hospital care | $210 | $205.80 | $4.20 | 2% | NON-DISPUTABLE |
| **Total** | | **$75,960** | **$68,095.80** | **$7,860 disputable** | | |

**Root cause (CPT 22612):** Contract (Exhibit C, effective 2025-07-01) requires 85% of MPFS. 2026 MPFS rate = $61,647.06 × 85% = $52,400. Payer paid $44,540, which equals $61,647.06 × 72.25% — the wrong percentage was loaded.

**CPT 22614 & 22840:** 50% MPR via CO-97 is standard NCCI policy for add-on/instrumentation codes. Not disputable unless operative report shows distinct sites (then modifier -59 applies).

**CPT 99232:** OA-23 sequestration. Mandatory 2% Medicare reduction. Do NOT include in dispute.

**Dispute letter:** Request reprocessing of CPT 22612 only, remit $7,860. Cite Exhibit C, Section 2, effective 2025-07-01, with the 85% × MPFS calculation shown explicitly.

## Guardrails

- Never fabricate contract terms or rates — if not provided, ask
- Human-in-the-loop — always draft-and-review
- Surface the dispute deadline
- Flag patterns (systematic underpayment) for contract-level escalation
- Audit trail — record what was compared and the root-cause determination

## References (read only when needed)

- `references/dispute-letter-template.md` — dispute letter structure
- `references/common-variance-causes.md` — root causes with CARC mapping + resolution approach
- `references/sample-underpayment.md` — synthetic short-pay case for demos
- `scripts/compute_variance.py` — multi-line variance calculator; run with `--demo` to verify setup
