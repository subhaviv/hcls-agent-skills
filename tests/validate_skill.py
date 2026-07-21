#!/usr/bin/env python3
"""Repo-wide property validation for HCLS Skills Expansion spec.

Covers Properties 1, 2, 3, 8, 9, 11 from the design document.
Run from the repo root: python tests/validate_skill.py
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
AGENTS_DIR = REPO_ROOT / "agents"

EXCLUDED_FILES = {
    "IMPLEMENTATION-GAPS.md",
    "validate_skill.py",
}
EXCLUDED_DIRS = {".git", ".kiro", ".agents", "node_modules", "__pycache__", "tests", "results", ".venv", "dist", "build", ".eggs"}

REQUIRED_FRONTMATTER = ["name", "description", "usage", "version", "tags"]

NON_INCLUSIVE_TERMS = ["whitelist", "blacklist", "master", "slave"]

errors = []
SKILL_FILTER = None  # Set via --skill flag to validate a single skill


def _iter_skill_dirs():
    """Iterate skill directories, respecting SKILL_FILTER."""
    for entry in sorted(SKILLS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        if SKILL_FILTER and entry.name != SKILL_FILTER:
            continue
        yield entry


def error(prop: str, msg: str):
    errors.append(f"[{prop}] {msg}")


# -------------------------------------------------------------------------
# Property 1: Skill format uniformity
# -------------------------------------------------------------------------
def check_property_1():
    for entry in _iter_skill_dirs():
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            error("P1", f"{entry.name}/ missing SKILL.md")
            continue

        content = skill_md.read_text()
        if not content.startswith("---"):
            error("P1", f"{entry.name}/SKILL.md missing YAML frontmatter")
            continue

        # Extract frontmatter
        parts = content.split("---", 2)
        if len(parts) < 3:
            error("P1", f"{entry.name}/SKILL.md malformed frontmatter")
            continue

        fm_text = parts[1]
        try:
            fm = yaml.safe_load(fm_text) or {}
        except yaml.YAMLError as e:
            error("P1", f"{entry.name}/SKILL.md invalid YAML frontmatter: {e}")
            continue
        if not isinstance(fm, dict):
            error("P1", f"{entry.name}/SKILL.md frontmatter is not a mapping")
            continue

        for field in REQUIRED_FRONTMATTER:
            if field not in fm:
                error("P1", f"{entry.name}/SKILL.md missing frontmatter field: {field}")

        if "name" in fm and fm["name"] != entry.name:
            error("P1", f"{entry.name}/SKILL.md name='{fm['name']}' != folder name")

        if "tags" in fm:
            tags = fm["tags"]
            # tags may be a YAML list (block or flow style) or, defensively,
            # a plain string if hand-written outside spec.
            if isinstance(tags, list):
                first_tag = str(tags[0]) if tags else ""
            else:
                first_tag = str(tags).split(",")[0].strip().lstrip("[")
            if "skill" not in first_tag:
                error("P1", f"{entry.name}/SKILL.md tags[0] is not 'skill'")


# -------------------------------------------------------------------------
# Property 2: No broken references
# -------------------------------------------------------------------------
def check_property_2():
    broken_pattern = re.compile(r"skill://\.\./skills/")
    flat_pattern = re.compile(r"skills/([\w-]+)\.md(?!\w)")

    for fpath in _iter_repo_files():
        if fpath.name in EXCLUDED_FILES:
            continue
        try:
            content = fpath.read_text(errors="ignore")
        except Exception:
            continue

        if broken_pattern.search(content):
            error("P2", f"{fpath.relative_to(REPO_ROOT)}: contains skill://../skills/ pattern")

        # Check skill:// URIs resolve to existing dirs
        for match in re.finditer(r"skill://([a-z0-9-]+)", content):
            skill_name = match.group(1)
            if not (SKILLS_DIR / skill_name).is_dir():
                error("P2", f"{fpath.relative_to(REPO_ROOT)}: skill://{skill_name} does not resolve to a skills/ directory")


# -------------------------------------------------------------------------
# Property 3: Self-containment
# -------------------------------------------------------------------------
def check_property_3():
    for entry in _iter_skill_dirs():
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue

        content = skill_md.read_text()

        # No file:// references outside own folder
        for match in re.finditer(r'file://([^\s"]+)', content):
            ref = match.group(1)
            if ref.startswith("AGENTS") or ".." in ref:
                error("P3", f"{entry.name}/SKILL.md has external file:// ref: {ref}")

        # No skill:// cross-references
        if "skill://" in content:
            error("P3", f"{entry.name}/SKILL.md contains skill:// cross-reference")


# -------------------------------------------------------------------------
# Property 8: Agent bundle validity
# -------------------------------------------------------------------------
def check_property_8():
    for fpath in sorted(AGENTS_DIR.glob("*.json")):
        try:
            data = json.loads(fpath.read_text())
        except Exception as e:
            error("P8", f"{fpath.name}: invalid JSON: {e}")
            continue

        resources = data.get("resources", [])
        for res in resources:
            if res.startswith("skill://"):
                # skill:// is an install-time protocol that resolves to the
                # target platform's .kiro/skills/ directory. In repo context,
                # we strip the .kiro/skills/ prefix and validate against the
                # repo's skills/ directory.
                target_path = res.replace("skill://", "")
                # Strip the .kiro/skills/ prefix to get the repo-relative pattern
                kiro_prefix = ".kiro/skills/"
                if target_path.startswith(kiro_prefix):
                    repo_pattern = target_path[len(kiro_prefix):]
                else:
                    repo_pattern = target_path

                # Handle glob patterns (e.g., "*/SKILL.md") by checking that
                # at least one skill directory matches
                if "*" in repo_pattern:
                    matches = list(SKILLS_DIR.glob(repo_pattern))
                    if not matches:
                        error("P8", f"{fpath.name}: skill://{target_path} does not resolve to any skills")
                else:
                    # Explicit path — check it exists as file or directory
                    resolved = SKILLS_DIR / repo_pattern
                    if not resolved.exists():
                        error("P8", f"{fpath.name}: skill://{target_path} does not resolve")


# -------------------------------------------------------------------------
# Property 9: No hardcoded user paths or non-inclusive language
# -------------------------------------------------------------------------
def check_property_9():
    user_path_pattern = re.compile(r"/Users/\w+/")

    for fpath in _iter_repo_files():
        if fpath.name in EXCLUDED_FILES:
            continue
        try:
            content = fpath.read_text(errors="ignore")
        except Exception:
            continue

        if user_path_pattern.search(content):
            error("P9", f"{fpath.relative_to(REPO_ROOT)}: contains hardcoded /Users/ path")

        content_lower = content.lower()
        for term in NON_INCLUSIVE_TERMS:
            # Skip if it's in a "don't use" table or similar documentation context
            if term in content_lower:
                # Check it's not just documenting the term to avoid
                lines_with_term = [
                    l for l in content.split("\n")
                    if term in l.lower()
                    and "don't use" not in l.lower()
                    and "instead" not in l.lower()
                    and "avoid" not in l.lower()
                    and "| " not in l  # table rows documenting terms
                ]
                if lines_with_term:
                    error("P9", f"{fpath.relative_to(REPO_ROOT)}: contains non-inclusive term '{term}'")


# -------------------------------------------------------------------------
# Property 11: Script safety
# -------------------------------------------------------------------------
def check_property_11():
    for skill_dir in _iter_skill_dirs():
        scripts_dir = skill_dir / "scripts"
        if not scripts_dir.is_dir():
            continue

        for script in sorted(scripts_dir.glob("*.py")):
            content = script.read_text()

            if "argparse" not in content:
                error("P11", f"{script.relative_to(REPO_ROOT)}: does not use argparse")

            if "shell=True" in content:
                error("P11", f"{script.relative_to(REPO_ROOT)}: uses shell=True")


# -------------------------------------------------------------------------
# Property 12: Line count ≤ 500
# -------------------------------------------------------------------------
def check_property_12():
    for entry in _iter_skill_dirs():
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue
        line_count = len(skill_md.read_text().splitlines())
        if line_count > 500:
            error("P12", f"{entry.name}/SKILL.md has {line_count} lines (max 500)")


# -------------------------------------------------------------------------
# Property 13: Response Format section present
# -------------------------------------------------------------------------
def check_property_13():
    for entry in _iter_skill_dirs():
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue
        content = skill_md.read_text()
        if not re.search(r"^## Response (Format|Structure)", content, re.MULTILINE):
            error("P13", f"{entry.name}/SKILL.md missing '## Response Format' or '## Response Structure' section")


# -------------------------------------------------------------------------
# Property 14: Category tag present
# -------------------------------------------------------------------------
def check_property_14():
    for entry in _iter_skill_dirs():
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue
        content = skill_md.read_text()
        if "category:reasoning" not in content and "category:pipeline" not in content:
            error("P14", f"{entry.name}/SKILL.md missing category tag (category:reasoning or category:pipeline)")


# -------------------------------------------------------------------------
# Property 15: Trigger keywords ≥ 12
# -------------------------------------------------------------------------
def check_property_15():
    for entry in _iter_skill_dirs():
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue
        content = skill_md.read_text()
        # Extract description from frontmatter using yaml.safe_load
        # to correctly handle multi-line scalars (description: > and |)
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        fm_text = parts[1]
        try:
            fm = yaml.safe_load(fm_text)
        except yaml.YAMLError:
            continue
        if not isinstance(fm, dict):
            continue
        desc = fm.get("description", "") or ""
        # Count quoted trigger keywords
        triggers = re.findall(r'"([^"]+)"', desc)
        if len(triggers) < 12:
            error("P15", f"{entry.name}/SKILL.md has {len(triggers)} trigger keywords (min 12)")


# -------------------------------------------------------------------------
# Property 16: Required sections by category
# -------------------------------------------------------------------------
def check_property_16():
    for entry in _iter_skill_dirs():
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue
        content = skill_md.read_text()
        if "category:reasoning" in content:
            # Reasoning skills need decision trees (├─/└─) or numbered procedures (≥10 numbered steps)
            has_tree = "├─" in content or "└─" in content
            numbered_steps = re.findall(r"^\d+\.", content, re.MULTILINE)
            if not has_tree and len(numbered_steps) < 10:
                error("P16", f"{entry.name}/SKILL.md (reasoning) lacks decision trees or ≥10 numbered steps")
        elif "category:pipeline" in content:
            # Pipeline skills need code blocks
            code_blocks = re.findall(r"^```", content, re.MULTILINE)
            if len(code_blocks) < 2:  # at least 1 complete code block (open + close)
                error("P16", f"{entry.name}/SKILL.md (pipeline) has fewer than 1 code block")


# -------------------------------------------------------------------------
# Property 17: Do-not-narrate instruction for reasoning skills with decision trees
# -------------------------------------------------------------------------
def check_property_17():
    for entry in _iter_skill_dirs():
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue
        content = skill_md.read_text()
        # Only applies to reasoning skills with decision trees
        if "category:reasoning" not in content:
            continue
        if "├─" not in content and "└─" not in content:
            continue
        # Extract Response Format/Structure section content
        match = re.search(
            r"^## Response (Format|Structure)\s*\n(.*?)(?=^## |\Z)",
            content, re.MULTILINE | re.DOTALL
        )
        if not match:
            error("P17", f"{entry.name}/SKILL.md (reasoning with decision trees) missing Response Format section")
            continue
        section = match.group(2).lower()
        if "do not narrate" not in section and "internal reasoning" not in section:
            error("P17", f"{entry.name}/SKILL.md (reasoning with decision trees) Response Format missing 'do not narrate' or 'internal reasoning' instruction")


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------
def _iter_repo_files():
    """Iterate over text files in the repo, excluding .git and binary files."""
    for fpath in REPO_ROOT.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in fpath.parts):
            continue
        if fpath.is_file() and fpath.suffix in (
            ".md", ".json", ".py", ".sh", ".txt", ".yaml", ".yml", ".toml",
        ):
            yield fpath


# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------
def _self_test():
    """Regression tests for the validator's own parsing logic."""
    import tempfile, shutil

    test_dir = Path(tempfile.mkdtemp())
    try:
        # Test: multi-line folded scalar (description: >) with triggers
        skill_dir = test_dir / "test-folded-scalar"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            '---\n'
            'name: test-folded-scalar\n'
            'description: >\n'
            '  Test skill for folded scalars. Use when the user asks about parsing.\n'
            '  Triggers include "term1", "term2", "term3", "term4", "term5", "term6",\n'
            '  "term7", "term8", "term9", "term10", "term11", "term12", "term13".\n'
            'usage: Test.\n'
            'version: 1.0.0\n'
            'tags: [skill, category:reasoning]\n'
            '---\n\n# Test\n'
        )

        # Parse the description using the same logic as check_property_15
        content = (skill_dir / "SKILL.md").read_text()
        parts = content.split("---", 2)
        fm_text = parts[1]
        fm = yaml.safe_load(fm_text)
        desc = fm.get("description", "") or ""
        triggers = re.findall(r'"([^"]+)"', desc)

        assert len(triggers) == 13, (
            f"Folded scalar test: expected 13 triggers, got {len(triggers)}. "
            f"Description parsed as: {desc!r:.200}"
        )

        # Test: multi-line literal scalar (description: |) with triggers
        skill_dir2 = test_dir / "test-literal-scalar"
        skill_dir2.mkdir()
        (skill_dir2 / "SKILL.md").write_text(
            '---\n'
            'name: test-literal-scalar\n'
            'description: |\n'
            '  Test skill for literal scalars. Use when the user asks about parsing.\n'
            '  Triggers include "a1", "a2", "a3", "a4", "a5", "a6",\n'
            '  "a7", "a8", "a9", "a10", "a11", "a12".\n'
            'usage: Test.\n'
            'version: 1.0.0\n'
            'tags: [skill, category:pipeline]\n'
            '---\n\n# Test\n'
        )

        content2 = (skill_dir2 / "SKILL.md").read_text()
        parts2 = content2.split("---", 2)
        fm_text2 = parts2[1]
        fm2 = yaml.safe_load(fm_text2)
        desc2 = fm2.get("description", "") or ""
        triggers2 = re.findall(r'"([^"]+)"', desc2)

        assert len(triggers2) == 12, (
            f"Literal scalar test: expected 12 triggers, got {len(triggers2)}. "
            f"Description parsed as: {desc2!r:.200}"
        )

        # Test: inline description (should still work)
        skill_dir3 = test_dir / "test-inline"
        skill_dir3.mkdir()
        (skill_dir3 / "SKILL.md").write_text(
            '---\n'
            'name: test-inline\n'
            'description: Inline description. Triggers include "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9", "x10", "x11", "x12".\n'
            'usage: Test.\n'
            'version: 1.0.0\n'
            'tags: [skill, category:reasoning]\n'
            '---\n\n# Test\n'
        )

        content3 = (skill_dir3 / "SKILL.md").read_text()
        parts3 = content3.split("---", 2)
        fm_text3 = parts3[1]
        fm3 = yaml.safe_load(fm_text3)
        desc3 = fm3.get("description", "") or ""
        triggers3 = re.findall(r'"([^"]+)"', desc3)

        assert len(triggers3) == 12, (
            f"Inline test: expected 12 triggers, got {len(triggers3)}. "
            f"Description parsed as: {desc3!r:.200}"
        )

        print("Self-test PASSED ✓ (folded scalar, literal scalar, inline all parse correctly)")
        return True
    finally:
        shutil.rmtree(test_dir)


def main():
    global SKILL_FILTER

    parser = argparse.ArgumentParser(description="Validate HCLS skill properties")
    parser.add_argument("--skill", type=str, default=None,
                        help="Validate a single skill by name (e.g., genomic-variant-interpretation)")
    parser.add_argument("--self-test", action="store_true",
                        help="Run internal regression tests for the validator's parsing logic")
    args = parser.parse_args()

    if args.self_test:
        success = _self_test()
        sys.exit(0 if success else 1)

    if args.skill:
        skill_path = SKILLS_DIR / args.skill
        if not skill_path.is_dir():
            print(f"ERROR: Skill '{args.skill}' not found in {SKILLS_DIR}")
            sys.exit(1)
        SKILL_FILTER = args.skill
        print(f"Running property validations for skill: {args.skill}\n")
    else:
        print("Running property validations...\n")

    checks = [
        ("Property 1: Skill format uniformity", check_property_1),
        ("Property 2: No broken references", check_property_2),
        ("Property 3: Self-containment", check_property_3),
        ("Property 8: Agent bundle validity", check_property_8),
        ("Property 9: No hardcoded paths / inclusive language", check_property_9),
        ("Property 11: Script safety", check_property_11),
        ("Property 12: Line count ≤ 500", check_property_12),
        ("Property 13: Response Format section", check_property_13),
        ("Property 14: Category tag present", check_property_14),
        ("Property 15: Trigger keywords ≥ 12", check_property_15),
        ("Property 16: Category-specific content", check_property_16),
        ("Property 17: Do-not-narrate instruction", check_property_17),
    ]

    for name, fn in checks:
        print(f"  Checking {name}...")
        fn()

    print()
    if errors:
        print(f"FAILED — {len(errors)} error(s):\n")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print("ALL PROPERTIES PASSED ✓")
        sys.exit(0)


if __name__ == "__main__":
    main()
