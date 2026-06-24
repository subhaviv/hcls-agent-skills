#!/usr/bin/env python3
"""Smoke test for the Strands-based executor — runs 3 prompts through both conditions."""
import asyncio
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from eval.execute import execute_prompt

# Pick 3 prompts from varied domains
TEST_PROMPTS = [
    "eval/prompts/single/genomic-variant-interpretation-01.yaml",
    "eval/prompts/single/claims-billing-rules-01.yaml",
    "eval/prompts/single/digital-pathology-01.yaml",
]


async def main():
    results_dir = Path(tempfile.mkdtemp(prefix="hcls-eval-test-"))
    print(f"Results dir: {results_dir}\n")

    for prompt_path in TEST_PROMPTS:
        p = yaml.safe_load(Path(prompt_path).read_text())
        prompt_id = p["id"]
        prompt_text = p["prompt"]

        for condition in ["baseline", "skills"]:
            print(f"Running: {prompt_id} [{condition}]...")
            result = await execute_prompt(
                prompt_id, prompt_text, condition, results_dir, timeout=120
            )
            text = result["text"]
            cached = result.get("cached", False)
            skills = result.get("activated_skills", [])

            print(f"  Cached: {cached}")
            print(f"  Length: {len(text)} chars")
            print(f"  Preview: {text[:200]}...")
            if skills:
                print(f"  Skills activated: {', '.join(skills)}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
