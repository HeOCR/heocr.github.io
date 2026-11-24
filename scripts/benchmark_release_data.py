"""Read the evaluation owner's release-safe aggregate bundle, pinned by byte digest."""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path

SCHEMA = "heocr.benchmark.scores.v1"
VIEW_IDS = ("all", "filtered")
CARRIER_IDS = ("pooled", "archive", "iphone", "issuer-render", "issuer-scan", "pixel", "scanner")


def require(condition, where):
    if not condition:
        raise ValueError(f"Invalid release data at {where}")


def fields(value, names, where):
    require(isinstance(value, dict) and value.keys() == set(names.split()), where)


def count(value, where, minimum=0):
    require(type(value) is int and value >= minimum, where)


def number(value, where, *, signed=False):
    require(type(value) in (Decimal, int) and (signed or 0 <= value), where)


def interval(value, where, *, signed=False):
    require(isinstance(value, list) and len(value) == 2, where)
    lo, hi = value
    number(lo, where, signed=signed)
    number(hi, where, signed=signed)
    require(lo <= hi, where)


def reader_names(rows):
    require(isinstance(rows, list) and bool(rows), "readers")
    names = {}
    for row in rows:
        fields(row, "id label", "reader")
        key, label = row["id"], row["label"]
        require(isinstance(key, str) and re.fullmatch(r"[A-Za-z0-9_.-]+", key), "reader id")
        require(isinstance(label, str) and 0 < len(label) <= 96 and label.isprintable(), "reader label")
        require(key not in names and label not in names.values(), "unique readers")
        names[key] = label
    return names


def open_row(row, names):
    fields(row, "reader cer chars edits wer words word_edits missed_numbers ref_numbers", "open result")
    require(isinstance(row["reader"], str) and row["reader"] in names, "open reader id")
    for key in ("chars", "words"):
        count(row[key], key, minimum=1)
    for key in ("edits", "word_edits", "missed_numbers", "ref_numbers"):
        count(row[key], key)
    require(row["missed_numbers"] <= row["ref_numbers"], "numeric misses")
    for key, numerator, denominator in (("cer", "edits", "chars"), ("wer", "word_edits", "words")):
        number(row[key], key)
        exact = Decimal(row[numerator]) / row[denominator]
        require(abs(row[key] - exact) < Decimal("1e-12"), key)
    return {**row, "reader_id": row["reader"], "reader": names[row["reader"]]}


def open_panel(value, names):
    fields(value, "aggregate_sha256 carriers category_order dataset issue_clusters line_cer metric pages score_scope view_labels views", "modern_print")
    require(value["category_order"] == 1 and value["metric"] == "page_cer" and value["line_cer"] is None, "registered metric")
    count(value["pages"], "registered pages", minimum=1)
    count(value["carriers"], "registered carriers", minimum=1)
    count(value["issue_clusters"], "issue_clusters", minimum=1)
    fields(value["views"], " ".join(VIEW_IDS), "registered views")
    views = {}
    panel = None
    for view_id in VIEW_IDS:
        groups = value["views"][view_id]
        fields(groups, " ".join(CARRIER_IDS), "view carrier coverage")
        views[view_id] = {}
        for group_id in CARRIER_IDS:
            group = groups[group_id]
            fields(group, "carriers readers", "carrier result")
            count(group["carriers"], "carriers")
            rows = group["readers"]
            expected = 10 if group["carriers"] else 0
            require(isinstance(rows, list) and len(rows) == expected, "panel size")
            if not rows:
                views[view_id][group_id] = {"carriers": 0, "readers": []}
                continue
            rows = [open_row(row, names) for row in rows]
            reader_ids = {row["reader_id"] for row in rows}
            require(len(reader_ids) == 10 and (panel is None or panel == reader_ids), "open reader panel")
            panel = reader_ids
            views[view_id][group_id] = {"carriers": group["carriers"], "readers": rows}
        actual = sum(groups[key]["carriers"] for key in CARRIER_IDS if key != "pooled")
        require(actual == groups["pooled"]["carriers"] == value["carriers"], "carrier census")
    return {"pages": value["pages"], "carriers": value["carriers"], "views": views}


def closed_panel(value, names):
    fields(value, "benchmark field_value_occurrences metric paddle_status page_cer pages readers reports score_scope", "closed aggregate")
    require(value["metric"] == "field_recall_pct" and value["page_cer"] is None, "closed metric")
    for key in ("pages", "reports", "field_value_occurrences"):
        count(value[key], key, minimum=1)
    rows = []
    seen = set()
    require(isinstance(value["readers"], list) and bool(value["readers"]), "closed reader rows")
    for row in value["readers"]:
        required = {"reader", "hits", "field_recall_pct", "ci95"}
        paired = {"delta_vs_rivok_full_pp", "paired_ci95_vs_rivok_full"}
        require(isinstance(row, dict) and row.keys() in (required, required | paired), "closed result")
        key = row["reader"]
        require(isinstance(key, str) and key in names and key not in seen, "closed reader id")
        seen.add(key)
        count(row["hits"], "hits")
        number(row["field_recall_pct"], "field recall")
        exact = Decimal(row["hits"] * 100) / value["field_value_occurrences"]
        require(0 <= exact <= 100 and abs(row["field_recall_pct"] - exact) < Decimal("1e-12"), "field recall")
        interval(row["ci95"], "field recall interval")
        require(row["ci95"][1] <= 100, "field recall interval")
        if paired <= row.keys():
            number(row["delta_vs_rivok_full_pp"], "paired change", signed=True)
            interval(row["paired_ci95_vs_rivok_full"], "paired interval", signed=True)
        rows.append({**row, "reader": names[key]})
    return {
        "pages": value["pages"], "reports": value["reports"],
        "field_value_occurrences": value["field_value_occurrences"], "results": rows,
    }


def validate(data):
    fields(data, "schema readers modern_print welfare_reports", "release")
    require(data["schema"] == SCHEMA, "schema")
    names = reader_names(data["readers"])
    return {"open": open_panel(data["modern_print"], names), "closed": closed_panel(data["welfare_reports"], names)}


def unique_keys(pairs):
    obj = dict(pairs)
    require(len(pairs) == len(obj), "duplicate JSON key")
    return obj


def reject_constant(_value):
    raise ValueError("Nonfinite number in release data")


def load(path: Path, sha256: str):
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == sha256, "SHA-256")
    data = json.loads(raw, parse_float=Decimal, parse_constant=reject_constant, object_pairs_hook=unique_keys)
    return validate(data)
