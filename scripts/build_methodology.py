"""Build the bilingual benchmark methodology pages."""
from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

import shell

ROOT = Path(__file__).resolve().parents[1]
e = html.escape
T = {
    "en": {
        "title": "Benchmark methodology", "lede": "How we plan to build and report real-world held-out sets.", "back": "Benchmark tables",
        "sections": [
            ("Open and closed sets", ["Each category has an open and a closed held-out set. Open sets use publishable images and references from multiple sources and are the headline benchmark. Closed sets may include private sources; we report them separately and give them less prominence because they cannot be fully reproduced independently.", "Sets are registered before scoring and use real-world examples representative of the problem, with reference text. Generated material is for development, never evaluation. Only registered held-out results are reported as performance."]),
            ("Source separation", ["A source is assigned to training or test, never both. Evaluation material is held out from training, tuning and model selection. Set documentation will describe sources, licences, reference creation, sampling and limitations without disclosing private material."]),
            ("Contamination policy v2", ["The same image, physical source or edition is excluded from training when it is in a test set. The same text in another format may be used in training; it is tagged. Results will be reported both including and excluding those tagged examples, with the distinction made clear."]),
            ("Launch criterion", [
                "Only registered open held-out sets of real documents count toward launch. HeOCR must achieve a "
                "state-of-the-art result in at least one of the six categories, with a character error rate (CER) "
                "at least 3% lower in relative terms than that of every eligible registered comparator in that category.",
                "The primary target is modern printed unpointed Hebrew. Release also requires the project owner's approval.",
            ]),
        ],
    },
    "he": {
        "title": "שיטת המבחנים", "lede": "איך נבנה ונדווח קבוצות של נתונים אמיתיים שהוחזקו בצד.", "back": "לטבלאות המדדים",
        "sections": [
            ("קבוצות פתוחות וסגורות", ["לכל קטגוריה קבוצה פתוחה וקבוצה סגורה שהוחזקו בצד. הקבוצות הפתוחות כוללות תמונות וטקסטי ייחוס שניתן לפרסם, ממקורות רבים, והן המבחן המרכזי. קבוצות סגורות עשויות לכלול מקורות פרטיים; נדווח אותן בנפרד ובהבלטה פחותה, מפני שלא ניתן לשחזר אותן במלואן באופן עצמאי.", "הקבוצות נרשמות לפני ההערכה וכוללות דוגמאות אמיתיות שמייצגות את הבעיה, עם טקסטי ייחוס. חומר שנוצר משמש לפיתוח בלבד, ולעולם לא להערכה. כביצועים מדווחות רק תוצאות על קבוצות רשומות שהוחזקו בצד."]),
            ("הפרדה בין מקורות", ["כל מקור משויך לאימון או למבחן, לעולם לא לשניהם. חומר ההערכה מוחזק בצד ואינו משמש לאימון, לכוונון או לבחירת מודל. תיעוד הקבוצה יתאר את המקורות, הרישיונות, יצירת טקסטי הייחוס, הדגימה והמגבלות בלי לחשוף חומר פרטי."]),
            ("מדיניות זיהום נתונים v2", ["אותה תמונה, אותו מקור פיזי או אותה מהדורה לא ייכללו באימון אם הם בקבוצת המבחן. מותר להשתמש באותו טקסט בפורמט אחר לאימון, והוא מתויג. התוצאות ידווחו גם עם הדוגמאות המתויגות וגם בלעדיהן, תוך הבהרת ההבדל."]),
            ("תנאי ההשקה", [
                "לתנאי ההשקה נחשבות רק תוצאות על מערכי הערכה פתוחים ורשומים של מסמכים אמיתיים שהוחזקו בצד. "
                "על HeOCR להשיג תוצאה בחזית התחום לפחות באחת משש הקטגוריות. באותה קטגוריה, שיעור שגיאות התווים "
                "(CER) של HeOCR צריך להיות נמוך ב־3% לפחות בחישוב יחסי מזה של כל מערכת השוואה רשומה וכשירה.",
                "היעד העיקרי הוא עברית מודרנית מודפסת ללא ניקוד. הפרסום דורש גם את אישור בעל הפרויקט.",
            ]),
        ],
    },
}


def page(lang):
    t = T[lang]
    sections = ''.join('<section><h2>' + e(title) + '</h2>' + ''.join('<p>' + e(p) + '</p>' for p in paragraphs) + '</section>\n' for title, paragraphs in t['sections'])
    return ''.join([shell.head(lang, e(t['title']), e(t['lede']), 'methodology'), shell.header(lang, 'methodology'),
                    shell.page_head(e(t['title']), f'<p class="lede">{e(t["lede"])}</p>'),
                    '<main id="main" class="wrap doc">\n', sections,
                    f'<p><a href="benchmarks.html">{e(t["back"])}</a></p></main>\n',
                    shell.footer(['<p><a href="./">HeOCR</a></p>']), shell.tail(lang)])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale = []
    for lang, path in (('he', ROOT / 'methodology.html'), ('en', ROOT / 'en/methodology.html')):
        output = page(lang)
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != output:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(output, encoding='utf-8')
    if stale:
        print('out of date: ' + ', '.join(stale), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
