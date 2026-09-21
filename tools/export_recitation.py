#!/usr/bin/env python3
"""يُخرج تلاوة إبراهيم في صيغةٍ يقبلها تطبيقٌ آخر.

تطبيقات المصحف لا تقبل الصوت وحده: تقبله ومعه «مقاطع» — متى تبدأ كل
آية ومتى تنتهي، بالملّي ثانية، منسوبةً إلى ملفٍ بعينه. وعندنا هذا فعلًا،
لكنه مقيسٌ على ملفات أوجه المصحف (khatma/N.mp3) لا على ملفات السور.

فيُخرَج على مستوى الوجه، وهو ما نملك قياسه يقينًا. ومن أراده على مستوى
السورة فعليه بمُدَد الأوجه — انظر --durations أدناه، واقرأ التحذير في
آخر هذا الملف قبل أن يعتمد عليه.

    python3 tools/export_recitation.py app/public/ayah-timings.json -o out/
    python3 tools/export_recitation.py … --durations durations.json
    python3 tools/export_recitation.py … --report
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict

TOTAL_PAGES = 604
SURAH_COUNT = 114


def load_timings(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    pages = d.get("pages") or {}
    return {int(k): v for k, v in pages.items() if str(k).isdigit()}


def parse_key(key):
    s, a = key.split(":")
    return int(s), int(a)


def read_version():
    """نسخةُ البيانات من ملف VERSION بجذر المستودع، أو None.

    من أخذ هذه البيانات لا يعرف أعندَه آخرُها أم نسخةٌ فيها عيبٌ عُولج،
    فالرقم يُكتَب داخل المخرجات نفسها لا في المستودع وحده: الملفُّ
    يُنسَخ إلى تطبيقاتٍ أخرى ويُفارق ما حوله.
    """
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "VERSION")
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None


def build_segments(pages, durations=None):
    """مقاطعُ الآيات، مرتّبةً، مع نهاية كل واحدة ومن أين جاءت.

    وأصحُّ النهايات ما قِيس داخل السكتة بين الآيتين (`end` من
    snap_cuts.py)، ثم بدايةُ التالية — وهي تقديرٌ لا قياس، انظر تعليقها
    أدناه — ثم نهايةُ ملف الوجه للأخيرة فيه، ولا تُعرَف إلا بمُدَده.
    فإن لم تُعطَ تُركت النهاية فارغةً ولم تُخمَّن: نهايةٌ مخترعة تقطع
    آيةً أو تُدخل فيها ما بعدها.
    """
    out = []
    # الآية التي تبدأ في وجهٍ وتمتدّ إلى الذي يليه تُذكَر في الاثنين.
    # المعتبَرُ أولُ ظهورٍ لها بترتيب المصحف، وهو موضع ابتدائها.
    seen = set()
    for page in sorted(pages):
        rows = pages[page] or []
        for i, row in enumerate(rows):
            key = row.get("key")
            start = row.get("start")
            if key is None or start is None:
                continue
            surah, ayah = parse_key(key)
            if (surah, ayah) in seen:
                continue
            seen.add((surah, ayah))

            # النهايةُ المذكورة صراحةً تُقدَّم على بداية التي تليها.
            #
            # وبدايةُ التالية نهايةٌ رديئة: هي تقديرُ المحاذاة لموضع أول
            # كلمةٍ منها، وخطؤه أعشارُ ثانية. فإن تأخّر بقي في ذيل هذه
            # الآية أوّلُ حرفٍ من تلك، فإذا تُليتا متتابعتين في تطبيقٍ
            # يقصّ عليهما سُمع ذلك الحرف مرّتين — وهو ما وقع فعلًا. أما
            # في تطبيق المصحف فالرقم يحرّك تظليلًا والصوتُ متّصلٌ لا
            # يُقَصّ، فلا يُحَسّ منه شيء.
            #
            # وtools/snap_cuts.py يمسح الصوت فينقل كل حدٍّ إلى السكتة
            # التي بين الآيتين ويكتب `end` صريحةً، فتبقى بين الملفّين
            # فرجةٌ لا نطقَ فيها.
            end = row.get("end")
            source = "silence" if end is not None else ""
            if end is None and i + 1 < len(rows) and rows[i + 1].get("start") is not None:
                end = rows[i + 1]["start"]
                source = "next_start"
            if end is None and durations and page in durations:
                end = durations[page]
                source = "file_end"

            out.append({
                "surah": surah,
                "ayah": ayah,
                "mushaf_page": page,
                "audio_file": f"khatma/{page}.mp3",
                "start_ms": int(round(float(start) * 1000)),
                "end_ms": None if end is None else int(round(float(end) * 1000)),
                # من أين جاءت النهاية. الفرقُ بين مقيسٍ ومقدَّر ليس
                # تفصيلًا: المقدَّر هو الذي يُسمَع منه الحرفُ مرّتين،
                # ومن يأخذ هذه البيانات له أن يعرف أيَّهما بيده.
                "end_source": source,
            })
    out.sort(key=lambda r: (r["surah"], r["ayah"]))
    return out


def report(pages, segments):
    have = set(pages)
    missing = [p for p in range(1, TOTAL_PAGES + 1) if p not in have]
    print(f"أوجه فيها توقيتات : {len(have)} من {TOTAL_PAGES}")
    if missing:
        head = ", ".join(str(p) for p in missing[:20])
        print(f"أوجه ناقصة        : {len(missing)} — {head}"
              f"{'…' if len(missing) > 20 else ''}")

    by_surah = defaultdict(int)
    for s in segments:
        by_surah[s["surah"]] += 1
    print(f"آيات مُوقَّتة       : {len(segments)} من 6236")
    empty = [n for n in range(1, SURAH_COUNT + 1) if not by_surah.get(n)]
    if empty:
        print(f"سور بلا أي آية    : {len(empty)} — {', '.join(map(str, empty[:20]))}"
              f"{'…' if len(empty) > 20 else ''}")

    open_end = sum(1 for s in segments if s["end_ms"] is None)
    if open_end:
        print(f"آيات بلا نهاية    : {open_end} (آخر آيةٍ في كل وجه — تحتاج --durations)")

    # ترتيبٌ غير تصاعدي داخل وجهٍ واحد علامةُ محاذاةٍ فاسدة.
    bad = []
    for page, rows in pages.items():
        starts = [r.get("start") for r in (rows or []) if r.get("start") is not None]
        if any(b < a for a, b in zip(starts, starts[1:])):
            bad.append(page)
    print(f"أوجه ترتيبها مختلّ : {len(bad)}" + (f" — {bad[:20]}" if bad else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("timings", help="مسار ayah-timings.json")
    ap.add_argument("-o", "--out", default="recitation-export", help="مجلد الإخراج")
    ap.add_argument("--durations", help='JSON: {"1": 41.2, "2": 63.9, …} مدّة كل وجه بالثواني')
    ap.add_argument("--report", action="store_true", help="اطبع تقرير تغطية ولا تكتب شيئًا")
    args = ap.parse_args()

    pages = load_timings(args.timings)
    if not pages:
        sys.exit("لا توقيتات في الملف.")

    durations = None
    if args.durations:
        with open(args.durations, encoding="utf-8") as f:
            durations = {int(k): float(v) for k, v in json.load(f).items()}

    segments = build_segments(pages, durations)

    if args.report:
        report(pages, segments)
        return

    os.makedirs(args.out, exist_ok=True)

    csv_path = os.path.join(args.out, "segments.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(segments[0].keys()))
        w.writeheader()
        w.writerows(segments)

    json_path = os.path.join(args.out, "segments.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "reciter": "Dr. Ibrahim Hassan",
            "reciter_ar": "د. إبراهيم حسن",
            "mushaf": "Madani (Hafs)",
            "audio_layout": "one file per mushaf page, 1..604",
            "time_unit": "ms, relative to the start of each audio_file",
            # النسخةُ تُقرَأ من ملف VERSION ولا تُكتَب هنا: رقمان في
            # موضعين يفترقان عند أوّل إصدار.
            "version": read_version(),
            "end_source_values": {
                "silence": "مقيسٌ داخل السكتة بين الآيتين — موثوق",
                "next_start": "تقديرٌ: مبدأ الآية التالية. قد يتأخّر فيُسمَع أوّلُ حرفٍ مرّتين",
                "file_end": "نهاية ملف الوجه",
            },
            "segments": segments,
        }, f, ensure_ascii=False, indent=1)

    print(f"كُتب {len(segments)} مقطعًا:")
    print(f"  {csv_path}")
    print(f"  {json_path}")
    report(pages, segments)


if __name__ == "__main__":
    main()

# ─────────────────────────────────────────────────────────────────────────
# تحذيرٌ لمن يريد التوقيتات منسوبةً إلى ملفات السور (surah/*.mp3):
#
# ما يخرج من هنا منسوبٌ إلى ملفات الأوجه، لأن المحاذاة قِيست عليها. وردّه
# إلى ملف السورة يفترض أن ملف السورة هو أوجهُها موصولةً بترتيبها وبلا
# زيادةٍ ولا نقص — فيكون مبدأ الوجه هو مجموع مُدَد ما قبله من أوجه
# سورته. وهذا **لم يُتحقَّق منه**: قد يكون ملف السورة تسجيلًا آخر، أو
# فيه استعاذةٌ أو بسملةٌ أو صمتٌ ليس في ملفات الأوجه، فتزيح التوقيتات
# كلها.
#
# فقبل الاعتماد عليه: خُذ سورةً قصيرةً، واحسب مبدأ آيةٍ في وسطها بهذه
# الطريقة، ثم اسمع ملف السورة عند ذلك الموضع. إن وافق فالافتراض صحيح
# لبقيتها؛ وإن زاغ فالطريق الصحيح أن تُعاد المحاذاة على ملفات السور
# نفسها بـ tools/align_page.py بعد تبديل مصدرها.
