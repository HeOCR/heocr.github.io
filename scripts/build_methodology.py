"""Build the bilingual benchmark methodology pages."""
from __future__ import annotations

import html

import shell

e = html.escape
T = {
    "en": {
        "title": "Benchmark methodology", "lede": "How we plan to build and report real-world held-out sets.", "back": "Benchmark tables",
        "sections": [
            ("Open and closed sets", [
                "Each category has an open and a closed held-out set. Open sets use publishable images and references from multiple sources and are the headline benchmark. Closed sets may include private sources; we report them separately and give them less prominence because they cannot be fully reproduced independently.",
                "Sets are registered before scoring and use real-world examples representative of the problem, with reference text. Generated material is for development, never evaluation. Only registered held-out results are reported as performance.",
                "Weighted rows combine the categories above them using the weights in the registered evaluation protocol.",
            ]),
            ("Source separation", ["A source is assigned to training or test, never both. Evaluation material is held out from training, tuning and model selection. Set documentation will describe sources, licences, reference creation, sampling and limitations without disclosing private material."]),
            ("Contamination policy", ["The same image, physical source or edition is excluded from training when it is in a test set. The same text in another format may be used in training; it is tagged. Results will be reported both including and excluding those tagged examples, with the distinction made clear."]),
        ],
    },
    "he": {
        "title": "שיטת המבחנים", "lede": "איך נבנה ונדווח קבוצות של נתונים אמיתיים שהוחזקו בצד.", "back": "לטבלאות המדדים",
        "sections": [
            ("קבוצות פתוחות וסגורות", [
                "לכל קטגוריה קבוצה פתוחה וקבוצה סגורה שהוחזקו בצד. הקבוצות הפתוחות כוללות תמונות וטקסטי ייחוס שניתן לפרסם, ממקורות רבים, והן המבחן המרכזי. קבוצות סגורות עשויות לכלול מקורות פרטיים; נדווח אותן בנפרד ובהבלטה פחותה, מפני שלא ניתן לשחזר אותן במלואן באופן עצמאי.",
                "הקבוצות נרשמות לפני ההערכה וכוללות דוגמאות אמיתיות שמייצגות את הבעיה, עם טקסטי ייחוס. חומר שנוצר משמש לפיתוח בלבד, ולעולם לא להערכה. כביצועים מדווחות רק תוצאות על קבוצות רשומות שהוחזקו בצד.",
                "השורות המשוקללות משלבות את הקטגוריות שמעליהן לפי המשקלים שנקבעו בפרוטוקול ההערכה הרשום.",
            ]),
            ("הפרדה בין מקורות", ["כל מקור משויך לאימון או למבחן, לעולם לא לשניהם. חומר ההערכה מוחזק בצד ואינו משמש לאימון, לכוונון או לבחירת מודל. תיעוד הקבוצה יתאר את המקורות, הרישיונות, יצירת טקסטי הייחוס, הדגימה והמגבלות בלי לחשוף חומר פרטי."]),
            ("מדיניות זיהום נתונים", ["אותה תמונה, אותו מקור פיזי או אותה מהדורה לא ייכללו באימון אם הם בקבוצת המבחן. מותר להשתמש באותו טקסט בפורמט אחר לאימון, והוא מתויג. התוצאות ידווחו גם עם הדוגמאות המתויגות וגם בלעדיהן, תוך הבהרת ההבדל."]),
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
