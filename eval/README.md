# HCLS Skills Evaluation Suite

Automated evaluation measuring whether domain skills improve agent responses for healthcare and life sciences questions. Uses the [AWS Strands Agents SDK](https://github.com/strands-agents/sdk-python) as the default execution backend, with kiro-cli as a legacy alternative.

## Quick Start

```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -e .

# Recommended: v9 methodology (Strands + Sonnet 4.6 + think tool)
python -m eval.run --parallel 2 --version v9 --pairwise \
  --model us.anthropic.claude-sonnet-4-6-20250514-v1:0 --tools think

python eval/build_review.py
open eval/results/review.html
```

## Prerequisites

- **Python 3.12+** managed via [uv](https://docs.astral.sh/uv/)
- **AWS credentials:** configured via `~/.aws/credentials` or environment variables
- **Amazon Bedrock access:** model access enabled for:
  - `us.anthropic.claude-sonnet-4-5-20250929-v1:0` (execution, default)
  - `us.anthropic.claude-opus-4-7` (LLM judge)
- **Region:** `us-east-1` (default Bedrock region)

## Architecture

```
eval/
├── run.py                  # CLI orchestrator — execute → judge → report
├── execute.py              # Dual-backend executor (strands SDK or kiro-cli)
├── judge.py                # Independent scoring via Bedrock Opus 4.7
├── judge_pairwise.py       # Pairwise scoring (both responses in one call)
├── report.py               # Generates JSON + markdown reports
├── build_review.py         # Generates interactive HTML review
├── generate_prompts.py     # One-time prompt generation from skill metadata
├── config.yaml             # Eval configuration (judge model, timeouts)
├── prompts/                # Version-controlled test prompts (410 total)
│   ├── single/             # 380 prompts (10 per skill × 38 skills)
│   └── cross/              # 30 prompts (10 per combo × 3 combos)
├── results/                # Output (gitignored)
│   ├── responses/          # Cached agent responses
│   ├── scores_v*.json      # Scored results per version
│   ├── report_v*.md        # Markdown reports per version
│   ├── review.html         # Interactive HTML review (all versions)
│   └── METHODOLOGY.md      # Judging method comparison
├── TECHNICAL_REPORT.md     # Academic-style analysis of v3 results
└── PRESENTATION.md/.html   # Slide deck (Marp)
```

### Execution Backends

`execute.py` supports two backends:

| Backend | Default | How it works | Requirements |
|---------|---------|--------------|--------------|
| `strands` | ✅ | AWS Strands Agents SDK with `AgentSkills` plugin, calls Bedrock directly | AWS credentials + Bedrock access |
| `kiro-cli` | — | Subprocess invocation of `kiro-cli chat` | kiro-cli installed + authenticated |

The **strands** backend builds an `Agent` with a `BedrockModel` for each prompt. For the "skills" condition, it attaches an `AgentSkills` plugin pointed at the skills directory. For "baseline", it runs a bare agent with no skills. No external CLI tools are needed.

## CLI Flags

```
python -m eval.run [OPTIONS]

Execution:
  --backend {strands,kiro-cli}  Execution backend (default: strands)
  --model MODEL_ID              Bedrock model ID for execution (strands only)
                                Default: us.anthropic.claude-sonnet-4-5-20250929-v1:0
  --tools TOOL [TOOL ...]       Tools to provide to the agent (e.g., --tools think)
                                Adds specified tools to both conditions symmetrically
  --kiro-model MODEL            Model override for kiro-cli backend
                                (e.g., --kiro-model claude-sonnet-4.6)
  --skills PATH                 Path to skills directory (default: ./skills/)
  --parallel N                  Max concurrent executions (default: 1)
  --version V                   Version label (e.g., v9). Tags output files.

Judging:
  --pairwise                    Use pairwise judge (recommended, most sensitive)
  --skip-execution              Skip execution, re-judge cached responses
  --skip-judge                  Skip judging, just generate report

Paths:
  --prompts-dir PATH            Prompts directory (default: eval/prompts)
  --results-dir PATH            Results directory (default: eval/results)
  --config PATH                 Config file (default: eval/config.yaml)
```

## Cross-Skill Prompts

The eval suite includes 30 cross-skill prompts (10 per category × 3 categories) that test multi-skill activation — questions spanning multiple domains where the agent must draw on several skills simultaneously. These are **not** standalone skills (no `SKILL.md` exists for them) but evaluation-only prompt categories.

| Category | Skills Tested | Example Scenario |
|----------|--------------|------------------|
| `drug-discovery-structural` | drug-repurposing + structure-based-drug-design + molecular-docking | Repurposing a kinase inhibitor requiring docking validation |
| `pharma-rwd-clinical` | pharmacoepidemiology + rwd-cohort-analysis + clinical-data-standards | Target trial emulation with claims data and MedDRA coding |
| `genomics-variant-pipeline` | genomic-variant-interpretation + variant-calling + ngs-quality-control | ACMG classification of a variant discovered via GATK pipeline |

Cross-skill prompts live in `eval/prompts/cross/` (e.g., `drug-discovery-structural-01.yaml`). In eval reports, they appear as 3 additional entries alongside the 38 single-skill entries, bringing the total to 41 rows. They should be interpreted as "cross-skill" category results, not as standalone skill evaluations.

## Running an Evaluation

### Full run (execution + judging + report)

```bash
python -m eval.run --parallel 2 --version v9 --pairwise \
  --model us.anthropic.claude-sonnet-4-6-20250514-v1:0 --tools think
```

This will:
1. Execute all 410 prompts under both conditions (baseline = bare agent, skills = agent with AgentSkills plugin)
2. Score all 820 responses via Claude Opus 4.7 pairwise judge
3. Generate `report_v9.md` and `scores_v9.json`

### Re-judge only (skip execution, use cached responses)

```bash
python -m eval.run --skip-execution --version v9 --pairwise
```

### Custom model

```bash
python -m eval.run --model us.anthropic.claude-sonnet-4-20250514-v1:0 --version v5 --pairwise --tools think
```

### Build interactive HTML review

```bash
python eval/build_review.py
open eval/results/review.html
```

Loads all score versions (v1–v9) with a toggle. Shows per-skill tables, side-by-side responses, judge reasoning, and skill activation flags.

### Using kiro-cli backend (legacy)

```bash
./install.sh --target kiro --path .
python -m eval.run --backend kiro-cli --parallel 2 --version v8 \
  --kiro-model claude-sonnet-4.6
```

Requires kiro-cli installed and authenticated. The agent config is auto-created at `.kiro/agents/hcls-eval.json`. Use `--kiro-model` to pin the model (recommended for reproducibility).

## Regenerating Prompts

Prompts are version-controlled and don't need regeneration. To regenerate:

```bash
python eval/generate_prompts.py --force
```

Uses Claude Sonnet 4 (`us.anthropic.claude-sonnet-4-6`) via Bedrock. Generates 10 prompts per skill with varying difficulty (3 easy, 4 intermediate, 3 hard).

## Configuration

`eval/config.yaml`:

```yaml
judge:
  model: us.anthropic.claude-opus-4-7
  max_tokens: 2048
  retries: 3

execution:
  timeout_seconds: 1200
  parallel: 1
  kiro_cmd: kiro-cli
  skills_agent: hcls-eval
```

The `execution.kiro_cmd` and `execution.skills_agent` fields are only used by the `kiro-cli` backend. The strands backend reads model and skills path from CLI flags (or defaults).

## Key Design Decisions

- **Baseline isolation:** Strands baseline uses a bare `Agent()` with no plugins; kiro-cli baseline runs from a temp directory with no `.kiro/`
- **Response sanitization:** Tool-call artifacts stripped before judging so the judge can't identify which condition produced the response
- **Position randomization (v3+):** 50/50 chance which response is shown as A vs B, canceling position bias
- **Score caching:** Responses and scores cached to disk — re-runs only process missing data
- **Paired t-test:** Per-skill significance via `scipy.stats.ttest_rel` on paired observations
- **Self-contained:** The strands backend requires only AWS credentials — no CLI tools, subscriptions, or local agents

## Judging Versions

| Version | Method | Backend | Model | Notes | Win Rate |
|---|---|---|---|---|---|
| v1 | Independent, raw | kiro-cli | — | Historical baseline | — |
| v2 | Independent, sanitized | kiro-cli | — | Absolute quality scores | — |
| v3 | Pairwise, sanitized + randomized | kiro-cli | Sonnet 4.5 | First pairwise (gold standard at time) | 69.5% |
| v5-strands | Pairwise, sanitized + randomized | Strands | Sonnet 4.5 | Bare baseline (no tools) | 88.5% |
| v7-strands-think | Pairwise, sanitized + randomized | Strands | Sonnet 4.5 | Think tool added (no measurable effect) | 88.0% |
| v8-kiro-sonnet46 | Pairwise, sanitized + randomized | kiro-cli | Sonnet 4.6 | Full tools; asymmetric isolation issue | 64.6% |
| v9-strands-think-sonnet46 | Pairwise, sanitized + randomized | Strands | Sonnet 4.6 | Think tool; **recommended primary** | 85.9% |

**Methodology note:** v3 was the gold standard when published (reported in `TECHNICAL_REPORT.md`). v9 is now the recommended primary measurement — it uses a symmetric, artifact-free harness (Strands) with model pinning (Sonnet 4.6) and a think tool for both conditions. The 70→86% difference between v3 and v9 is explained by harness effects (tool artifact noise in kiro-cli), not skill quality. Anchor on **critical thinking** as the least-confounded dimension: skills improve reasoning quality 77–85% of the time regardless of harness.

**Harness effects:** The execution harness significantly affects measured win rates due to response artifact contamination in agentic harnesses. See [`HARNESS_EFFECTS.md`](./HARNESS_EFFECTS.md) for a detailed analysis of how tool interleaving, MCP noise, and asymmetric isolation confound pairwise coherence judgments.

## Interpreting Results

- **Overall delta:** Mean score difference (skills - baseline) across all prompts and dimensions
- **Win rate (v3+):** Percentage of prompts where the judge declared skills the winner
- **Per-skill N:** Number of valid prompts (excludes timeouts). "activated" count shows how many had the intended skill loaded.
- **Sig? (✓):** Paired t-test p < 0.05 for that dimension
- **Skill flags:** ✓ Intended loaded, ⚠ Unintended loaded, ✗ Intended not loaded, ○ No skill loaded
- **Cross-skill entries (3 of 41):** These rows test multi-skill activation and are labeled with a `cross-skill` category. Unlike single-skill entries, they measure whether the agent can combine knowledge from 2–3 skills in one response. A win here indicates effective skill composition, not the quality of any individual skill.

## Reproducibility

To reproduce results exactly:

1. **Pin the model.** Always use `--model` with the full model ID (e.g., `us.anthropic.claude-sonnet-4-6-20250514-v1:0`). Without pinning, Bedrock may route to a different model version.

2. **Check response metadata.** Each cached response file in `eval/results/responses/` includes metadata (model ID, backend, tools, timestamp). Verify these match your intended configuration before re-judging.

3. **Symmetric conditions.** Both baseline and skills conditions must have identical environment access — the ONLY variable should be skill content. See the [eval-setup-guidelines steering doc](../.kiro/steering/eval-setup-guidelines.md) for detailed parity requirements and known anti-patterns.

4. **Version label.** Use a unique `--version` tag for each configuration change to avoid mixing results from different setups.

Example reproducing v9:
```bash
python -m eval.run --parallel 2 --version v9 --pairwise \
  --model us.anthropic.claude-sonnet-4-6-20250514-v1:0 --tools think
```
