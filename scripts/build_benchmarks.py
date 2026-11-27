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
# C1 public rows (eval, restricted-eval #1936/#1937, built by build_public_scores.py 7c54fcf1): the HeOCR lane is the
# capture-only 1k model (receipt #1916); comparator bytes equal the v0 release; Kraken and Qwen appended.
PUBLISHED_V0 = ROOT / "benchmarks" / "c1-public-scores.json"
PUBLISHED_V0_SHA256 = "98e8db900e77ef9bc05edab39c66c1fc04f8dc676cbb36f357d0e7e54164a623"
# Hosted readers on the 56 original-equivalent C1 inputs (eval #1937, build_hosted_scores.py 05283760); Shay approved.
HOSTED_56 = ROOT / "benchmarks" / "c1-hosted-56-public-scores.json"
HOSTED_56_SHA256 = "deb3ef1174df5982ba607e4b53b76a3557a3594acddfdb84b258a5f0797901c2"
# PBY-H v0 stratum U public rows (eval #1937; score receipt #1895, registration #1880).
PBYH_V0 = ROOT / "benchmarks" / "pby-h-v0-public-scores.json"
PBYH_V0_SHA256 = "264d77050f162dd1dcf913494df79a66099658122a446e1180ef9e2a180133c6"

# Counted once per source page from the published manifest at HF revision
# 54d637d0. Manifest SHA-256 f173417a49f960f8bdd2bf9950a9e676d2070aeb6d6a3b0066887af6a11190.
MODERN_REFERENCE_LINES = 1863
MODERN_MATCHED_PAGES = 17

HISTORICAL_V01 = ROOT / "benchmarks" / "phist-open-v0.1-scores.json"
# Release-safe aggregate projection of the deciding measures and Google lanes.
# Receipts cb8ce168, ed96179e and 723180b1. The C2 registered verdict
# stays bound to the original comparator set.
HISTORICAL_V01_SHA256 = "24d136103135a0a9f3e85a3b4480e3047caa0553d8ca7f6e2233290f906b11dc"
LEADERBOARD = ROOT / "leaderboard" / "results.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        data = benchmark_release_data.load(PUBLISHED_V0, PUBLISHED_V0_SHA256)
        data["open"].update(reference_lines=MODERN_REFERENCE_LINES, matched_pages=MODERN_MATCHED_PAGES)
        historical_raw = HISTORICAL_V01.read_bytes()
        if hashlib.sha256(historical_raw).hexdigest() != HISTORICAL_V01_SHA256:
            raise ValueError("Historical aggregate SHA-256 mismatch")
        historical = json.loads(historical_raw)
        leaderboard = leaderboard_results.read_results(LEADERBOARD)
        pbyh = benchmark_release_data.load_pbyh(PBYH_V0, PBYH_V0_SHA256)
        hosted = benchmark_release_data.load_hosted(HOSTED_56, HOSTED_56_SHA256)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    api_rows = tuple(row for row in leaderboard["rows"] if "diagnostic" in row)
    stale = build_release_benchmark.write_pages(
        ROOT, data, public_pages=31, check=args.check, historical=historical, api_rows=api_rows, pbyh=pbyh, hosted=hosted,
    )
    if stale:
        parser.error("Out of date: " + ", ".join(stale) + ". Run python3 scripts/build_benchmarks.py.")


if __name__ == "__main__":
    main()
