"""Generate the English and Hebrew benchmark status reports from the public results file."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import benchmark_release_data
import build_release_benchmark
import leaderboard_results

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_V0 = ROOT / "benchmarks" / "pmod-open-v0-scores.json"
PUBLISHED_V0_SHA256 = "18a35d121e41bda303e75c1db14b61f8b1c6cc0b1cc2035088b05a9c89072e26"

HISTORICAL_V01 = ROOT / "benchmarks" / "phist-open-v0.1-scores.json"
# Release-safe aggregate projection of the deciding measures and Google lanes.
# Receipts cb8ce168 and ed96179e, cross-checked against the prior run
# 9fdf3e8c, descriptive audit 4fd4cd2e, and model card dcb3f990.
HISTORICAL_V01_SHA256 = "097bc5173e8413f10f162bb8212a52fd12325515cb6e68ade6d10fbcaf0cf123"
LEADERBOARD = ROOT / "leaderboard" / "results.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        data = benchmark_release_data.load(PUBLISHED_V0, PUBLISHED_V0_SHA256)
        historical_raw = HISTORICAL_V01.read_bytes()
        if hashlib.sha256(historical_raw).hexdigest() != HISTORICAL_V01_SHA256:
            raise ValueError("Historical aggregate SHA-256 mismatch")
        historical = json.loads(historical_raw)
        leaderboard = leaderboard_results.read_results(LEADERBOARD)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    api_rows = tuple(row for row in leaderboard["rows"] if "diagnostic" in row)
    stale = build_release_benchmark.write_pages(
        ROOT, data, public_pages=31, check=args.check, historical=historical, api_rows=api_rows,
    )
    if stale:
        parser.error("Out of date: " + ", ".join(stale) + ". Run python3 scripts/build_benchmarks.py.")


if __name__ == "__main__":
    main()
