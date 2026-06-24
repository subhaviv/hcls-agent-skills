# Evaluation Analysis: Do Domain Skills Improve Agent Responses?

A technical analysis of 8 evaluation versions (v1–v5, v7–v9) measuring whether curated domain skills improve AI agent responses for healthcare and life sciences (HCLS) questions.

## Evaluation Design

The evaluation uses a pairwise comparison methodology across 410 prompts: 380 targeting individual skills and 30 testing cross-skill activation. The prompt set spans 38 skills across 11 HCLS domains (genomics, single-cell analysis, medical imaging, protein structure, pharmacoepidemiology, clinical data, drug discovery, proteomics, clinical data review, multi-omics integration, and healthcare operations).

Each prompt is answered twice — once with skills loaded (treatment) and once without (baseline) — under otherwise identical conditions. A judge model (Claude Opus 4.7) performs pairwise comparison on five dimensions: scientific accuracy, coherence, relevance, critical thinking, and actionability. Response position is randomized to control for order effects, and both responses are sanitized to remove tool-call artifacts before judging.

The independent variable across conditions is skill content availability. Everything else — model, tools, environment — should be held constant. As documented below, violations of this symmetry explain most cross-version variance.

## Version Matrix

| Version | Backend | Model | Baseline Tools | Win Rate | Cohen's d |
|---------|---------|-------|----------------|----------|-----------|
| v3 | kiro-cli | auto | thinking, file reads, MCP | 69.5% | 0.39 |
| v5-strands | Strands SDK | Sonnet 4.5 | None | 88.5% | — |
| v7-strands-think | Strands SDK | Sonnet 4.5 | think tool | 88.0% | — |
| v8-kiro-sonnet46 | kiro-cli | Sonnet 4.6 | thinking, file reads (KIRO_HOME isolated) | 64.6% | 0.20 |
| v9-strands-think-sonnet46 | Strands SDK | Sonnet 4.6 | think tool | 85.9% | 0.97 |

Two clusters emerge: Strands SDK versions converge around 86–88% win rate, while kiro-cli versions cluster at 65–70%. The following sections explain why.

## The Coherence Gap: Why Harnesses Diverge

The 20-percentage-point gap between kiro-cli and Strands results traces primarily to a single dimension: coherence.

Between v8 (kiro-cli, 64.6%) and v9 (Strands, 85.9%), the coherence win rate differs by 43.9 percentage points. In v8, 91% of skills-condition responses contain file-read artifacts (`Reading file:`, `Successfully read N bytes`) and 34% contain thinking traces — visible structural noise that degrades perceived coherence. The v8 baseline, by contrast, has 0% artifacts due to `KIRO_HOME` isolation that stripped it of all MCP servers, steering files, and global context.

This asymmetry is the root cause. The baseline was made artificially clean while the skills condition retained its full (noisy) environment. The judge penalizes the skills condition for incoherence that has nothing to do with skill content — it reflects tool-interleaving artifacts in the captured output.

Version 3 avoided this problem through symmetric contamination: both conditions ran in the same project directory with the same MCP servers. Thinking tool output appeared in 100% of baseline responses too. Result: coherence was near-neutral (54.9% skills win rate on that dimension), and the overall win rate (69.5%) reflects genuine content differences rather than formatting asymmetry.

In Strands SDK versions, `str(result)` captures only the final assistant text. Tool calls — including the `skills` tool invocation — are invisible in the captured output. Both conditions produce clean, artifact-free prose. The coherence comparison is therefore unconfounded, and the 86% win rate reflects the actual quality difference.

## The Think Tool Has No Measurable Effect

Versions 5 and 7 form a natural experiment: identical setup except v7 adds a `think` tool to the baseline condition. Results are statistically indistinguishable:

- v5 (no think): 88.5% win rate
- v7 (think): 88.0% win rate
- Baseline mean scores identical: 84.7 in both versions

The think tool is confirmed to be invoked (5/5 spot-checked responses show tool calls), but because `callback_handler=None` suppresses streaming output, thinking content never reaches the captured response. The judge sees only final text, which is unaffected.

Despite producing non-identical responses (mean text similarity of 23% between v5 and v7 baseline outputs), the quality scores are the same. This establishes that the model reaches equivalent quality through different reasoning paths — a form of convergent quality regardless of whether internal deliberation is explicit or implicit.

These two versions also serve as a reproducibility test for the judge: 80% agreement on pairwise verdicts, with symmetric flips (39 reversals in each direction). This indicates stable judging without systematic drift.

## Strands AgentSkills: Progressive Loading, Clean Output

The Strands SDK's `AgentSkills` plugin uses a progressive loading mechanism. The system prompt receives only a lightweight XML catalog (~3–4KB) listing available skills with trigger keywords. When the model determines a skill is relevant, it calls the `skills` tool to load the full SKILL.md content into its context.

This is architecturally analogous to kiro-cli's file-read mechanism for skill loading, but with a critical difference for evaluation: `str(result)` on the Strands agent captures only the final assistant message. Tool invocations, skill content, and intermediate reasoning are excluded from the captured output. Both conditions therefore produce clean text, enabling a fair pairwise comparison on content quality alone.

## Model-Specific Skill Activation in Kiro-CLI

An important discovery: Sonnet 4.5 in kiro-cli does not proactively read skills. The model receives skill summaries in its context window but does not invoke the `read` tool to load full SKILL.md content. Sonnet 4.6 and the `auto` model selector do read skills reliably.

The root cause is that Sonnet 4.5 was not trained with awareness of the Agent Skills specification. It treats skill summaries as informational context rather than as pointers to loadable resources. The `--agent-engine v1` flag partially mitigates this but does not fully resolve it for Sonnet 4.5.

This finding is relevant for deployment: organizations using kiro-cli should verify their model actively loads skills, not merely receives summaries.

## Asymmetric Isolation in v8

Version 8 attempted to create a clean baseline by overriding `KIRO_HOME` to an empty directory. This successfully stripped the baseline of MCP servers, steering files, and all global context — producing artifact-free responses. However, the skills condition retained the full environment (MCP + steering + skills), introducing tool artifacts visible in captured output.

The result is an unfair coherence advantage for the baseline. The 64.6% win rate underestimates skill value because it conflates content quality with presentation cleanliness. Version 3's methodology — where both conditions share the same environment and tool access — produces a fairer measurement despite being "messier" in absolute terms. Symmetric noise cancels in pairwise comparison; asymmetric noise does not.

## Judge Behavior Analysis (v9)

Qualitative analysis of v9 judge rationales reveals the mechanisms by which skills produce wins:

| Reason | Frequency | Description |
|--------|-----------|-------------|
| Factual corrections | 59% | Skills correct specific errors in baseline responses |
| Specificity | 33% | Skills provide calibrated thresholds absent from parametric knowledge |
| Critical thinking | 29% | Skills flag edge cases, limitations, and caveats baseline misses |

When the baseline wins (14.1% of comparisons), the primary causes are: skill steering to the wrong framework for the query (36% of baseline wins) and baseline producing a more directly relevant response (27%).

Position bias is +7.4 percentage points (favoring the second-presented response) but not statistically significant (p = 0.096). No formulaic judging patterns were detected — rationales are specific to the content of each comparison pair.

## Critical Thinking: The Least-Confounded Dimension

Across all harness configurations, critical thinking shows the smallest gap between kiro-cli and Strands measurements:

- v8 (kiro-cli): 76.6% skills win rate
- v9 (Strands): 84.9% skills win rate
- Gap: 8.3 percentage points

Compare this to coherence (43.9pp gap) or overall win rate (21.3pp gap). Critical thinking is minimally affected by formatting artifacts because it measures whether the agent applies the correct framework, flags appropriate limitations, uses domain-specific thresholds, and challenges assumptions. These qualities are present or absent regardless of whether `Reading file:` noise appears in the output.

This makes critical thinking the most reliable signal for skill value across measurement contexts: skills improve reasoning quality 77–85% of the time regardless of harness.

## Comparison with External Benchmarks

The SkillsBench evaluation (arXiv 2602.12670) reports a +16.6 percentage point improvement with full agentic tools when both conditions have equal tool access. Key methodological differences:

- SkillsBench uses deterministic verifiers (not LLM judges)
- SkillsBench fixes the model per configuration (paired evaluation)
- SkillsBench ensures symmetric tool access across conditions

Our v3 (69.5% with symmetric tools, kiro-cli) aligns most closely with SkillsBench's methodology: both conditions have equal environment access, and the only variable is skill content. Our v9 (85.9%, clean SDK) represents maximum measurable uplift in an artifact-free comparison — comparable to SkillsBench's harness-specific results where output capture is cleanest.

The convergence across independent evaluation frameworks (different prompts, different judges, different skill implementations) strengthens confidence that the effect is real and robust.

## Conclusions and Recommendations

### Reporting Framework

The true effect of domain skills on HCLS agent responses lies in a bracket: **70–86% win rate** depending on measurement context.

- **Primary metric for clean SDK deployments:** v9 at 85.9% (Cohen's d = 0.97). This measures skill content value with minimal confounding from harness artifacts. Appropriate for Strands SDK, AWS Bedrock AgentCore, or any deployment where tool calls are invisible in output.

- **Reference metric for agentic harnesses:** v3 at 69.5% (Cohen's d = 0.39). This measures skill value in a realistic agent environment with tools, MCP servers, and streaming output. Both conditions are equally noisy, making the comparison fair despite lower absolute numbers.

- **Anchor dimension:** Critical thinking at 77–85% win rate across all versions. This is the least-confounded signal and the strongest evidence that skills improve the agent's reasoning regardless of presentation artifacts.

### Interpreting v8

The v8 result (64.6%) underestimates skill value due to documented asymmetric isolation. It should not be cited as the primary finding. The methodology is fixable: running both conditions from the same directory with the same environment (as v3 did) eliminates the asymmetry.

### Future Work

1. **Fix v8 methodology** — run both conditions with symmetric environment access (no `KIRO_HOME` override for baseline only). Expected result: win rate closer to v3's 69.5%.
2. **Expand per-skill sample size** — current evaluation uses 10 prompts per skill. Expanding to n=30 would enable per-skill confidence intervals and identify which of the 38 skills genuinely underperform versus which show variance from small samples.
3. **Cross-model validation** — test whether skill benefits generalize to models beyond the Claude family (e.g., GPT-4, Gemini) to establish skill portability.
4. **Longitudinal tracking** — as models improve, re-evaluate to identify skills that become redundant (model learned the content) versus those that remain high-value (encoding institutional or regulatory knowledge that changes over time).

---

*Analysis based on evaluation runs conducted April–June 2026. Judge model: Claude Opus 4.7. Prompt set: 410 (380 single-skill + 30 cross-skill). Full per-skill results available in `eval/results/`.*
