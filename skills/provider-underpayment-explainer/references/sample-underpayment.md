# Sample Underpayment Cases — DEMO ONLY (synthetic, no real PHI)

Say "use the single-line sample case" or "use the multi-line sample case" to run the skill end-to-end without real data.

---

## The claim

- **Payer:** BlueCross BlueShield of Ohio (commercial PPO)
- **Patient:** Angela R. Morrison (synthetic)
- **Member ID:** BCBS-7720194
- **Provider:** Summit Orthopedics, NPI 1663000000
- **DOS:** 2026-05-14
- **Service:** CPT 27447 — Total knee arthroplasty (TKA)
- **Place of Service:** 22 (Outpatient Hospital)
- **Claim Number:** CLM-2026-661488

## The remittance (835 ERA)

| Field | Value |
|---|---|
| Billed amount | $42,500.00 |
| Expected payment (per contract) | $38,750.00 (Exhibit B, effective 2026-01-01: 110% of Medicare) |
| Actual payment | $31,200.00 |
| Variance | **-$7,550.00 (19.5% short)** |
| CARC | CO-45 — Charges exceed fee schedule/maximum allowable |
| RARC | N/A |
| Payment date | 2026-06-02 |

## Contract reference

- **Contract:** BCBS Ohio Provider Agreement, effective 2026-01-01
- **Exhibit B, Section 3:** Orthopedic surgical procedures reimbursed at **110% of current Medicare Physician Fee Schedule** (MPFS)
- **2026 Medicare rate for CPT 27447 (facility):** $35,227.27
- **Expected at 110%:** $35,227.27 × 1.10 = **$38,750.00**
- **Prior-year contract (2025):** 100% of MPFS → $31,200 ← this matches what was paid

## Root cause

The payer is paying at the **2025 contract rate (100% of MPFS = $31,200)** instead of the **2026 rate (110% of MPFS = $38,750)**. The 10% escalator effective 2026-01-01 was not loaded into the payer's adjudication system.

## Expected outcome

- **Root cause:** Contract rate not updated (annual escalator not applied)
- **Dispute viable:** Yes — clear contract provision, large dollar variance, likely a batch issue across all post-Jan-1 claims
- **Posture:** Dispute + escalate to managed-care team (pattern issue, not one-off)
- **Action:** Cite Exhibit B effective date, show the math, request reprocessing at $38,750. Also flag: "Please confirm this rate is now loaded for future claims."

---

## Multi-Line Sample Case — DEMO ONLY (synthetic, no real PHI)

Say "use the multi-line sample case" to demo complex stacking across four service lines with mixed denial types.

---

## The claim

- **Payer:** Aetna Better Health (commercial HMO)
- **Patient:** Marcus T. Rivera (synthetic)
- **Member ID:** AET-4481092
- **Provider:** Coastal Spine & Orthopedics, NPI 1720000001
- **DOS:** 2026-04-22
- **Service:** Lumbar spinal fusion with instrumentation — multi-level
- **Place of Service:** 21 (Inpatient Hospital)
- **Claim Number:** CLM-2026-884201

## The remittance (835 ERA) — 4 service lines

| CPT | Description | Billed | Expected | Paid | CARC | RARC | Modifier |
|-----|-------------|--------|----------|------|------|------|----------|
| 22612 | Lumbar fusion, posterior, single level | $58,000.00 | $52,400.00 | $44,540.00 | CO-45 | — | — |
| 22614 | Lumbar fusion, posterior, each additional level | $28,500.00 | $14,250.00 | $14,250.00 | CO-97 | — | -51 |
| 22840 | Posterior segmental instrumentation | $18,200.00 | $9,100.00 | $9,100.00 | CO-97 | — | -51 |
| 99232 | Subsequent hospital care, moderate complexity | $420.00 | $210.00 | $205.80 | OA-23 | — | — |

**Payment date:** 2026-05-10  
**Total billed:** $105,120.00  
**Total expected:** $75,960.00  
**Total paid:** $68,095.80  
**Total variance:** $7,864.20 — of which **$7,860.00 is disputable**

## Contract reference

- **Contract:** Aetna Better Health Provider Agreement, effective 2025-07-01
- **Exhibit C, Section 2:** Spinal surgical procedures reimbursed at **85% of current Medicare Physician Fee Schedule** (MPFS), inpatient facility rate
- **2026 Medicare rate for CPT 22612 (inpatient facility):** $61,647.06
- **Expected at 85%:** $61,647.06 × 0.85 = **$52,400.00**
- **Paid amount:** $44,540.00 — matches 72.25% of MPFS, not 85%

## Root causes (one per line)

| CPT | Root Cause | Disputable |
|-----|-----------|-----------|
| 22612 | Wrong % of Medicare applied — paid at 72.25% instead of contracted 85% (CO-45) | **Yes — $7,860.00** |
| 22614 | 50% multiple-procedure reduction applied (CO-97, modifier -51) — standard and correct | No |
| 22840 | 50% multiple-procedure reduction applied (CO-97, modifier -51) — standard and correct | No |
| 99232 | Medicare sequestration — mandatory 2% reduction (OA-23, $4.20) | No |

## Expected outcome

- **CPT 22612:** Dispute — payer applied 72.25% of MPFS instead of contracted 85%. Variance $7,860.00. Cite Exhibit C, Section 2 with the calculated rate.
- **CPT 22614 & 22840:** Do NOT dispute — 50% MPR is correct per NCCI for add-on/instrumentation codes billed with a primary procedure.
- **CPT 99232:** Do NOT dispute — sequestration is mandatory and correct.
- **Disputable total:** $7,860.00 (CPT 22612 only)
- **Posture:** Single-claim dispute. Check other Aetna inpatient spinal claims — if the same wrong % appears systematically, escalate as a rate-loading error.

## Script input for compute_variance.py

```bash
python scripts/compute_variance.py --lines '[
  {"cpt":"22612","description":"Lumbar fusion posterior single level","billed":58000,"expected":52400,"paid":44540,"carc":"CO-45"},
  {"cpt":"22614","description":"Lumbar fusion each additional level","billed":28500,"expected":14250,"paid":14250,"carc":"CO-97","modifier":"-51"},
  {"cpt":"22840","description":"Posterior segmental instrumentation","billed":18200,"expected":9100,"paid":9100,"carc":"CO-97","modifier":"-51"},
  {"cpt":"99232","description":"Subsequent hospital care","billed":420,"expected":210,"paid":205.80,"carc":"OA-23"}
]'
```
