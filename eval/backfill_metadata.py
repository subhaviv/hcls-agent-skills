#!/usr/bin/env python3
"""Backfill metadata into response files that were generated before the metadata field was added."""
import json
from pathlib import Path

VERSIONS = {
    "v5-strands": {
        "backend": "strands",
        "model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "tools": [],
    },
    "v6-kiro-sonnet45": {
        "backend": "kiro-cli",
        "model": "claude-sonnet-4.5",
        "tools": ["thinking", "file-read"],  # kiro-cli native tools
    },
    "v7-strands-think": {
        "backend": "strands",
        "model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "tools": ["think"],
    },
}

results_dir = Path("eval/results/responses")

for version, meta in VERSIONS.items():
    version_dir = results_dir / version
    if not version_dir.exists():
        continue
    patched = 0
    for f in version_dir.glob("*.json"):
        data = json.loads(f.read_text())
        if "metadata" not in data:
            data["metadata"] = {
                "backend": meta["backend"],
                "model": meta["model"],
                "tools": meta["tools"],
                "skills_path": "./skills/" if data.get("condition") == "skills" else None,
            }
            f.write_text(json.dumps(data, indent=2))
            patched += 1
    print(f"{version}: patched {patched} files")

print("Done.")
