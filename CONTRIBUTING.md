# Contributing

Thanks for contributing! This repo hosts agent skills for healthcare and life sciences, compatible with any platform that supports the [Agent Skills standard](https://agentskills.io).

## Skill Categories

- **reasoning** — Encodes methodology, decision frameworks, and domain expertise. Guides *how the agent thinks*.
- **pipeline** — Encodes tool invocations, code scaffolding, and deterministic transformations. Guides *what the agent runs*.

If a skill mixes both, split it or pick the dominant category.

## Before You Start

Read these first — they define what a valid skill looks like:

- **[Skill Design Guide](./SKILL_DESIGN_GUIDE.md)** — structural template, content patterns, and what makes skills succeed or fail.
- **[Quality Checklist](./QUALITY_CHECKLIST.md)** — the pre-merge checklist (maps directly to `tests/validate_skill.py`).
- **[Customizing Guide](./CUSTOMIZING.md)** — worked examples for modifying, extending, or creating skills from scratch.

## Workflow

1. Fork the repo on GitHub.
2. Clone your fork and create a branch: `git checkout -b skill/<skill-name>` or `fix/<short-desc>`.
3. Create `skills/<skill-name>/SKILL.md` (kebab-case directory matching the `name` frontmatter field).
4. Author your skill following the [Structural Template](./SKILL_DESIGN_GUIDE.md#the-structural-template).
5. Test locally with representative prompts in your agent platform of choice.
6. Validate structural requirements:
   ```bash
   python tests/validate_skill.py --skill <skill-name>
   ```
7. Walk through the [Quality Checklist](./QUALITY_CHECKLIST.md).
8. (Optional) Evaluate your skill. If you'd like to measure your skill's impact before opening a PR, generate 30 prompts and run the scoped eval:
   ```bash
   python eval/generate_prompts.py --skill <skill-name> --count 30 --force
   ```
   Then follow [Running eval for a single skill](./eval/README.md#running-eval-for-a-single-skill) to execute and review results. This step is optional — maintainers may run their own evaluation during review if you skip it.
9. Push to your fork and open a pull request describing the skill, its category, and example prompts used for testing.

## Pull Request Guidelines

- One skill per PR (unless tightly coupled).
- Include 2+ example prompts and describe expected behavior.
- All `validate_skill.py` checks must pass.
- If you ran an evaluation (optional, see step 8), report the results in the PR description.
- No PII or PHI in examples — use synthetic or public data.

## Code of Conduct

Be respectful, assume good intent, and keep discussions on-topic. Report issues to the maintainers.
