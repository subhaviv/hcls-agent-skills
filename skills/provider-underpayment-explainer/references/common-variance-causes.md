# Common Variance Causes

Root causes of claim underpayments, mapped to CARC/RARC codes and resolution approach.

---

## 1. Wrong Fee Schedule / Contract Rate

**CARC:** CO-45 (Charges exceed fee schedule/maximum allowable)
**What happened:** Payer applied the wrong rate — often an out-of-network tier, an expired rate, or a rate from a different contract period.
**Investigation:**
- Compare paid rate against the contract's fee schedule for the specific CPT + POS + modifier combination
- Check if the contract has an effective-date change the payer hasn't loaded
- Check if the claim crossed a contract-renewal boundary
**Resolution:** Cite the correct contract exhibit with effective dates. Request reprocessing at the contracted rate.

## 2. Multiple-Procedure Reduction (Incorrect)

**CARC:** CO-97 (Benefit included in another service), sometimes CO-45
**What happened:** Payer applied a 50% reduction on the secondary procedure, but the procedures were distinct/separately identifiable, or the reduction percentage is wrong.
**Investigation:**
- Were the procedures distinct? (different operative sites, different sessions, modifier -59/-XE)
- Is the payer applying NCCI edits correctly?
- Is the reduction 50% (standard) or something non-standard?
**Resolution:** Provide operative notes showing distinct services. Cite modifier -59 if applicable. If the reduction % is wrong, cite the contract's multi-procedure language.

## 3. Downcoding

**CARC:** CO-45 + RARC N362 (not billed at the appropriate level), or CO-59
**What happened:** Payer paid a lower-level code than what was billed (e.g., paid 99213 when 99214 was billed).
**Investigation:**
- Does the documentation support the billed code?
- Did the payer's clinical review determine a lower level?
- Is this a payer policy or an error?
**Resolution:** If documentation supports the billed level, cite the E/M guidelines and request reprocessing. If documentation is borderline, may not be worth disputing.

## 4. Sequestration (Medicare — NOT an error)

**CARC:** OA-23 or CO-253
**What happened:** Mandatory 2% Medicare payment reduction (Budget Control Act of 2011, extended annually).
**Investigation:**
- Is the patient Medicare? If yes, sequestration is correct and NOT disputable.
- Is the reduction exactly 2%? If more, there's an additional issue.
**Resolution:** ⚠️ Do NOT dispute sequestration — it's legally mandated. If the total variance exceeds 2%, investigate the additional reduction separately.

## 5. Coordination of Benefits (COB) Error

**CARC:** OA-22 (payment adjusted for coordination of benefits) or CO-22
**What happened:** Payer reduced payment claiming another insurance is responsible for a portion, but the COB was applied incorrectly.
**Investigation:**
- Does the patient actually have secondary coverage?
- Is this payer primary or secondary?
- Was the COB already handled by the other payer?
**Resolution:** If no secondary exists, provide proof (eligibility verification showing single coverage). If COB order is wrong, provide the payer's own eligibility response showing they are primary.

## 6. Modifier Reduction (Incorrect)

**CARC:** CO-4 (procedure code inconsistent with modifier) or CO-45
**What happened:** Payer applied a professional-component-only rate (-26) when global was billed, or vice versa. Or reduced for -TC when the provider owns the equipment.
**Investigation:**
- What modifier was on the claim vs. what the payer assumed?
- Does the provider bill globally for this service (owns equipment + interprets)?
**Resolution:** Clarify the modifier intent. If global is correct, cite the service arrangement and request reprocessing at the global rate.

## 7. Contract Rate Not Updated (Annual Escalator)

**CARC:** CO-45
**What happened:** The contract includes an annual rate escalator (e.g., 3% CPI increase effective Jan 1), but the payer is still paying the prior-year rate.
**Investigation:**
- Check the contract's escalator clause and effective date
- Compare the paid rate against both the old and new rates — does it match the old rate exactly?
**Resolution:** Cite the escalator clause, the effective date, and the calculated new rate. This is often a batch issue (affects all claims after the effective date) — escalate to the managed-care team for a bulk correction.

## 8. Place of Service (POS) Reduction

**CARC:** CO-45, sometimes CO-18
**What happened:** Payer paid at a lower POS rate (e.g., office rate when the service was in a facility, or vice versa).
**Investigation:**
- What POS code was on the claim?
- Does the payer's contract have POS-specific rates?
**Resolution:** If the POS on the claim is correct, cite it. If it was a coding error, correct and resubmit.

---

## Quick Lookup Table

| CARC | Most Likely Cause | First Check |
|------|-------------------|-------------|
| CO-45 | Wrong fee schedule / rate not updated / POS | Compare paid rate to contract |
| CO-97 | Multiple-procedure reduction | Were services distinct? |
| CO-45 + N362 | Downcoding | Documentation support the level? |
| OA-23 / CO-253 | Sequestration (2% Medicare) | ⚠️ NOT disputable |
| OA-22 / CO-22 | COB error | Does secondary actually exist? |
| CO-4 | Modifier reduction | Global vs. component billing? |
