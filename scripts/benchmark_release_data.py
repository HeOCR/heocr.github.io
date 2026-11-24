"""Read the evaluation owner's release-safe aggregate bundle, pinned by byte digest."""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path

SCHEMA = "heocr.benchmark-release-aggregates.v1"
METRICS = {"cer", "wer"}


def require(condition, where):
    if not condition:
        raise ValueError(f"Invalid release data at {where}")


def fields(value, names, where):
    require(isinstance(value, dict) and value.keys() == set(names.split()), where)


def items(value, count, where):
    require(isinstance(value, list) and len(value) == count, where)


def label(value, where):
    require(isinstance(value, str) and 0 < len(value) <= 96 and value.isprintable(), where)


def localized(value, where):
    fields(value, "en he", where)
    for text in value.values():
        label(text, where)


def positive_count(value, where):
    require(type(value) is int and value > 0, where)


def rate(value, where):
    require(type(value) in (Decimal, int) and 0 <= value, where)


def metric(value, where):
    fields(value, "percent ci95 denominator", where)
    if value["percent"] is None:
        require(value["ci95"] is None and value["denominator"] in (None, 0), where)
        return
    rate(value["percent"], where)
    if value["ci95"] is not None:
        items(value["ci95"], 2, where)
        lo, hi = value["ci95"]
        rate(lo, where)
        rate(hi, where)
        require(lo <= hi, where)
    if value["denominator"] is not None:
        positive_count(value["denominator"], where)


def result_rows(rows, where, reader_count=None):
    require(isinstance(rows, list) and rows, where)
    if reader_count is not None:
        items(rows, reader_count, where)
    readers = []
    for row in rows:
        fields(row, "reader metrics", where)
        label(row["reader"], where)
        readers.append(row["reader"])
        metrics = row["metrics"]
        require(isinstance(metrics, dict) and "cer" in metrics and metrics.keys() <= METRICS, where)
        for value in metrics.values():
            metric(value, where)
    require(len(set(readers)) == len(readers), where)
    return set(readers)


def validate(data):
    fields(data, "schema p_mod_open uc_w", "release")
    require(data["schema"] == SCHEMA, "schema")
    open_set = data["p_mod_open"]
    fields(open_set, "public_pages carriers views", "p_mod_open")
    require(type(open_set["public_pages"]) is int and 0 < open_set["public_pages"] <= 31, "p_mod_open.public_pages")
    carriers = open_set["carriers"]
    require(isinstance(carriers, dict) and carriers, "p_mod_open.carriers")
    for carrier, name in carriers.items():
        require(re.fullmatch(r"[a-z0-9_-]+", carrier), "carrier id")
        localized(name, "carrier name")
    items(open_set["views"], 2, "p_mod_open.views")
    view_names = {"en": set(), "he": set()}
    readers = None
    for view in open_set["views"]:
        fields(view, "name results", "view")
        localized(view["name"], "view name")
        for lang, name in view["name"].items():
            require(name not in view_names[lang], "distinct view names")
            view_names[lang].add(name)
        require(isinstance(view["results"], dict) and view["results"].keys() == carriers.keys(), "view carrier coverage")
        for rows in view["results"].values():
            shown = result_rows(rows, "open results", reader_count=10)
            require(readers is None or readers == shown, "open reader panel")
            readers = shown
    closed = data["uc_w"]
    fields(closed, "pages results", "uc_w")
    positive_count(closed["pages"], "uc_w.pages")
    result_rows(closed["results"], "closed aggregates")


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
    validate(data)
    return data
