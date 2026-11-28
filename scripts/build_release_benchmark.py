"""Build bilingual benchmark release pages in a local staging directory."""
from __future__ import annotations

import argparse
import html
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import benchmark_release_data
import build_methodology
import reader_access
import shell

ROOT = Path(__file__).resolve().parents[1]
e = html.escape
DATASET = "https://huggingface.co/datasets/HeOCR/p-mod-open-v0"
HISTORICAL_MODEL = "https://huggingface.co/HeOCR/heocr-p-hist-measured/tree/v1.1"
MODERN_MODEL = "https://huggingface.co/HeOCR/heocr-modern-measured/tree/v1.0"
MODERN_MODEL_ID = "heocr-modern-capture-1k"
T = {
    "en": {
        "lang": "en",
        "title": "HeOCR benchmarks", "lede": "A comparison of Hebrew OCR engines on real documents set aside for testing.",
        "open": "Open held-out sets", "open_text": "Open sets are designed so others can evaluate their readers independently.",
        "closed": "Closed held-out sets", "closed_text": "Closed sets may include private sources. They will also be reported, but cannot be independently reproduced in full.",
        "modern": "Modern unpointed print",
        "historical": "Historical unpointed print",
        "more_sets": "More sets in progress",
        "in_progress": ("Pointed modern print", "Pointed historical print", "Historical handwriting", "Modern handwriting", "Weighted scores"),
        "evaluation_view": "Evaluation view",
        "capture": "Capture type",
        "alternatives": "Other views and captures",
        "all_images": "All ({count})",
        "modern_views": (
            ("filtered", "Verified, no known training overlap (recommended)",
             "Scores words and characters in independently verified reference text, excluding known project training overlap and known public exposure."),
            ("all", "All reference text", "Scores every word and character in the benchmark’s reference text."),
        ),
        "historical_views": (
            ("filtered", "No known training-text overlap (recommended)",
             "Scores {filtered} lines of AI-reviewed reference text after removing known training-text overlap."),
            ("all", "All reference text", "Scores every eligible line in the reference text ({eligible} of {total} lines)."),
        ),
        "historical_result": "{model} led the registered comparators in both views, with {all_cer} CER across all eligible text and {filtered_cer} after filtering.",
        "modern_model_note": "Modern unpointed print",
        "historical_model_note": "Historical unpointed print",
        "api_capture": "Images scored",
        "api_alternatives": "Results for artwork-masked images",
        "carriers": {"scanner": "Scanner", "phone": "Phone", "issuer-render": "Digital render", "archive": "Archive", "issuer-scan": "Publisher scan"},
        "method": "Read the benchmark methodology", "preview": "Layout preview. Release figures are pending.",
        "open_result": "P-mod-open v0 results", "dataset": "Download the benchmark dataset", "doi": "Cite the dataset (Zenodo DOI)", "closed_missing": "No figure published here",
        "scope_pending": "The public dataset scope is pending source-rights review. The figures use the registered scope.",
        "published": "The public dataset includes {public} of the {registered} scored pages. The figures use the registered scope.",
        "numbers": "Numbers missed",
        "modern_intro": "Official gazettes, legal notices and other public documents in modern unpointed Hebrew.",
        "phone_matched_note": "Two different phones photographed the same {pages} pages; results are pooled.",
        "modern_capture_design": "A scanner and two phones captured the same {matched} printed pages, scored against the same text for each page. Other images come from archives or publishers’ PDFs.",
        "reading": "All measures are error rates. Lower is better.",
        "primary_cer": "The primary metric is page character error rate (CER).",
        "page_count": "{count:,} pages", "capture_count": "{count:,} images",
        "reference_count": "{count:,} reference lines", "region_count": "{count:,} image regions",
        "capture_notes": {
            "pooled": "Combines the images from all capture types.",
            "scanner": "Office scans of the printed pages also photographed by both phones.",
            "phone": "Results are pooled across the phones.",
            "issuer-render": "Page images rendered directly from the publishers’ PDFs.",
            "archive": "Page images obtained from archives.",
            "issuer-scan": "Scanned images supplied by the publishers.",
        },
        "metric_help": {
            "cer": "Character replacements, omissions and insertions divided by the number of reference characters.",
            "wer": "Word replacements, omissions and insertions divided by the number of reference words.",
            "numbers": "Share of number occurrences in the reference with no exact match in the OCR output.",
            "api_all": "Character edits divided by the number of reference characters in all reference text.",
            "api_filtered": "Character edits divided by the number of reference characters kept after filtering.",
        },
        "closed_nav": "Closed sets",
        "commercial": "Hosted readers (a different 56-image scope)",
        "commercial_note": "The hosted readers were measured separately on 56 images with the original scored pixels and nine with artwork masked for public release. Tesseract and Rivok are re-scored on the same 56 images for comparison. HeOCR was not scored on this scope, so compare it only in the table above. General hosted vision-language models lead on these modern documents.",
        "api_original": "56 images with the original scored pixels",
        "api_masked": "9 images with artwork masked",
        "gemini_note": "Gemini’s model family helped build the v0 references and may have an advantage.",
        "haiku_note": "Haiku 4.5 hit its output limit on 11 images.",
        "historical_intro": "Public-domain scans of pre-modern Hebrew print without vowel marks. The benchmark scores selected regions of the scanned pages.",
        "all_positions": "All positions",
        "historical_filtered": "Filtered",
        "historical_caveat": "HeOCR P-hist v1.1 is a fine-tune of Rivok Full. The v0.1 references came from two independent AI transcriptions and adjudication. A re-score with human-proofread references is coming.",
        "descriptive": "Descriptive",
        "historical_numbers_note": "C2 contains only 8 numbers; number recall is not compared on this set.",
        "cloud_note": "Google’s descriptive scores use the same eligible and filtered lines. The registered result was decided before these comparisons.",
        "primary": "Primary",
        "best": "Lowest error",
        "reader": "Reader", "cer": "CER", "wer": "Word error",
        "pbyh": "Modern unpointed literature",
        "pbyh_title": "PBY-H v0 results",
        "pbyh_intro": "Pages from public-domain Hebrew literary works in Project Ben-Yehuda, imaged from scans of the exact printed editions. The text has no vowel marks.",
        "work_count": "{count:,} works", "scored_lines": "{count:,} scored lines",
        "pbyh_masked": "{masked:,} lines where the printed edition and the reference text differ are left out for every reader.",
        "pbyh_finding": "{model} ({cer} CER) is statistically level with Rivok Lite, Google Cloud Vision and Rivok Full, and clearly better than Google Document AI, Tesseract and PaddleOCR.",
        "pbyh_refs": "The reference is Project Ben-Yehuda’s volunteer-proofread reading text, not a diplomatic transcription.",
        "pbyh_caveat": "HeOCR old-print v1.1 is a fine-tune of Rivok Full. Other Project Ben-Yehuda text is public and may be in any reader’s training data, ours included. The other readers’ training data is unknown.",
        "not_run": "Not run",
        "not_run_reason": "Google Drive’s built-in OCR was not run: its API refused Hebrew as an OCR language.",
        "pbyh_paired": "Differences are tested with a paired bootstrap by work (12 works).",
        "modern_notes": "HeOCR’s model is a fine-tune of Rivok Full, so a near-tie with it is expected. A CER above 100% means the reader inserted text that is not on the page. The other readers’ training data is unknown, and these pages may be on the public web.",
        "modern_finding": "{model} ties Rivok Full on modern printed documents ({ours} vs {rivok} CER in the recommended view). That is not a win under our registered test. It is clearly better than stock Tesseract.",
    },
    "he": {
        "lang": "he",
        "title": "מדדי ביצועים של HeOCR", "lede": "השוואה בין מנועי זיהוי טקסט בעברית על מסמכים אמיתיים שנשמרו לבדיקה.",
        "open": "קבוצות פתוחות שהוחזקו בצד", "open_text": "קבוצות פתוחות נועדו לאפשר הערכה עצמאית של מנועי זיהוי.",
        "closed": "קבוצות סגורות שהוחזקו בצד", "closed_text": "קבוצות סגורות עשויות לכלול מקורות פרטיים. גם תוצאותיהן ידווחו, אך לא ניתן לשחזר אותן במלואן באופן עצמאי.",
        "modern": "דפוס מודרני ללא ניקוד",
        "historical": "דפוס היסטורי ללא ניקוד",
        "more_sets": "מערכי מבחן נוספים בהכנה",
        "in_progress": ("דפוס מודרני מנוקד", "דפוס היסטורי מנוקד", "כתב יד היסטורי", "כתב יד מודרני", "ציונים משוקללים"),
        "evaluation_view": "איזה טקסט נבדק",
        "capture": "סוג תמונה",
        "alternatives": "תוצאות לפי טקסט או סוג תמונה",
        "all_images": "הכול ({count})",
        "modern_views": (
            ("filtered", "טקסט מאומת ללא חפיפה ידועה לאימון (מומלץ)",
             "בודקים מילים ותווים מטקסט ייחוס שאומת באופן עצמאי, אחרי הסרת חפיפה ידועה עם נתוני האימון של הפרויקט וטקסט שנחשף לציבור."),
            ("all", "כל טקסט הייחוס", "בודקים את כל המילים והתווים בטקסט הייחוס של המבחן."),
        ),
        "historical_views": (
            ("filtered", "ללא חפיפה ידועה לטקסט האימון (מומלץ)",
             "בודקים {filtered} שורות מטקסט הייחוס שהוכן באמצעות בינה מלאכותית, לאחר הסרת חפיפה ידועה עם טקסט האימון."),
            ("all", "כל טקסט הייחוס", "בודקים את כל השורות הכשירות בטקסט הייחוס ({eligible} מתוך {total})."),
        ),
        "historical_result": "{model} הוביל בשתי ההשוואות שנרשמו מראש עם {all_cer} שגיאות תווים בכל הטקסט הכשיר ו־{filtered_cer} לאחר סינון.",
        "modern_model_note": "לדפוס מודרני ללא ניקוד",
        "historical_model_note": "לדפוס היסטורי ללא ניקוד",
        "api_capture": "תמונות שנבדקו",
        "api_alternatives": "תוצאות לתמונות שבהן הוסתרו סמלים",
        "carriers": {"scanner": "סורק", "phone": "טלפון", "issuer-render": "תמונה דיגיטלית", "archive": "ארכיון", "issuer-scan": "סריקה של הגוף המפרסם"},
        "method": "לשיטת בניית המבחנים", "preview": "תצוגה מקדימה של המבנה. נתוני ההערכה יתווספו לקראת הפרסום.",
        "open_result": "תוצאות P-mod-open v0", "dataset": "להורדת מערך המבחן", "doi": "ציטוט מערך הנתונים (Zenodo DOI)", "closed_missing": "אין כאן תוצאה שפורסמה",
        "scope_pending": "היקף מערך הנתונים הציבורי ייקבע לאחר בדיקת זכויות המקור. התוצאות מחושבות לפי הקבוצה הרשומה.",
        "published": "מערך הנתונים הציבורי כולל {public} מתוך {registered} העמודים שהוערכו. התוצאות מחושבות לפי הקבוצה הרשומה.",
        "numbers": "מספרים שלא זוהו",
        "modern_intro": "רשומות, הודעות משפטיות ומסמכים ציבוריים נוספים בדפוס עברי מודרני ללא ניקוד.",
        "phone_matched_note": "שני טלפונים שונים צילמו את אותם {pages} עמודים. התוצאות מחושבות יחד.",
        "modern_capture_design": "אותם {matched} עמודים נסרקו וצולמו בשני טלפונים, וכל התמונות של עמוד נבדקות מול אותו טקסט ייחוס. יתר התמונות באו מארכיונים או מקובצי PDF של הגופים המפרסמים.",
        "reading": "כל המדדים מציגים שיעורי שגיאה. ככל שהשיעור נמוך יותר, התוצאה טובה יותר.",
        "primary_cer": "המדד הראשי הוא שיעור שגיאות התווים בעמוד (CER).",
        "page_count": "{count:,} עמודים", "capture_count": "{count:,} תמונות",
        "reference_count": "{count:,} שורות ייחוס", "region_count": "{count:,} אזורים בתמונות",
        "capture_notes": {
            "pooled": "כל התמונות, מכל סוגי המקורות.",
            "scanner": "סריקות של אותם עמודים מודפסים שצולמו גם בשני הטלפונים.",
            "phone": "התוצאות מחושבות יחד לכל התמונות מהטלפונים.",
            "issuer-render": "תמונות שהופקו ישירות מקובצי PDF של הגופים המפרסמים.",
            "archive": "תמונות עמודים שמקורן בארכיונים.",
            "issuer-scan": "סריקות שסיפקו הגופים המפרסמים.",
        },
        "metric_help": {
            "cer": "מספר התווים שהוחלפו, נשמטו או נוספו, חלקי מספר התווים בטקסט הייחוס.",
            "wer": "מספר המילים שהוחלפו, נשמטו או נוספו, חלקי מספר המילים בטקסט הייחוס.",
            "numbers": "שיעור המופעים של מספרים בטקסט הייחוס שלא נמצאה להם התאמה מדויקת בתוצאת הזיהוי.",
            "api_all": "מספר השינויים בתווים, חלקי מספר התווים בכל טקסט הייחוס.",
            "api_filtered": "מספר השינויים בתווים, חלקי מספר התווים בטקסט הייחוס שנותר לאחר סינון.",
        },
        "closed_nav": "קבוצות סגורות",
        "commercial": "שירותי זיהוי מקוונים (קבוצה אחרת של 56 תמונות)",
        "commercial_note": "השירותים המקוונים נבדקו בנפרד על 56 תמונות שבהן הפיקסלים זהים לאלה שנמדדו במקור, ועל תשע תמונות שבהן הוסתרו סמלים לקראת הפרסום. Tesseract ו־Rivok נבדקו שוב על אותן 56 תמונות לצורך השוואה. HeOCR לא נבדק בקבוצה הזו, ולכן יש להשוות אותו רק בטבלה שלמעלה. מודלים כלליים של ראייה ושפה מובילים במסמכים המודרניים האלה.",
        "api_original": "56 תמונות עם הפיקסלים המקוריים",
        "api_masked": "9 תמונות עם סמלים מוסתרים",
        "gemini_note": "מודל מאותה משפחה של Gemini השתתף בהכנת טקסטי הייחוס של v0, ולכן ייתכן שיש לו יתרון.",
        "haiku_note": "Haiku 4.5 הגיע למגבלת אורך התשובה ב־11 תמונות.",
        "historical_intro": "סריקות ברשות הציבור של דפוס עברי ישן ללא ניקוד. המבחן בודק את הטקסט באזורים שנבחרו מתוך העמודים הסרוקים.",
        "all_positions": "כל המיקומים",
        "historical_filtered": "לאחר סינון",
        "historical_caveat": "HeOCR P-hist v1.1 מבוסס על כוונון נוסף של Rivok Full. טקסטי הייחוס של v0.1 הוכנו בשני תעתוקים עצמאיים באמצעות בינה מלאכותית ובהכרעה ביניהם. בהמשך נחשב את הציונים שוב לפי טקסטי ייחוס שעברו הגהה אנושית.",
        "descriptive": "תיאורי",
        "historical_numbers_note": "ב־C2 יש רק 8 מספרים. במבחן הזה אין השוואה של זיהוי מספרים.",
        "cloud_note": "הציונים התיאוריים של Google חושבו על אותן שורות כשירות ומסוננות. התוצאה הרשומה נקבעה לפני ההשוואות האלה.",
        "primary": "ראשי",
        "best": "שיעור השגיאות הנמוך ביותר",
        "reader": "מנוע זיהוי", "cer": "CER", "wer": "שגיאות מילים",
        "pbyh": "ספרות בדפוס מודרני ללא ניקוד",
        "pbyh_title": "תוצאות PBY-H v0",
        "pbyh_intro": "עמודים מיצירות ספרות עבריות ברשות הציבור מפרויקט בן־יהודה, מתוך סריקות של המהדורות המודפסות עצמן. הטקסט אינו מנוקד.",
        "work_count": "{count:,} יצירות", "scored_lines": "{count:,} שורות שנבדקו",
        "pbyh_masked": "{masked:,} שורות שבהן המהדורה המודפסת וטקסט הייחוס שונים הוצאו מהבדיקה לכל המנועים.",
        "pbyh_finding": "{model} ({cer} שגיאות תווים) שקול סטטיסטית ל־Rivok Lite, ל־Google Cloud Vision ול־Rivok Full, וטוב בבירור מ־Google Document AI, מ־Tesseract ומ־PaddleOCR.",
        "pbyh_refs": "טקסט הייחוס הוא טקסט הקריאה של פרויקט בן־יהודה שעבר הגהה בידי מתנדבים, ולא תעתיק דיפלומטי.",
        "pbyh_caveat": "HeOCR old-print v1.1 מבוסס על כוונון נוסף של Rivok Full. טקסטים אחרים של פרויקט בן־יהודה זמינים לציבור וייתכן שהם בנתוני האימון של כל מנוע, כולל שלנו. נתוני האימון של המנועים האחרים אינם ידועים.",
        "not_run": "לא נבדק",
        "not_run_reason": "זיהוי הטקסט המובנה של Google Drive לא נבדק: הממשק שלו דחה עברית כשפת זיהוי.",
        "pbyh_paired": "ההבדלים נבדקו בשיטת bootstrap מזווגת לפי יצירה (12 יצירות).",
        "modern_notes": "המודל של HeOCR מבוסס על כוונון נוסף של Rivok Full, ולכן צפוי שהתוצאות יהיו קרובות. שיעור שגיאות תווים מעל 100% פירושו שהמנוע הוסיף טקסט שאינו מופיע בעמוד. נתוני האימון של המנועים האחרים אינם ידועים, וייתכן שהעמודים האלה זמינים ברשת.",
        "modern_finding": "{model} שקול ל־Rivok Full במסמכים מודפסים מודרניים ({ours} לעומת {rivok} שגיאות תווים בתצוגה המומלצת). לפי המבחן הרשום זה אינו ניצחון. הוא טוב בבירור מ־Tesseract הרגיל.",
    },
}


def numbers(value):
    return f'<bdi dir="ltr">{value}</bdi>'


def percentage(value):
    return numbers(f"{Decimal(value.numerator) * 100 / value.denominator:.2f}%")


def error_rate(edits, denominator):
    if denominator == 0:
        return None, ""
    return Fraction(edits, denominator), numbers(f"{edits:,} / {denominator:,}")


def result_table(t, table_id, caption, columns, rows):
    # Use exact ratios so display rounding cannot change the order or winners.
    def order(row):
        value = row["cells"][0][0]
        return value is None, value, row["name"].casefold()

    best = [
        min((row["cells"][i][0] for row in rows if row["cells"][i][0] is not None), default=None)
        for i in range(len(columns))
    ]
    open_rows = [row for row in rows if reader_access.classify(row["name"]) == "open"]
    best_open = [
        min((row["cells"][i][0] for row in open_rows if row["cells"][i][0] is not None), default=None)
        for i in range(len(columns))
    ]
    api_labels = {
        "api_all": f'{t["cer"]} · {t["all_positions"]}',
        "api_filtered": f'{t["cer"]} · {t["historical_filtered"]}',
    }
    headers = []
    for i, column in enumerate(columns):
        definition = e(t["metric_help"][column])
        label = api_labels[column] if column in api_labels else t[column]
        primary = f'<span class="benchmark-primary">{e(t["primary"])}</span>' if i == 0 else ""
        headers.append(
            f'<th scope="col"><details class="benchmark-metric-help" name="{table_id}-metrics">'
            f'<summary title="{definition}">{e(label)}'
            '<span class="benchmark-help-icon" aria-hidden="true">?</span></summary>'
            f'<span class="benchmark-tooltip">{definition}</span></details>{primary}</th>'
        )
    body = []
    for row in sorted(rows, key=order):
        ours = row.get("ours", False)
        marker = row.get("note")
        label = f'<bdi>{e(row["name"])}</bdi>'
        if row.get("model_url"):
            label = f'<a href="{e(row["model_url"])}">{label}</a>'
        label += reader_access.badge(row["name"], t["lang"])
        is_open = reader_access.classify(row["name"]) == "open"
        if marker:
            label += f'<small class="benchmark-reader-note">{e(marker)}</small>'
        cells = []
        for (value, fraction), lowest, lowest_open in zip(row["cells"], best, best_open, strict=True):
            if value is None:
                cells.append('<td class="num">—</td>')
                continue
            score = percentage(value)
            if value == lowest:
                score = (f'<span class="benchmark-best">{score}'
                         f'<span class="benchmark-sr-only"> ({e(t["best"])})</span></span>')
            elif is_open and value == lowest_open:
                score = (f'<span class="benchmark-best-open">{score}<span class="benchmark-sr-only"> '
                         f'({e(reader_access.BEST_OPEN[t["lang"]])})</span></span>')
            cells.append(f'<td class="num"><strong class="benchmark-score">{score}</strong>'
                         f'<small class="benchmark-fraction">{fraction}</small></td>')
        row_class = ' class="ours"' if ours else ""
        body.append(f'<tr{row_class}><th scope="row">{label}</th>{"".join(cells)}</tr>')
    return (
        f'<div id="{table_id}" class="tablewrap benchmark-table">'
        f'<table><caption class="benchmark-sr-only">{e(caption)}</caption>'
        f'<thead><tr><th scope="col">{e(t["reader"])}</th>{"".join(headers)}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div>\n'
    )


def link(target, label):
    return f'<a href="{e(target)}">{e(label)}</a>'


def disclosure(summary, content, *, identifier=None, group=None):
    attr = f' id="{identifier}"' if identifier else ""
    if group:
        attr += f' name="{group}"'
    return (f'<details class="method benchmark-details"{attr}><summary>{e(summary)}</summary>'
            f'<div class="benchmark-details-body">{content}</div></details>\n')


def radio_group(panel_id, dimension, legend, options):
    items = []
    for i, (key, label, _) in enumerate(options):
        checked = " checked" if i == 0 else ""
        items.append(
            f'<label><input type="radio" name="{panel_id}-{dimension}" '
            f'data-score-{dimension} value="{key}"{checked}><span>{e(label)}</span></label>'
        )
    return (f'<fieldset class="benchmark-options"><legend>{e(legend)}</legend>'
            f'<div class="benchmark-pills">{"".join(items)}</div></fieldset>')


def score_panel(t, panel_id, views, captures, tables, *, view_label, alternatives):
    """Render the default and native disclosures from the same score tables."""
    first_view = views[0][0]
    first_capture = captures[0][0]
    controls = [radio_group(panel_id, "view", view_label, views)]
    if len(captures) > 1:
        controls.append(radio_group(panel_id, "capture", t["capture"], captures))
    notes = []
    for capture, _, note in captures:
        if note:
            hidden = "" if capture == first_capture else " hidden"
            notes.append(f'<p class="note benchmark-capture-note" data-score-capture-note="{capture}"{hidden}>{e(note)}</p>')
    fallback = []
    for view, title, note in views:
        if note:
            hidden = "" if view == first_view else " hidden"
            notes.append(f'<p class="note benchmark-view-note" data-score-note="{view}"{hidden}>{e(note)}</p>')
        options = []
        for capture, capture_label, capture_note in captures:
            if (view, capture) == (first_view, first_capture):
                continue
            table = tables[view, capture]
            if len(captures) > 1:
                explanation = f'<p class="note">{e(capture_note)}</p>'
                table = disclosure(capture_label, explanation + table, group=f"{panel_id}-{view}-captures")
            options.append(table)
        if options and len(captures) > 1:
            explanation = f'<p class="note">{e(note)}</p>'
            fallback.append(disclosure(title, explanation + "".join(options), identifier=f"{panel_id}-{view}"))
        elif options:
            explanation = f'<p class="note">{e(note)}</p>' if note else ""
            fallback.append(explanation + "".join(options))
    return "".join([
        f'<div class="benchmark-selector" data-score-panel="{panel_id}">',
        f'<div class="benchmark-controls" data-score-controls hidden>{"".join(controls)}</div>',
        "".join(notes),
        '<p class="benchmark-sr-only" role="status" data-score-status></p>',
        f'<div data-score-active>{tables[first_view, first_capture]}</div>',
        disclosure(alternatives, "".join(fallback), identifier=f"{panel_id}-alternatives"),
        '</div>\n',
    ])


def text_score_cells(row):
    return [
        error_rate(row["edits"], row["chars"]),
        error_rate(row["word_edits"], row["words"]),
    ]


def best_modern_model(data):
    # The registered C1 primary view is filtered pooled page CER.
    candidates = [
        row for row in data["views"]["filtered"]["pooled"]["readers"]
        if row["reader_id"].startswith("heocr-") and row["reader_id"] != "heocr-stock"
    ]
    winner = min(candidates, key=lambda row: Fraction(row["edits"], row["chars"]), default=None)
    return winner["reader_id"] if winner is not None else None


def modern_rows(t, group, winner):
    rows = []
    for row in group["readers"]:
        reader = row["reader_id"]
        if reader.startswith("heocr-") and reader != winner:
            continue
        cells = [*text_score_cells(row), error_rate(row["missed_numbers"], row["ref_numbers"])]
        result = {"name": row["reader"], "cells": cells}
        if reader == winner:
            if reader == MODERN_MODEL_ID:
                result.update(name="HeOCR modern MEASURED v1.0", model_url=MODERN_MODEL)
            result.update(ours=True, note=t["modern_model_note"])
        rows.append(result)
    return rows


def modern_api_results(t, api_rows, hosted=None):
    columns = ("api_all", "api_filtered")
    views = (("original", t["api_original"], t["api_original"]),
             ("masked", t["api_masked"], t["api_masked"]))
    panel_id = "p-mod-open-api-scores"
    tables = {}
    for scope, title, _ in views:
        rows = []
        if scope == "original" and hosted is not None:
            by_view = {view: {r["reader_id"]: r for r in hosted["views"][view]} for view in ("all", "filtered")}
            for reader_id, row in by_view["all"].items():
                rows.append({"name": row["reader"], "cells": [
                    error_rate(by_view[view][reader_id]["edits"], by_view[view][reader_id]["chars"])
                    for view in ("all", "filtered")]})
        else:
            for row in api_rows:
                scores = row["diagnostic"]["masked_views"] if scope == "masked" else row["views"]
                counts = (scores[view]["pooled"] for view in ("all", "filtered"))
                rows.append({"name": row["reader"],
                             "cells": [error_rate(count["edits"], count["chars"]) for count in counts]})
        tables[scope, "pooled"] = result_table(t, f"{panel_id}-{scope}-pooled", title, columns, rows)
    return disclosure(t["commercial"], "".join([
        f'<p>{e(t["commercial_note"])}</p>',
        score_panel(t, panel_id, views, (("pooled", "", ""),), tables,
                    view_label=t["api_capture"], alternatives=t["api_alternatives"]),
        f'<p class="note">{e(t["gemini_note"])} {e(t["haiku_note"])}</p>',
    ]), identifier="p-mod-open-api")


def benchmark_metadata(t, counts, links=()):
    metadata = [e(t[label].format(count=count)) for label, count in counts]
    return f'<p class="benchmark-meta">{" · ".join([*metadata, *links])}</p>'


def pool_phone_captures(groups):
    streams = (groups["phone-a"], groups["phone-b"])
    fields = ("edits", "chars", "word_edits", "words", "missed_numbers", "ref_numbers")
    readers = {}
    for stream in streams:
        for row in stream["readers"]:
            total = readers.setdefault(row["reader_id"], {
                "reader_id": row["reader_id"], "reader": row["reader"], **dict.fromkeys(fields, 0),
            })
            for field in fields:
                total[field] += row[field]
    return {"carriers": sum(stream["carriers"] for stream in streams), "readers": list(readers.values())}


def open_results(t, data, public_pages, api_rows, hosted=None):
    counts = [("page_count", data["pages"]), ("capture_count", data["carriers"])]
    if "reference_lines" in data:
        counts.append(("reference_count", data["reference_lines"]))
    links = []
    if public_pages is not None:
        links = [link(DATASET, t["dataset"]), link(benchmark_release_data.PMOD_OPEN_V0_DOI_URL, t["doi"])]
    intro = t["modern_intro"]
    if "matched_pages" in data:
        intro += " " + t["modern_capture_design"].format(matched=data["matched_pages"])
    out = [
        f'<article class="benchmark-result" id="p-mod-open"><h3><bdi>{e(t["open_result"])}</bdi></h3>',
        benchmark_metadata(t, counts, links),
        f'<p class="benchmark-intro">{e(intro)}</p>',
        f'<p class="note">{e(t["primary_cer"])}</p>',
    ]
    if public_pages is None:
        out.append(f'<p class="note">{e(t["scope_pending"])}</p>')
    elif public_pages != data["pages"]:
        note = t["published"].format(public=public_pages, registered=data["pages"])
        out.append(f'<p class="note">{e(note)}</p>')

    views = {view: {**groups, "phone": pool_phone_captures(groups)}
             for view, groups in data["views"].items()}
    capture_notes = t["capture_notes"].copy()
    if "matched_pages" in data:
        capture_notes["phone"] = t["phone_matched_note"].format(pages=data["matched_pages"])
    captures = [("pooled", t["all_images"].format(count=data["carriers"]), capture_notes["pooled"])]
    for key, label in t["carriers"].items():
        count = views["all"][key]["carriers"]
        if count:
            captures.append((key, f"{label} ({count})", capture_notes[key]))
    winner = best_modern_model(data)
    pooled = {row["reader_id"]: row for row in views["filtered"]["pooled"]["readers"]}
    if winner is not None and "rivok-full" in pooled:
        cer = lambda r: percentage(Fraction(pooled[r]["edits"], pooled[r]["chars"]))  # noqa: E731
        name = modern_rows(t, views["filtered"]["pooled"], winner)
        name = next(r["name"] for r in name if r.get("ours"))
        out.append('<p class="benchmark-finding">' + e(t["modern_finding"]).format(
            model=f'<bdi>{e(name)}</bdi>', ours=cer(winner), rivok=cer("rivok-full")) + "</p>")
    columns = ("cer", "wer", "numbers")
    panel_id = "p-mod-open"
    tables = {
        (view, capture): result_table(t, f"{panel_id}-{view}-{capture}", f"{label} · {title}", columns,
                                      modern_rows(t, views[view][capture], winner))
        for view, label, _ in t["modern_views"]
        for capture, title, _ in captures
    }
    out.append(score_panel(t, panel_id, t["modern_views"], captures, tables,
                           view_label=t["evaluation_view"], alternatives=t["alternatives"]))
    out.append(f'<p class="note">{e(t["modern_notes"])}</p>')
    if api_rows:
        out.append(modern_api_results(t, api_rows, hosted))
    out.append("</article>\n")
    return "".join(out)


def historical_results(t, data):
    views = [
        (view, label, note.format(eligible=data["eligible_lines"], filtered=data["filtered_lines"],
                                 total=data["reference_lines"]))
        for view, label, note in t["historical_views"]
    ]
    panel_id = "p-hist-open-scores"
    columns = ("cer", "wer")
    tables = {}
    for view, label, _ in views:
        rows = []
        for row in data["readers"]:
            ours = row["id"].startswith("heocr-")
            note = t["historical_model_note"] if ours else t["descriptive"] if row["descriptive"] else None
            model_url = HISTORICAL_MODEL if row["id"] == "heocr-p-hist-v1-1" else None
            rows.append({"name": row["name"], "ours": ours, "model_url": model_url,
                         "note": note, "cells": text_score_cells(row[view])})
        tables[view, "pooled"] = result_table(t, f"{panel_id}-{view}-pooled", label, columns, rows)

    model = next(row for row in data["readers"] if row["id"].startswith("heocr-"))

    def model_cer(view):
        return percentage(Fraction(model[view]["edits"], model[view]["chars"]))

    finding = e(t["historical_result"]).format(model=f'<bdi>{e(model["name"])}</bdi>',
                                              all_cer=model_cer("all"), filtered_cer=model_cer("filtered"))
    return "".join([
        f'<article class="benchmark-result" id="p-hist-open"><h3><bdi>{e(data["dataset"])}</bdi></h3>',
        benchmark_metadata(t, [("page_count", data["leaves"]), ("region_count", data["regions"]),
                               ("reference_count", data["reference_lines"])]),
        f'<p class="benchmark-intro">{e(t["historical_intro"])}</p>',
        f'<p class="note">{e(t["primary_cer"])}</p>',
        f'<p class="benchmark-finding">{finding}</p>',
        score_panel(t, panel_id, views, (("pooled", "", ""),), tables, view_label=t["evaluation_view"],
                    alternatives=views[1][1]),
        f'<p class="note benchmark-footnote">{e(t["historical_numbers_note"])}</p>',
        f'<p class="note">{e(t["cloud_note"])}</p>',
        f'<p class="note">{e(t["historical_caveat"])}</p>',
        "</article>\n",
    ])


def pbyh_results(t, data):
    panel_id = "pby-h-open-scores"
    rows = []
    for row in data["readers"]:
        ours = row["id"].startswith("heocr-")
        if row["status"] == "not_run":
            rows.append({"name": row["label"], "note": t["not_run"], "cells": [(None, ""), (None, "")]})
            continue
        rows.append({"name": row["label"], "ours": ours,
                     "model_url": HISTORICAL_MODEL if row["id"] == "heocr-p-hist-v1-1" else None,
                     "cells": text_score_cells(row)})
    table = result_table(t, f"{panel_id}-pooled", t["pbyh_title"], ("cer", "wer"), rows)
    model = next(row for row in data["readers"] if row["id"].startswith("heocr-"))
    finding = e(t["pbyh_finding"]).format(model=f'<bdi>{e(model["label"])}</bdi>',
                                         cer=percentage(Fraction(model["edits"], model["chars"])))
    notes = [t["pbyh_masked"].format(masked=data["masked_lines"]), t["pbyh_refs"], t["pbyh_paired"]]
    if any(row["status"] == "not_run" for row in data["readers"]):
        notes.append(t["not_run_reason"])
    notes.append(t["pbyh_caveat"])
    return "".join([
        f'<article class="benchmark-result" id="pby-h-open"><h3><bdi>{e(t["pbyh_title"])}</bdi></h3>',
        benchmark_metadata(t, [("page_count", data["pages"]), ("work_count", data["works"]),
                               ("scored_lines", data["scored_lines"])]),
        f'<p class="benchmark-intro">{e(t["pbyh_intro"])}</p>',
        f'<p class="note">{e(t["primary_cer"])}</p>',
        f'<p class="benchmark-finding">{finding}</p>',
        table,
        "".join(f'<p class="note">{e(note)}</p>' for note in notes),
        "</article>\n",
    ])


def page(lang, data, public_pages=None, *, historical=None, api_rows=(), pbyh=None, hosted=None):
    t = T[lang]
    toc = []
    open_panels = []
    if data is not None:
        toc.append(("p-mod-open", e(t["modern"]), None))
        open_panels.append(open_results(t, data["open"], public_pages, api_rows, hosted))
    if historical is not None:
        toc.append(("p-hist-open", e(t["historical"]), None))
        open_panels.append(historical_results(t, historical))
    if pbyh is not None:
        toc.append(("pby-h-open", e(t["pbyh"]), None))
        open_panels.append(pbyh_results(t, pbyh))
    if not toc:
        toc.append(("open", e(t["open"]), None))
    toc.append(("closed", e(t["closed_nav"]), None))
    preview_note = f'<p class="note">{e(t["preview"])}</p>' if data is None else ""
    badges = "".join(f"<li>{e(category)}</li>" for category in t["in_progress"])
    return "".join([
        shell.head(lang, e(t["title"]), e(t["lede"]), "bench"), shell.header(lang, "bench"),
        '<main id="main" class="bench benchmark-page">\n',
        shell.page_head(e(t["title"]), f'<p class="lede">{e(t["lede"])}</p><p>{e(t["reading"])} {link("methodology.html", t["method"])}</p>{preview_note}'
                        + reader_access.legend(lang)),
        shell.toc(lang, toc),
        f'<section id="open" class="wrap domain"><h2 class="benchmark-sr-only">{e(t["open"])}</h2>',
        "".join(open_panels),
        "</section>\n",
        '<section id="closed" class="wrap domain">',
        disclosure(t["closed"], f'<p>{e(t["closed_text"])}</p><p class="note">{e(t["closed_missing"])}</p>'),
        "</section>\n",
        '<section class="wrap benchmark-progress" aria-labelledby="benchmark-progress-title">',
        f'<h2 id="benchmark-progress-title">{e(t["more_sets"])}</h2><ul>{badges}</ul>',
        '</section>\n</main>\n',
        shell.footer(['<p><a href="./">HeOCR</a></p>']),
        f'<script src="{shell.prefix(lang)}benchmark-controls.js" defer></script>',
        shell.tail(lang),
    ])


def write_pages(output_dir, data, public_pages, *, check, historical=None, api_rows=(), pbyh=None, hosted=None,
                strict=False):
    stale = []
    for lang in shell.LANGS:
        benchmark = page(lang, data, public_pages, historical=historical, api_rows=api_rows, pbyh=pbyh, hosted=hosted)
        if strict:
            reader_access.check_classified(benchmark)
        for key, output in (("bench", benchmark), ("methodology", build_methodology.page(lang))):
            relative = shell.site_path(lang, key)
            path = output_dir / relative
            if check:
                if not path.is_file() or path.read_text(encoding="utf-8") != output:
                    stale.append(relative)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(output, encoding="utf-8")
    return stale


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--release-data", type=Path)
    parser.add_argument("--sha256")
    parser.add_argument("--public-pages", type=int)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if (args.release_data is None) != (args.sha256 is None):
        parser.error("--release-data and --sha256 must be provided together")
    if args.public_pages is not None and args.release_data is None:
        parser.error("--public-pages requires --release-data")
    output_dir = args.out_dir.resolve()
    if output_dir.is_relative_to(ROOT):
        parser.error("--out-dir must be outside this site checkout")
    try:
        data = benchmark_release_data.load(args.release_data, args.sha256) if args.release_data else None
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.public_pages is not None and not 1 <= args.public_pages <= data["open"]["pages"]:
        parser.error("--public-pages exceeds the registered page scope or is zero")
    stale = write_pages(output_dir, data, args.public_pages, check=args.check)
    if stale:
        print("out of date: " + ", ".join(stale), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
