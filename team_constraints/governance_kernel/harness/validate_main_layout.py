#!/usr/bin/env python3
"""Validate the constrained main-branch layout."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
ALLOWED_TOP_LEVEL = {"this_project", "team_constraints", "CLAUEDE.md", ".git"}


def main() -> int:
    actual = {p.name for p in ROOT.iterdir()}
    unexpected = sorted(actual - ALLOWED_TOP_LEVEL)
    required_missing = sorted({"this_project", "team_constraints", "CLAUEDE.md"} - actual)
    if unexpected or required_missing:
        if unexpected:
            print("unexpected top-level entries:")
            for item in unexpected:
                print(f"- {item}")
        if required_missing:
            print("missing top-level entries:")
            for item in required_missing:
                print(f"- {item}")
        return 1
    print("main layout validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
