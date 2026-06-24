# Evaluating Domain-Specific Agent Skills for Healthcare and Life Sciences: A Pairwise Comparison Study

## Abstract

We evaluate whether loading domain-specific reasoning and pipeline skills into an AI coding assistant improves response quality for healthcare and life sciences (HCLS) questions. Across **3 primary evaluation versions** (v3, v8, v9) using two backend harnesses (kiro-cli and Strands SDK), two model generations (Sonnet 4.5 and 4.6), and varying baseline conditions, we measure the impact of 38 domain skills on 410 test prompts spanning 12 HCLS domains. Claude Opus 4.7 serves as the judge, scoring responses on five dimensions: scientific accuracy, coherence, relevance, critical thinking, and actionability.

Skills win **70–86% of head-to-head comparisons** depending on measurement context. In a clean SDK deployment where both conditions produce artifact-free responses (Strands SDK, v9), skills win **85.9%** (Cohen's d = 0.97, large effect). In an agentic harness with symmetric tool access (kiro-cli, v3), skills win **69.5%** (d = 0.39, small-medium). The gap is explained by response artifacts from tool interleaving in the agentic harness, not by skill quality differences. Critical thinking — the least-confounded dimension — improves **77–85%** of the time regardless of harness.

The strongest effect across all versions is on critical thinking (77–85% win rate, d = 0.65–1.03), confirming that skills' primary value is teaching the agent *how to think* about domain problems. We find a strong negative correlation (r = -0.54 to -0.61 across versions) between baseline response quality and skill benefit — the most robust finding, replicating across all three harness configurations. Skills reduce response variance by up to 62%. Per-skill rankings are uncorrelated between versions (r ≈ 0), indicating that n=10 per skill is insufficient for individual skill attribution despite the overall effect being definitive (p < 10⁻¹²).

## 1. Introduction

Large language models demonstrate broad competence across scientific domains but exhibit inconsistent performance on specialized tasks requiring precise methodology, tool-specific parameters, or domain-specific decision frameworks. In healthcare and life sciences, errors in variant classification criteria, study design choices, or clinical data standards can have downstream consequences for research validity and patient safety.

Agent skills — structured knowledge documents loaded into an AI assistant's context — represent one approach to injecting domain expertise without model fine-tuning. Skills encode two types of knowledge: (1) **reasoning skills** that teach methodology, decision frameworks, and common pitfalls; and (2) **pipeline skills** that encode tool-specific commands, parameters, and code patterns.

This study evaluates 38 HCLS skills across 12 domains across 3 evaluation versions to determine: (a) whether skills measurably improve response quality, (b) which dimensions of quality benefit most, (c) under what conditions skills provide the greatest value, (d) whether reasoning skills and pipeline skills differ in their impact, and (e) how measurement harness choice affects observed effect sizes.

## 2. Methodology

### 2.1 Skill Corpus

The evaluation covers 38 skills organized into 12 domains:

| Domain | Skills | Type Split |
|---|---|---|
| Genomics | 4 | 1 reasoning, 3 pipeline |
| Single-Cell Analysis | 4 | 1 reasoning, 3 pipeline |
| Medical Imaging | 4 | 1 reasoning, 3 pipeline |
| Protein Structure | 3 | 1 reasoning, 2 pipeline |
| Cross-Domain | 3 | 3 reasoning |
| Pharmacoepidemiology | 2 | 1 reasoning, 1 pipeline |
| Clinical Data | 2 | 1 reasoning, 1 pipeline |
| Drug Discovery | 2 | 1 reasoning, 1 pipeline |
| Proteomics | 2 | 1 reasoning, 1 pipeline |
| Clinical Data Review | 2 | 1 reasoning, 1 pipeline |
| Multi-Omics | 2 | 1 reasoning, 1 pipeline |
| Healthcare Operations | 8 | 4 reasoning, 4 pipeline |

Total: 17 reasoning skills, 21 pipeline skills.

### 2.2 Test Prompt Generation

410 test prompts were generated using Claude Sonnet 4.6 (`us.anthropic.claude-sonnet-4-6`) via Amazon Bedrock:
- 380 single-skill prompts (10 per skill, varying difficulty: 3 easy, 4 intermediate, 3 hard)
- 30 cross-skill prompts (10 per combination for 3 multi-skill scenarios)

Each prompt is self-contained, providing sufficient context for a complete response without clarification. Prompts include realistic fictional data (patient counts, gene names, specific parameters) and request multiple concrete deliverables.

### 2.3 Response Generation

Three agent harness configurations were used:

**v3 — kiro-cli agent (Sonnet 4.5)**
The Kiro CLI agent tool invokes the underlying model through `kiro-cli chat --no-interactive`. Skills are loaded via `--agent hcls-eval` which registers all 38 SKILL.md files as readable resources. The agent has access to a `thinking` tool and file-read operations. Both baseline and skills conditions run from the same project directory, producing symmetric tool-call noise in both conditions' output.

**v8 — kiro-cli agent (Sonnet 4.6)**
Same kiro-cli harness as v3 but pinned to Sonnet 4.6. The baseline condition's environment was isolated by overriding `KIRO_HOME` to an empty directory, stripping all context. The skills condition retained the full project environment. This created an asymmetric setup documented in §4.2.

**v9 — Strands SDK agent (Sonnet 4.6)**
The AWS Strands Agents SDK creates a lightweight Python agent via `Agent(model=BedrockModel(...), callback_handler=None)`. The skills condition additionally loads an `AgentSkills(skills="./skills/")` plugin. Both conditions capture only the final assistant text via `str(result)`, producing artifact-free output.

In all versions, two conditions are compared:
- **Baseline:** Agent invoked without skill content available
- **Skills:** Agent invoked with all 38 skills available via progressive loading

The independent variable is skill content availability.

### 2.4 Judging Protocol

We employ pairwise comparison with the following design:

- **Judge model:** Claude Opus 4.7 (`us.anthropic.claude-opus-4-7`) via Amazon Bedrock
- **Presentation:** Both responses shown in a single judge call as "Response A" and "Response B"
- **Position randomization:** 50% probability that baseline is presented as A (and skills as B), or vice versa. This controls for position bias.
- **Sanitization:** Tool-call artifacts (file reads, thinking logs, skill paths) are stripped from both responses before judging. The judge cannot identify which condition produced which response.
- **Scoring:** Five dimensions, each 0-100, plus a forced winner declaration (A, B, or tie)

**Skill activation tracking:** Skill activation is tracked via response text markers and classified into activation patterns: clean (only intended skill loaded), same-domain extra (intended + related skill from same domain), cross-domain extra (unrelated skill also loaded), only unintended (wrong skill loaded), and none (no skill loaded). Precision is computed as |target∩loaded|/|loaded| and recall as |target∩loaded|/|target|, where target is the prompt-level ground truth label and loaded is the set of skills detected in the response.

### 2.5 Scoring Dimensions and Metrics

| Dimension | Definition |
|---|---|
| Scientific Accuracy | Correctness of facts, mechanisms, citations, domain knowledge |
| Coherence | Logical structure, clear reasoning chain, internal consistency |
| Relevance | Addresses all parts of the prompt, appropriate depth, stays on topic |
| Critical Thinking | Challenges assumptions, identifies limitations, considers alternatives |
| Actionability | Provides concrete next steps, specific parameters, runnable commands |

**Note on metrics:** The judge scores each response on a 0-100 scale per dimension. However, LLM judges exhibit score compression — scores cluster in the 78-96 range, making raw deltas (e.g., +1.5) difficult to interpret. We therefore report two primary metrics:

- **Win rate:** Percentage of prompts where the skills condition scored higher than baseline. Intuitive and robust to scale compression.
- **Cohen's d:** Effect size (mean delta / pooled standard deviation). Measures how large the improvement is relative to natural variance. Benchmarks: 0.2 = small, 0.5 = medium, 0.8 = large.

Raw deltas are reported as a secondary reference.

### 2.6 Statistical Analysis

- Per-skill win rates and Cohen's d computed from paired observations (same prompt, both conditions)
- Correlation between baseline strength and skill benefit assessed via Pearson r
- Skill activation detected by parsing response text for explicit skill file reads
- Position bias assessed via chi-square test on winner declaration by position

## 3. Results

### 3.1 Overall Effect Across Versions

| Metric | v3 (kiro-cli) | v8 (kiro-cli) | v9 (Strands) |
|---|---|---|---|
| Prompts evaluated | 410 | 410 | 410 |
| Skills win rate | **69.5%** | 64.6% | **85.9%** |
| Cohen's d (overall) | 0.39 | 0.20 | **0.97** |
| Critical thinking win rate | **78.0%** | 76.6% | 85.1% |
| Reasoning skills win rate | 75.6% | 61.3% | 86.2% |
| Pipeline skills win rate | 66.5% | 69.0% | 89.4% |
| Baseline-benefit correlation (r) | -0.59 | -0.54 | -0.61 |
| Max variance reduction | -61.9% | -54.3% | -52.1% |

Two clusters emerge: v9 (Strands SDK) achieves ~86% win rate while kiro-cli versions cluster at 65–70%. The following subsections explain why.

### 3.2 Per-Dimension Results

| Dimension | v3 WR (d) | v8 WR (d) | v9 WR (d) |
|---|---|---|---|
| Critical Thinking | **78.0%** (0.65) | **76.6%** (0.49) | 85.1% (1.03) |
| Scientific Accuracy | 69.3% (0.34) | 65.9% (0.16) | **87.7%** (0.85) |
| Actionability | 68.0% (0.37) | 62.6% (0.17) | 77.3% (0.56) |
| Relevance | 55.6% (0.32) | 63.0% (0.16) | 78.3% (0.43) |
| Coherence | 54.9% (-0.08) | 48.5% (-0.03) | **92.8%** (1.09) |

Critical thinking is the most stable signal across harnesses (76.6–85.1%, 8.5pp range). Coherence is the most harness-dependent (48.5–92.8%, 44pp range) — see §4.2 for explanation.

### 3.3 Skill Activation

Skill activation is classified into patterns based on which skills were loaded relative to the prompt's ground-truth target skill(s):

- **Only intended skill(s):** The agent loaded exactly the skill(s) designated for that prompt — no extras.
- **Intended + same-domain extra:** The intended skill was loaded, plus additional skill(s) from the same domain (e.g., a `variant-calling` prompt also loaded `genomic-variant-interpretation` — both genomics).
- **Intended + cross-domain extra:** The intended skill was loaded, plus skill(s) from a different domain (e.g., a genomics prompt also loaded a clinical-data skill).
- **Only unintended skill(s):** A skill was loaded, but not the one targeted by the prompt.
- **No skill loaded:** The agent did not load any skill.

**Activation metrics:**

| Metric | v3 | v8 | v9 |
|---|---|---|---|
| Precision (target∩loaded / loaded) | 62.3% | 76.9% | 82.9% |
| Recall (target∩loaded / target) | 84.5% | 89.8% | 93.8% |
| Unintended rate (loaded−target / loaded) | 37.7% | 23.1% | 17.1% |

**Win rate by activation pattern:**

| Pattern | v3 Count (WR) | v8 Count (WR) | v9 Count (WR) |
|---|---|---|---|
| Only intended skill(s) | 127 (70.9%) | 263 (64.6%) | 320 (86.6%) |
| Intended + same-domain extra | 129 (75.2%) | 79 (72.2%) | 49 (87.8%) |
| Intended + cross-domain extra | 81 (69.1%) | 26 (50.0%) | 12 (91.7%) |
| Only unintended skill(s) | 0 (—) | 9 (44.4%) | 27 (74.1%) |
| No skill loaded | 73 (57.5%) | 33 (63.6%) | 2 (50.0%) |

Key observations:
- **Clean activation win rates match overall win rates** in each version (v3: 70.9% vs 69.5% overall; v9: 86.6% vs 85.9% overall), confirming the benefit comes from targeted skill activation, not bulk context injection.
- **Same-domain extra loading does not hurt** — win rates are equal to or higher than clean activation, suggesting related skills provide complementary value.
- **Cross-domain extra loading shows version-dependent effects** — neutral in v3 (69.1%), harmful in v8 (50.0%), but neutral/positive in v9 (91.7%). The v8 result may reflect the asymmetric contamination issue rather than genuine cross-domain harm.
- **Precision improves across versions** (62% → 77% → 83%), reflecting better skill selection mechanics in newer harnesses.

### 3.4 Effect by Skill Type

| Type | v3 Win Rate | v8 Win Rate | v9 Win Rate |
|---|---|---|---|
| Reasoning (n=160) | **76%** | 61% | 86% |
| Pipeline (n=200) | 67% | **69%** | **89%** |

The reasoning > pipeline advantage observed in v3 (+9pp) does not replicate stably: v8 reverses it (-8pp) and v9 shows pipeline slightly ahead (-3pp). Per-skill correlation between versions is near-zero (v3 vs v9: r = -0.004), confirming this is sampling noise at n=10 per skill, not a real skill-type effect. The critical thinking advantage for reasoning skills (d = 0.69 vs 0.56 in v3) persists but is insufficient to generalize a stable type-level conclusion from these data.

### 3.6 Effect by Baseline Strength

**v3 (kiro-cli, auto model)**

| Baseline Tier | N | Baseline (m±s) | Skills (m±s) | Delta | Win Rate |
|---|---|---|---|---|---|
| Weak (<80) | 15 | 75.8±4.0 | 84.4±6.3 | +8.7 | **87%** |
| Medium (80-90) | 246 | 87.1±2.5 | 89.3±3.3 | +2.2 | 79% |
| Strong (>90) | 149 | 91.5±0.9 | 91.0±2.5 | -0.5 | 54% |

**v8 (kiro-cli, Sonnet 4.6)**

| Baseline Tier | N | Baseline (m±s) | Skills (m±s) | Delta | Win Rate |
|---|---|---|---|---|---|
| Weak (<80) | 23 | 77.0±2.4 | 84.5±3.3 | +7.5 | **96%** |
| Medium (80-90) | 275 | 86.6±2.6 | 88.4±4.5 | +1.8 | 73% |
| Strong (>90) | 112 | 91.2±0.8 | 89.0±4.2 | -2.2 | 33% |

**v9 (Strands SDK, Sonnet 4.6)**

| Baseline Tier | N | Baseline (m±s) | Skills (m±s) | Delta | Win Rate |
|---|---|---|---|---|---|
| Weak (<80) | 46 | 77.0±2.6 | 84.9±3.5 | +7.9 | **96%** |
| Medium (80-90) | 325 | 85.8±2.6 | 89.5±3.3 | +3.7 | 89% |
| Strong (>90) | 39 | 91.0±0.7 | 91.1±2.0 | +0.0 | 54% |

Pearson correlation between baseline score and delta: v3: **r = -0.59**, v8: **r = -0.54**, v9: **r = -0.61** (all p < 0.001). This is the most robust finding in the evaluation — it replicates across harnesses, models, and judging sessions.

## 4. Multi-Version Analysis

Following the initial v3 evaluation, we conducted additional evaluation versions to test robustness across backends, models, and baseline conditions. The results reveal that measurement harness choice significantly affects observed win rates, while the underlying skill benefit remains stable when measured on unconfounded dimensions.

### 4.1 Version Matrix

| Version | Backend | Model | Baseline Tools | Win Rate | Cohen's d |
|---------|---------|-------|----------------|----------|-----------|
| v3 | kiro-cli | auto (Sonnet 4.5) | thinking, file reads | 69.5% | 0.39 |
| v8 | kiro-cli | Sonnet 4.6 | thinking, file reads (KIRO_HOME isolated) | 64.6% | 0.20 |
| v9 | Strands SDK | Sonnet 4.6 | think tool | 85.9% | 0.97 |

Note on v3 tools: MCP servers were configured in the project directory but no MCP tool calls were observed in evaluated responses — prompts are self-contained HCLS questions that do not require coding tools.

### 4.2 The Harness Effects Discovery

The 20-percentage-point gap between kiro-cli and Strands results traces primarily to a single dimension: **coherence**.

Between v8 (kiro-cli, 64.6%) and v9 (Strands, 85.9%), the coherence win rate differs by **43.9 percentage points**:

| Version | Coherence Win Rate | Overall Win Rate |
|---------|-------------------|-----------------|
| v8 (kiro-cli) | 48.5% | 64.6% |
| v9 (Strands) | 92.4% | 85.9% |
| **Gap** | **43.9pp** | **21.3pp** |

The root cause is **asymmetric artifact contamination**. In v8:
- **Skills condition:** 91% of responses contain file-read artifacts (`Reading file:`, `Successfully read N bytes`); 34% contain thinking traces
- **Baseline condition:** 0% artifacts due to `KIRO_HOME` isolation that stripped all MCP servers, steering files, and global context

The baseline was made artificially clean while the skills condition retained its full (noisy) environment. The judge penalizes skills for incoherence that reflects tool-interleaving artifacts, not skill content quality.

**Why v3 was fair despite being "messy":** Both conditions ran in the same project directory with the same tools. Thinking tool output appeared in 100% of baseline responses too. Symmetric noise cancels in pairwise comparison — coherence was near-neutral (54.9% skills win rate), and the 69.5% overall win rate reflects genuine content differences.

**Why Strands is cleanest:** `str(result)` captures only the final assistant text. Tool calls — including the `skills` tool invocation — are invisible in captured output. Both conditions produce clean, artifact-free prose. The coherence comparison is unconfounded.

### 4.4 Critical Thinking: The Least-Confounded Dimension

Across all harness configurations, critical thinking shows the smallest gap between kiro-cli and Strands measurements:

| Dimension | v3 (kiro-cli) | v8 (kiro-cli) | v9 (Strands) | Max Gap |
|-----------|--------------|--------------|--------------|---------|
| Coherence | 54.9% | 48.5% | 92.4% | 43.9pp |
| Overall | 69.5% | 64.6% | 85.9% | 21.3pp |
| Critical Thinking | 78.0% | 76.6% | 85.1% | **8.5pp** |

Critical thinking is minimally affected by formatting artifacts because it measures whether the agent:
- Applies the correct analytical framework
- Flags appropriate limitations and caveats
- Uses domain-specific thresholds rather than generic ones
- Challenges assumptions when warranted

These qualities are present or absent regardless of whether `Reading file:` noise appears in the output. This makes critical thinking the **most reliable signal** for skill value across measurement contexts: skills improve reasoning quality **77–85%** of the time regardless of harness.

### 4.5 Per-Skill Rankings: Unstable at n=10

Per-skill win rates are **uncorrelated between versions**:

| Correlation | Pearson r |
|-------------|-----------|
| v3 vs v8 | 0.212 |
| v3 vs v9 | -0.004 |
| v8 vs v9 | 0.011 |

A skill winning 90% in v3 has no predictive power for its win rate in v8 or v9. This is expected at n=10 per skill: the 95% binomial confidence interval is ±28%, meaning a "true 80%" skill can measure anywhere from 50% to 100% on any given run.

This does NOT mean skill quality varies randomly — it means **n=10 is insufficient to rank individual skills reliably**. The overall win rate (aggregated across 410 prompts) is highly significant (v9: p < 10⁻³⁰; v3: p < 10⁻¹²). Individual per-skill tables in the appendix should be interpreted as illustrative, not as reliable rankings.

### 4.6 Judge Behavior Analysis (v9)

Qualitative analysis of v9 judge rationales reveals how skills produce wins:

| Reason | Frequency | Description |
|--------|-----------|-------------|
| Factual corrections | 59% | Skills correct specific errors in baseline responses |
| Specificity | 33% | Skills provide calibrated thresholds absent from parametric knowledge |
| Critical thinking | 29% | Skills flag edge cases, limitations, and caveats baseline misses |

When the baseline wins (14.1% of comparisons), the primary causes are: skill steering to the wrong framework for the query (36% of baseline wins) and baseline producing a more direct response (27%).

## 5. Comparison with External Benchmarks

### 5.1 SkillsBench Alignment

The SkillsBench evaluation (arXiv 2602.12670) provides independent validation using a fundamentally different methodology:

| Aspect | This Study | SkillsBench |
|--------|-----------|------------|
| Evaluation method | LLM-as-judge (pairwise) | Deterministic verifiers |
| Task count | 410 prompts | 87 tasks |
| Domain | HCLS-specific (38 skills) | General-purpose |
| Skill implementation | Agent Skills standard (SKILL.md) | Platform-native |
| Key finding | +16–36pp improvement | **+16.6pp** with full tools |

SkillsBench reports a +16.6 percentage point improvement when both conditions have equal tool access — closely matching our v3 methodology (69.5% vs 50% chance = +19.5pp) where both conditions have symmetric environment access.

### 5.2 Methodological Convergence

Key methodological principles align across evaluations:

1. **Symmetric tool access** — both SkillsBench and our v3/v9 ensure conditions differ only in skill content
2. **Model pinning** — SkillsBench fixes the model per configuration; our v9 pins to Sonnet 4.6
3. **Clean output capture** — SkillsBench uses deterministic verifiers; our Strands versions capture only final text

The convergence across independent frameworks (different prompts, different judges, different skill implementations) strengthens confidence that the effect is real and robust rather than an artifact of any single evaluation methodology.

## 6. Discussion

### 6.1 Baseline Quality Moderates Skill Benefit

The negative correlation between baseline quality and skill benefit is consistent across all three versions (r = -0.54 to -0.61). Skills provide the greatest lift when the base model produces weaker responses (87% win rate for baseline <80) with diminishing returns as quality increases (55% win rate for baseline >90). However, this is not absolute — cross-domain skills achieve an 80% win rate even with a strong baseline (90.2), demonstrating that well-designed reasoning frameworks add value across the quality spectrum. The relationship is one of diminishing returns, not a binary threshold.

### 6.2 Methodology Over Facts

The d = 0.65 effect on critical thinking versus d = 0.34 on scientific accuracy (v3) reveals that skills' primary contribution is methodological, not factual. The base model already possesses substantial HCLS knowledge from training. What it lacks is the consistent application of domain-specific decision frameworks — when to challenge a user's premise, which pitfalls to flag, how to structure a validation plan. This finding replicates in v9, where critical thinking shows the largest effect size (d = 1.03) among non-coherence dimensions.

### 6.3 The Coherence Trade-off

In v3, the coherence regression is negligible (d = -0.08, 55% win rate). However, the multi-version analysis reveals this dimension is **extremely sensitive to measurement methodology**. The 43.9pp coherence gap between v8 and v9 is entirely attributable to response artifacts, not skill content. When measured cleanly (Strands), skills actually *improve* coherence (92.4% win rate in v9). The true coherence impact of skill content is neutral-to-positive; observed regression in agentic harnesses reflects tool noise, not skill quality.

### 6.4 Variance Reduction

An underappreciated benefit of skills is variance reduction. Across versions, the skills condition shows lower standard deviation than baseline, with reductions of 52–62% depending on version and domain (e.g., clinical-data: 6.8→3.3 in v3). This means skills make responses more predictably good — reducing the probability of a catastrophically wrong answer even when the average improvement is modest.

### 6.5 Reasoning vs Pipeline: Not a Stable Predictor

The v3 finding that reasoning skills outperform pipeline skills (+9pp) does not replicate. v8 reverses the direction (-8pp) and v9 shows near-parity (-3pp). Cross-version per-skill correlation is effectively zero (r = -0.004 to 0.212). Recent literature offers context:

- **MASA (arXiv 2605.30723)** finds the optimal skill form is model-dependent: the same skill can help one model and hurt another.
- **SkillsBench domain breakdown** shows the biggest gains come from "specialized procedural knowledge underrepresented in training" (Healthcare: +51.9pp) versus domains with strong pretraining coverage (Software Engineering: +4.5pp).

This suggests the real axis of skill effectiveness is not reasoning vs pipeline but rather **"novel to the model" vs "already in training data"** — which is consistent with our baseline-strength correlation (r = -0.54 to -0.61) being the most stable finding.

### 6.6 Activation Reliability

Skill activation is tracked via response text markers and classified into activation patterns (clean, same-domain extra, cross-domain extra, misfire, none). Precision and recall are computed against prompt-level ground truth labels. In v3, 82% of prompts triggered skill activation. Skills with low activation rates (scrna-seq-pipeline: 20%, trajectory-analysis: 30%) likely have trigger descriptions that don't match the natural language patterns in the test prompts. Improving skill descriptions and trigger phrases is a high-leverage optimization.

### 6.7 Domain-Specific Observations

Domains where skills provide the most value share a common characteristic: they require precise, non-obvious knowledge that is underrepresented in general training data. Clinical data standards (d = 0.52), multi-omics integration (d = 0.48), and pharmacoepidemiology (d = 0.44) are all areas where the base model produces plausible but imprecise responses. Skills inject the exact decision criteria needed.

Conversely, domains where skills provide no benefit (proteomics d = -0.01, clinical-data-review d = -0.05) involve well-documented standards that are adequately represented in training data. For these domains, the skill content may need to focus on edge cases and common misapplications rather than standard procedures.

### 6.8 Limitations

- **Single model family:** Results are specific to Claude Sonnet models. Different base models may show different skill sensitivity.
- **LLM-as-judge bias:** Despite sanitization and position randomization, the judge (Opus 4.7) may have systematic preferences that correlate with skill-loaded response patterns. Position bias is not significant (p = 0.096) but exists (+7.4pp).
- **Prompt generation bias:** Test prompts were generated by an LLM from skill descriptions, which may favor skill-loaded responses by design.
- **No human validation:** All scoring is automated. Human expert evaluation on a subset would strengthen confidence.
- **Per-skill power:** At n=10 per skill, individual skill win rates have ±28% confidence intervals. Per-skill conclusions require n≥30. The overall finding (N=410) is highly powered.
- **Harness confounding:** The 20pp gap between backends demonstrates that infrastructure choices materially affect observed results. Any single version's win rate should be interpreted in context of its measurement methodology.

## 7. Conclusions

### 7.1 Primary Finding

Domain-specific skills provide a measurable, consistent improvement to AI assistant responses for HCLS questions. The true effect lies in a bracket:

- **Clean SDK deployment (Strands, v9):** 85.9% win rate, Cohen's d = 0.97 (large effect). Measures skill content value with minimal confounding. Appropriate for Strands SDK, AWS Bedrock AgentCore, or deployments where tool calls are invisible in output.
- **Agentic harness with symmetric tools (kiro-cli, v3):** 69.5% win rate, Cohen's d = 0.39 (small-medium). Measures skill value in a realistic agent environment with symmetric noise. Both conditions equally affected by tool artifacts.
- **Anchor dimension (all versions):** Critical thinking at 77–85% win rate. The least-confounded signal and strongest evidence that skills improve reasoning regardless of presentation artifacts.

### 7.2 Key Takeaways

1. **Skills improve reasoning quality 77–85% of the time** regardless of measurement harness (v3: 78.0%, v8: 76.6%, v9: 85.1%)
2. **The improvement is concentrated in methodology, not facts** — critical thinking (d = 0.65–1.03) > scientific accuracy (d = 0.34–0.85) across versions
3. **The benefit is most pronounced when baseline quality is lowest** (r = -0.54 to -0.61 across all versions) — the most robust finding, replicating perfectly
4. **Skills reduce response variance by up to 62%**, making outputs more predictably reliable
5. **Per-skill rankings are noise at n=10** — zero correlation between versions means individual skill "improvements" or "regressions" cannot be interpreted. Need n≥30 for per-skill conclusions
6. **Measurement methodology matters enormously** — asymmetric artifact contamination can swing observed win rates by 20+ percentage points
7. **Reasoning vs pipeline is not a stable predictor** — the advantage direction reverses between versions; the real axis is "novel to the model" vs "already in training data"

### 7.3 Interpreting v8

The v8 result (64.6%) underestimates skill value due to documented asymmetric isolation. It should not be cited as the primary finding. The methodology is fixable: running both conditions from the same directory with the same environment (as v3 did) eliminates the asymmetry.

### 7.4 Recommendations

For **evaluation designers:**
- Ensure symmetric environment access between conditions (the only variable should be skill content)
- Use `str(result)` or equivalent to capture only final text, not tool interleaving
- Report both win rate and Cohen's d; report the bracket, not a single number
- Pin model versions explicitly

For **skill authors:**
- Target domains where the base model is weakest (r = -0.54 to -0.61 correlation) — niche regulatory and methodological knowledge over well-documented standards
- Include 15+ trigger keywords for reliable activation
- Add output format sections to prevent coherence regression
- Focus on what the model gets wrong without help, regardless of whether the skill is "reasoning" or "pipeline"

For **deployers:**
- Strands SDK with `AgentSkills` plugin provides cleanest integration
- Skills provide most value for niche regulatory and methodological domains

## Appendix A: Per-Skill Detailed Breakdown

See `eval/results/report_v3.md` § "Per-Skill Detailed Breakdown" for individual skill tables with win rate and Cohen's d across all 5 dimensions.

## Appendix B: Judging Methodology

### Pairwise Protocol (v3)

Both responses are sent in a single Claude Opus 4.7 call:
- Labeled as "Response A" and "Response B"
- Position randomized (50/50) per prompt to control for position bias
- Tool-call artifacts stripped from both responses (sanitized)
- Judge scores both responses on 5 dimensions (0-100) and declares a winner
- Win rate and Cohen's d derived from the paired 0-100 scores

### Sanitization Rules

The following patterns are removed before judging:
- Tool usage headers (`using tool: thinking`, `Batch fs_read operation`)
- File read operations (`Reading file:`, `Successfully read`)
- Skill file paths (`.kiro/skills/*/SKILL.md`)
- Completion timestamps (`Completed in 0.0s`)
- Summary lines (`operations processed, N successful`)
- Tool status markers (`✓`, `✗`, `↱`, `►`, `▶`, `⋮`)
- Preambles (`I'll share my reasoning process`)

### Comparison with Alternative Methods

| Method | Win Rate | Cohen's d | Notes |
|---|---|---|---|
| v3: Pairwise, sanitized + randomized | 69.5% | 0.39 | Symmetric tools, fair |
| v8: Pairwise, asymmetric isolation | 64.6% | 0.20 | Baseline artificially clean |
| v9: Pairwise, clean SDK | 85.9% | 0.97 | Artifact-free, cleanest |

All methods show a positive skill effect, confirming the benefit is robust to judging methodology.

## Appendix C: Harness Effects Detail

For the full analysis of harness effects including artifact frequency tables, per-dimension breakdowns across versions, and the asymmetric isolation diagnosis, see [`eval/HARNESS_EFFECTS.md`](./HARNESS_EFFECTS.md).

## Appendix D: Per-Domain Breakdown

| Domain | N | v3 WR (d) | v8 WR (d) | v9 WR (d) |
|---|---|---|---|---|
| Clinical Data | 20 | 75% (0.52) | 45% (-0.14) | 85% (1.32) |
| Clinical Data Review | 20 | 50% (-0.05) | 60% (0.53) | 85% (1.42) |
| Cross-Domain | 30 | 80% (0.38) | 57% (0.18) | 83% (0.83) |
| Drug Discovery | 30 | 77% (0.35) | 50% (-0.24) | 90% (0.94) |
| Genomics | 50 | 72% (0.41) | 74% (0.85) | 86% (1.29) |
| Healthcare Ops | 80 | 71% (0.32) | 64% (0.41) | 84% (0.98) |
| Imaging | 40 | 75% (0.43) | 53% (-0.03) | 98% (1.86) |
| Multi-Omics | 20 | 70% (0.48) | 75% (0.55) | 80% (0.99) |
| Pharmacoepidemiology | 30 | 67% (0.44) | 65% (0.52) | 83% (0.86) |
| Protein Structure | 30 | 67% (0.18) | 58% (0.35) | 93% (1.72) |
| Proteomics | 20 | 50% (-0.01) | 60% (0.07) | 75% (0.58) |
| Single-Cell | 40 | 65% (0.16) | 73% (0.55) | 90% (2.07) |

Note: per-domain rankings at n=10–20 per domain are subject to the same statistical instability as per-skill rankings (§4.5).
