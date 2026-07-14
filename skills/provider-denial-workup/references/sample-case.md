# Sample Case — DEMO ONLY (synthetic, no real PHI)

Say "use the sample case" to run the skill end-to-end without real data.

## The denial

- **Payer:** Meridian Health Plan (commercial PPO)
- **CARC:** CO-50 — not deemed medically necessary
- **Service:** CPT 72148 — MRI lumbar spine w/o contrast
- **Diagnosis:** ICD-10 M54.16 — lumbar radiculopathy
- **DOS:** 2026-06-10 | **Denial date:** 2026-06-28
- **Claim:** CLM-2026-778213 | **Member:** MHP-4471902
- **Payer rationale:** "conservative treatment not documented prior to advanced imaging per medical policy RAD-014"

## Clinical context

47-year-old with 8 weeks progressive low back pain radiating to the left leg with L5-dermatomal numbness. Completed 6 weeks of PT (2x/wk, Apr 22–Jun 3, 2026) + NSAIDs + activity modification — no meaningful improvement. Positive left straight-leg raise on Jun 5 visit. Ordering physician documented concern for lumbar disc herniation with nerve-root compression. MRI ordered for surgical candidacy after failed conservative management.

## Expected outcome

Policy RAD-014 requires ≥6 weeks conservative therapy — which was met. If MCP is live, maps to criteria `MN-RAD-014` → determination: **MEETS** → posture: **OVERTURN**. Strong appeal candidate.
