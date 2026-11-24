"""Shared aggregate format for the Space and bilingual site builder."""

from datetime import date
import json
import re
from pathlib import Path

SCHEMA = "heocr.leaderboard.results.v1"
DATASET = "HeOCR/p-mod-open-v0"
RESULTS_REPO = "HeOCR/hebrew-ocr-leaderboard-results"
MANIFEST = "f173417a49f960f8bdd2bf9950a9e676d2070aeb6d6a6a3b0066887af6a11190"
CATEGORIES = {
    "C1": ("Modern unpointed print", "דפוס מודרני ללא ניקוד"),
    "C2": ("Historical unpointed print", "דפוס היסטורי ללא ניקוד"),
    "C3": ("Modern pointed print", "דפוס מודרני מנוקד"),
    "C4": ("Historical pointed print", "דפוס היסטורי מנוקד"),
    "C5": ("Modern handwriting", "כתב יד מודרני"),
    "C6": ("Historical handwriting", "כתב יד היסטורי"),
}
STRATA = {
    "pooled": ("Pooled page CER", "שגיאת תווים מצרפית"),
    "archive": ("Archive", "ארכיון"),
    "issuer-render": ("Issuer render", "תצוגת המוציא לאור"),
    "issuer-scan": ("Issuer scan", "סריקת המוציא לאור"),
    "scanner": ("Office scanner", "סורק משרדי"),
    "phone-a": ("Phone A", "טלפון א׳"),
    "phone-b": ("Phone B", "טלפון ב׳"),
}
VIEWS = {
    "filtered": ("Common filtered positions", "מיקומים משותפים לאחר סינון"),
    "all": ("All reference positions", "כל המיקומים בטקסט הייחוס"),
}
READER_TYPES = {"open weights": "משקולות פתוחות", "API": "API", "commercial API": "API מסחרי"}
BIAS_NOTICE = "same model family took part in building v0 references (biased comparator)"
SHA = re.compile(r"[a-f0-9]{64}")
ROW_ID = re.compile(r"[a-z0-9-]{1,64}")
BASELINES = {"rivok-full", "rivok-lite", "tessdata-best", "tessdata-fast", "paddle"}


def text(value, length):
    return isinstance(value, str) and 0 < len(value) <= length and value == value.strip() and value.isprintable()


def valid_metrics(groups):
    if not isinstance(groups, dict) or groups.keys() != STRATA.keys():
        return False
    for item in groups.values():
        if not isinstance(item, dict) or item.keys() != {"edits", "chars"}:
            return False
        if any(type(x) is not int or x < 0 for x in item.values()) or (item["chars"] == 0 and item["edits"] != 0):
            return False
    return groups["pooled"]["chars"] > 0 and all(
        groups["pooled"][key] == sum(group[key] for name, group in groups.items() if name != "pooled")
        for key in ("edits", "chars")
    )


def valid_views(views):
    return isinstance(views, dict) and views.keys() == VIEWS.keys() and all(
        valid_metrics(groups) for groups in views.values()
    )


def validate(data):
    if not isinstance(data, dict) or data.keys() != {"schema", "benchmark", "rows"} or data["schema"] != SCHEMA:
        raise ValueError("Invalid leaderboard schema")
    if data["benchmark"] != {"dataset": DATASET, "manifest_sha256": MANIFEST, "pages": 31, "carriers": 65}:
        raise ValueError("Invalid benchmark scope")
    if not isinstance(data["rows"], list):
        raise ValueError("Invalid leaderboard rows")
    ids = set()
    for row in data["rows"]:
        fields = {"id", "category", "reader", "version", "type", "licence", "date", "scorer_version",
                  "verified", "submission_sha256", "views"}
        if not isinstance(row, dict) or row.keys() not in (fields, fields | {"diagnostic"}):
            raise ValueError("Invalid row fields")
        if not isinstance(row["id"], str) or not ROW_ID.fullmatch(row["id"]) or row["id"] in ids:
            raise ValueError("Invalid or repeated reader row")
        ids.add(row["id"])
        if (row["category"] != "C1" or row["type"] not in READER_TYPES or type(row["verified"]) is not bool
                or re.match(r"^heocr\b", str(row["reader"]), re.IGNORECASE)):
            raise ValueError("Invalid row classification")
        if not all(text(row[key], limit) for key, limit in
                   (("reader", 80), ("version", 60), ("licence", 80), ("scorer_version", 100))):
            raise ValueError("Invalid reader display fields")
        if not isinstance(row["date"], str) or date.fromisoformat(row["date"]).isoformat() != row["date"]:
            raise ValueError("Invalid result date")
        key = row["submission_sha256"]
        if key is not None and (not isinstance(key, str) or not SHA.fullmatch(key) or row["id"] != key):
            raise ValueError("Invalid submission pin")
        if key is None and not row["verified"]:
            raise ValueError("Unverified rows require a submission pin")
        if not valid_views(row["views"]):
            raise ValueError("Invalid score breakdown")
        if "diagnostic" in row:
            diagnostic = row["diagnostic"]
            if (not isinstance(diagnostic, dict)
                    or diagnostic.keys() != {"notice", "paired_carriers", "masked_carriers", "masked_views"}
                    or diagnostic["notice"] != BIAS_NOTICE
                    or (diagnostic["paired_carriers"], diagnostic["masked_carriers"]) != (56, 9)
                    or not valid_views(diagnostic["masked_views"])
                    or row["type"] != "commercial API" or not row["verified"] or key is not None):
                raise ValueError("Invalid diagnostic breakdown")
    if not BASELINES <= {row["id"] for row in data["rows"] if row["verified"] and row["submission_sha256"] is None}:
        raise ValueError("Required external baselines are missing")
    return data


def read_results(path: Path):
    return validate(json.loads(path.read_bytes()))


def cer(metric):
    return metric["edits"] / metric["chars"] if metric["chars"] else None


def percentage(metric):
    value = cer(metric)
    return "—" if value is None else f"{value:.2%}"


def ranked(data, view):
    return sorted((row for row in data["rows"] if "diagnostic" not in row), key=lambda row: (cer(row["views"][view]["pooled"]), row["reader"].casefold(), row["id"]))
