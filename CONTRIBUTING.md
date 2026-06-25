# Contributing

Thanks for contributing a skill! This repo hosts agent skills for healthcare and life sciences, compatible with any platform that supports the [Agent Skills standard](https://agentskills.io).

## Adding a New Skill

1. Create a directory under `skills/<skill-name>/` (kebab-case, matches the `name` frontmatter).
2. Add a `SKILL.md` with YAML frontmatter and these sections: **Overview**, **Usage**, **Core Concepts**. Add others (Examples, References) as needed.
3. Keep the skill self-contained. Supporting files (templates, prompts, scripts) go in the same directory.
4. Verify your skill against the [Quality Checklist](./QUALITY_CHECKLIST.md) and the [Skill Design Guide](./SKILL_DESIGN_GUIDE.md).

### Folder Structure

```
skills/
  my-skill/
    SKILL.md
    templates/        # optional
    references/       # optional
```

### Frontmatter Schema

```yaml
---
name: my-skill                       # required, matches directory name
description: One-sentence summary    # required, shown in skill picker
version: 0.1.0                       # required, semver
tags:                                # required, must include category
  - category:reasoning               #   or category:pipeline
  - domain:oncology                  #   additional tags encouraged
---
```

## Skill Categories

- **reasoning** — Encodes methodology, decision frameworks, checklists, and domain expertise. Guides *how the agent thinks*. Example: choosing a statistical test, framing a differential diagnosis.
- **pipeline** — Encodes concrete tool invocations, code scaffolding, and deterministic transformations. Guides *what the agent runs or generates*. Example: a `nextflow` command recipe, a CDK stack template.

If a skill mixes both, split it or pick the dominant category.

## Workflow

1. Fork the repo.
2. Branch: `git checkout -b skill/<skill-name>` or `fix/<short-desc>`.
3. Author and locally test your skill with representative prompts in your agent platform of choice.
4. Run `python tests/validate_skill.py` to check structural requirements.
5. Run through the [Quality Checklist](./QUALITY_CHECKLIST.md) and the [Skill Design Guide](./SKILL_DESIGN_GUIDE.md).
6. Open a merge request describing the skill, category, and example prompts used for testing.

## Code of Conduct

Be respectful, assume good intent, and keep discussions on-topic. Report issues to the maintainers.
