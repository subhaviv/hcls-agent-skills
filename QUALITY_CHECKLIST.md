---
title: Quality Checklist
inclusion: fileMatch
fileMatchPattern: 'skills/*/SKILL.md'
---

# Skill Quality Checklist

Use this checklist when authoring or reviewing a skill. A skill should satisfy every item before merging. Items marked with a property number (P*n*) are enforced by `tests/validate_skill.py`.

## Frontmatter (P1)

- [ ] `name` is present and matches the directory name
- [ ] `description` is present — includes trigger phrases (see P15 below)
- [ ] `usage` is present — one-line instruction for when to invoke
- [ ] `version` follows semver
- [ ] `tags` array present; first element is the literal string `skill`
- [ ] `tags` includes `category:reasoning` or `category:pipeline` (P14)
- [ ] Pipeline skills: `validated_against` includes date and key package versions

## Structure

- [ ] File is ≤ 500 lines (P12)
- [ ] `## Response Format` or `## Response Structure` section present (P13)
- [ ] `description` contains ≥ 12 quoted trigger keywords (P15)
- [ ] **Reasoning skills:** decision trees (├─/└─) OR ≥ 10 numbered steps (P16)
- [ ] **Pipeline skills:** ≥ 1 fenced code block (P16)
- [ ] **Reasoning skills with decision trees:** Response Format section contains "do not narrate" or "internal reasoning" instruction (P17)

## Content Quality

- [ ] Triggers are concrete (specific task phrases, not vague topics)
- [ ] Domain expertise is actionable (decision rules, checklists, commands) rather than generic background
- [ ] Skill is self-contained and works independently of other skills
- [ ] References are cited for any clinical, scientific, or regulatory claims

## Testing

- [ ] Tested with at least two representative example prompts
- [ ] Example prompts and outputs contain no PII or PHI (use synthetic or public data)
- [ ] `python tests/validate_skill.py --skill <name>` passes

## Sign-off

- [ ] Author has reviewed every item above
- [ ] Reviewer has reviewed every item above
