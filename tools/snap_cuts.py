#!/usr/bin/env python3
"""ينقل حدود الآيات إلى السكتة الحقيقية بينها.

المشكلة التي يعالجها
────────────────────
بدايات الآيات في ayah-timings.json مقيسةٌ بالمحاذاة القسرية: تفريغٌ
بـ faster-whisper ثم مطابقةٌ بالنصّ (tools/align_page.py). وما يخرج منها
تقديرٌ لموضع أول كلمة، خطؤه في حدود العُشر إلى ثلاثة أعشار الثانية.

وهذا القدر لا يُحَسّ في تطبيق المصحف: الرقم هناك يحرّك تظليلًا فحسب،
والصوت ملفُ وجهٍ واحدٍ متّصل لا يُقَصّ ولا يُعاد منه شيء.

لكنه يُسمَع حين يُقَصّ عليه: نهاية الآية تُؤخَذ بدايةَ التي تليها
بالضبط — ولا فاصل — فإن تأخّر التقديرُ عن النطق الحقيقيّ بقي في ذيل
الآية أوّلُ حرفٍ من التي بعدها. فإذا تُليت الآيتان متتابعتين سُمع ذلك
الحرف مرّتين. وأشدُّ ما يقع في حروف العطف وأوائل السور: الواو والفاء
خفيفتان قصيرتان، وهما أسوأ ما يقدّره whisper.

    ‹…إنّ ربَّك لسريعُ العقاب› ‹وَ› | ‹وَإنّه لغفورٌ رحيم›

العلاج
──────
الحدُّ الصحيح ليس تقديرَ whisper بل السكتةُ التي يقف فيها القارئ بين
الآيتين — وهي موجودة في الصوت نفسه، يكشفها ffmpeg. فيُمسح كلُّ وجهٍ
مرّةً واحدة، ويُنقل كلُّ حدٍّ إلى داخل أقرب سكتةٍ إليه:

    نهاية السابقة = مبدأ السكتة + ذيلٌ يسير
    بداية التالية = منتهى السكتة − تمهيدٌ يسير

فلا يبقى في ذيل الآية شيءٌ من التي بعدها، ولا يُقتطع من أوّلها حرف.
والحدُّ الذي لا تُوجَد حوله سكتةٌ يُترك كما هو ويُذكر في التقرير: تلك
وحدها ما يستحقّ السماع بالأذن.

    python3 tools/snap_cuts.py TIMINGS AUDIO_DIR -o snapped.json
    python3 tools/snap_cuts.py TIMINGS AUDIO_DIR -o snapped.json --report r.csv
    python3 tools/snap_cuts.py --selftest      # لا يحتاج صوتًا ولا ffmpeg

يحتاج ffmpeg:  brew install ffmpeg
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys

# عتبةُ ما يُعَدّ صمتًا. −35dB لا −50: التسجيل فيه أرضيةُ ضجيجٍ خفيفة،
# وعتبةٌ أشدّ صرامةً لا ترى السكتات القصيرة بين الآيات أصلًا.
NOISE_DB = "-35dB"
# أقصرُ سكتةٍ تُعتَدّ. الوقفة بين آيتين أطول من هذا بكثير عادةً؛ وما دونه
# سكتاتُ النطق داخل الكلمة نفسها (الشدّة والقلقلة) فلا تُعَدّ حدًّا.
MIN_SILENCE = 0.12
# أبعدُ ما يُبحَث عنه حول تقدير المحاذاة. خطأ المحاذاة أعشارُ ثانية،
# وثانيةٌ ونصف سعةٌ كافية؛ وما جاوزها فالأرجح أنه سكتةُ آيةٍ أخرى.
WINDOW = 1.5
# ما يُترك من السكتة لكلِّ جانب: ذيلٌ بعد الآية حتى لا تُبتَر نهايتُها،
# وتمهيدٌ قبل التي تليها حتى لا يُقتطع أولُ حرفٍ منها.
LEAD = 0.10
TAIL = 0.30

SILENCE_RE = re.compile(r"silence_(start|end):\s*(-?[\d.]+)")
DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d\d):(\d\d\.\d+)")


def scan(audio: str, noise: str, min_silence: float):
    """سكتاتُ الملف ومدّته من مسحةٍ واحدة.

    مسحةٌ واحدة لكل وجه لا لكل حدّ: ffmpeg يقرأ الملف كاملًا في الحالين،
    وستّ مئة قراءةٍ أرخص من ستّة آلاف. والمدّة تُؤخذ من هذه المسحة نفسها
    لا بـ ffprobe: بعض نسخ ffmpeg تُوزَّع بلا ffprobe، وكان غيابُه يُسقط
    الأداة كلها من أجل رقمٍ مطبوعٍ أمامنا أصلًا.

    يُرجِع (السكتات، المدّة أو None).
    """
    out = subprocess.run(
        ["ffmpeg", "-nostdin", "-i", audio, "-af",
         f"silencedetect=noise={noise}:d={min_silence}", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr

    spans: list[tuple[float, float]] = []
    start = None
    for kind, val in SILENCE_RE.findall(out):
        t = float(val)
        if kind == "start":
            start = t
        elif start is not None:
            spans.append((start, t))
            start = None

    total = None
    m = DURATION_RE.search(out)
    if m:
        h, mi, s = m.groups()
        total = int(h) * 3600 + int(mi) * 60 + float(s)
    # سكتةٌ مفتوحة في آخر الملف: ffmpeg لا يطبع لها منتهًى، ونهايتُها
    # نهايةُ الملف — وهي بالضبط الذيلُ الذي نريد تقليمه.
    if start is not None and total is not None:
        spans.append((start, total))
    return spans, total


def pick(t: float, spans: list[tuple[float, float]], window: float):
    """السكتةُ التي يقع فيها هذا الحدّ، أو أقربُها إليه داخل السعة.

    المحتوِية أولًا: إن وقع التقديرُ داخل سكتةٍ فهي المقصودة يقينًا ولا
    يُلتفَت إلى ما قد يكون أقربَ إلى مركزه من جيرانها.
    """
    for s0, s1 in spans:
        if s0 <= t <= s1:
            return (s0, s1)
    best = None
    for s0, s1 in spans:
        d = s0 - t if s0 > t else t - s1
        if d <= window and (best is None or d < best[0]):
            best = (d, (s0, s1))
    return best[1] if best else None


def snap(t: float, spans, window: float, lead: float, tail: float):
    """يُرجِع (نهايةُ السابقة، بدايةُ التالية، السكتةُ التي وُجدت).

    والقَدْران يُقلَّمان إلى خُمسَي السكتة كلٌّ منهما حين تضيق: بذلك
    تبقى بينهما فرجةٌ دائمًا مهما قصرت، فلا يُدرك أحدُ الملفّين الآخر.
    """
    span = pick(t, spans, window)
    if span is None:
        return t, t, None
    s0, s1 = span
    gap = s1 - s0
    return s0 + min(tail, gap * 0.4), s1 - min(lead, gap * 0.4), span


def selftest() -> int:
    """اختبارُ الحساب وحده — بسكتاتٍ مفروضة، بلا صوتٍ ولا ffmpeg."""
    fails = 0

    def check(name, got, want, tol=1e-6):
        nonlocal fails
        ok = all(abs(g - w) <= tol for g, w in zip(got[:2], want)) and len(got) >= 2
        print(f"  {'✓' if ok else '✗'} {name}: {got[:2]} {'' if ok else f'≠ {want}'}")
        if not ok:
            fails += 1

    # سكتةٌ واسعة: يُؤخَذ الذيلُ والتمهيدُ كاملين.
    spans = [(10.0, 11.0)]
    check("حدٌّ داخل سكتةٍ واسعة", snap(10.4, spans, WINDOW, LEAD, TAIL), (10.30, 10.90))
    # تقديرٌ متأخّرٌ عن السكتة — وهي حالةُ تكرار الحرف: يُسحَب إليها.
    check("تقديرٌ متأخّر", snap(11.6, spans, WINDOW, LEAD, TAIL), (10.30, 10.90))
    # تقديرٌ سابقٌ لها.
    check("تقديرٌ سابق", snap(9.2, spans, WINDOW, LEAD, TAIL), (10.30, 10.90))
    # سكتةٌ ضيّقة: يُقلَّم الطرفان ويبقى بينهما فرجة.
    narrow = snap(20.1, [(20.0, 20.2)], WINDOW, LEAD, TAIL)
    check("سكتةٌ ضيّقة", narrow, (20.08, 20.12))
    if narrow[0] >= narrow[1]:
        print("  ✗ الطرفان تداخلا في السكتة الضيّقة")
        fails += 1
    else:
        print("  ✓ الفرجة محفوظة في السكتة الضيّقة")
    # لا سكتةَ في السعة: يُترك الحدُّ ويُعلَّم.
    none = snap(50.0, spans, WINDOW, LEAD, TAIL)
    check("لا سكتة قريبة", none, (50.0, 50.0))
    if none[2] is not None:
        print("  ✗ ادّعى سكتةً لا وجود لها")
        fails += 1
    else:
        print("  ✓ أُعلن أنه بلا سكتة")
    # المحتوِية تسبق الأقرب مركزًا.
    two = snap(10.95, [(10.0, 11.0), (11.1, 12.0)], WINDOW, LEAD, TAIL)
    check("المحتوِية تسبق", two, (10.30, 10.90))

    print(f"\n{'كلّها سليمة' if not fails else f'{fails} إخفاق'}")
    return 1 if fails else 0


def guard_only(args) -> int:
    """علاجٌ مؤقّت بلا صوت: تُسحَب النهاية عن بداية التالية بقَدْرٍ ثابت.

    ليس هذا الصواب، وإنما هو أقلُّ خطأً مما كان. خطأ المحاذاة متأخّرٌ في
    الغالب — ولهذا يُسمَع الحرفُ مرّتين لا ينقص — فسحبُ النهاية قدرًا
    يسيرًا يُخرج أوّلَ الآية التالية من ذيل السابقة. وما يُدفَع ثمنًا
    أن تُقلَّم أواخرُ الآيات التي كانت محاذاتُها مضبوطة، وهي مدودٌ
    طويلة يُقتطع من آخرها أعشارُ ثانيةٍ لا تكاد تُسمَع.

    والصوابُ أن تُمسَح السكتات: هناك يُعرف موضعُ الحدّ ولا يُخمَّن.
    """
    with open(args.timings, encoding="utf-8") as f:
        doc = json.load(f)
    pages = {int(k): v for k, v in (doc.get("pages") or {}).items() if str(k).isdigit()}

    out_pages: dict[str, list[dict]] = {}
    guarded = tight = 0
    for page in sorted(pages):
        rows = [r for r in (pages[page] or [])
                if r.get("key") and r.get("start") is not None]
        made = []
        for i, r in enumerate(rows):
            start = float(r["start"])
            end = None
            if i + 1 < len(rows):
                nxt = float(rows[i + 1]["start"])
                end = nxt - args.guard
                # آيةٌ أقصرُ من الحاجز لا يُقتطع منها: تُترك كما كانت
                # ويُعدّ ذلك، فالقِصَرُ نفسه علامةُ محاذاةٍ مشكوكٍ فيها.
                if end <= start + 0.3:
                    end = nxt
                    tight += 1
                else:
                    guarded += 1
            made.append({"key": r["key"], "start": round(start, 3),
                         "end": None if end is None else round(end, 3)})
        out_pages[str(page)] = made

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({
            "note": (f"نهاياتٌ مسحوبةٌ عن بداية التالية بـ{args.guard}s — علاجٌ "
                     "مؤقّت بلا مسحِ صوت. الصواب tools/snap_cuts.py بالصوت."),
            "pages": out_pages,
        }, f, ensure_ascii=False)

    total = guarded + tight
    print(f"حدود عُولجت      : {total}")
    print(f"سُحبت {args.guard}s  : {guarded} ({100 * guarded / total:.1f}%)")
    print(f"تُركت لقِصَرها    : {tight} ({100 * tight / total:.1f}%) ← آياتٌ أقصر من الحاجز، تُراجَع")
    print(f"المخرجات في {args.out}")
    print("\nوهذا تخفيفٌ لا تصحيح: الحدُّ ما زال تقديرًا، وإنما أُبعد عن التالية.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("timings", nargs="?", help="ayah-timings.json")
    ap.add_argument("audio", nargs="?", help="مجلد ملفات الأوجه، فيه 1.mp3 … 604.mp3")
    ap.add_argument("-o", "--out", default="snapped-timings.json")
    ap.add_argument("--report", help="CSV بما نُقل وما لم تُوجَد له سكتة")
    ap.add_argument("--pages", help="أوجهٌ بعينها: 523-525 أو 1,5,9")
    ap.add_argument("--noise", default=NOISE_DB)
    ap.add_argument("--min-silence", type=float, default=MIN_SILENCE)
    ap.add_argument("--window", type=float, default=WINDOW)
    ap.add_argument("--lead", type=float, default=LEAD)
    ap.add_argument("--tail", type=float, default=TAIL)
    ap.add_argument("--selftest", action="store_true", help="اختبر الحساب ولا تمسح صوتًا")
    ap.add_argument("--guard", type=float, metavar="SECONDS",
                    help="بلا صوت: اجعل النهاية بدايةَ التالية ناقصَ هذا القدر")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.timings:
        ap.error("يلزم TIMINGS (أو --selftest)")
    if args.guard is not None:
        return guard_only(args)
    if not args.audio:
        ap.error("يلزم AUDIO_DIR (أو --guard للعلاج المؤقّت بلا صوت)")

    if subprocess.call(["which", "ffmpeg"], stdout=subprocess.DEVNULL) != 0:
        sys.exit("ffmpeg غير مثبَّت. جرّب: brew install ffmpeg")

    with open(args.timings, encoding="utf-8") as f:
        doc = json.load(f)
    pages = {int(k): v for k, v in (doc.get("pages") or {}).items() if str(k).isdigit()}

    if args.pages:
        want = set()
        for part in args.pages.split(","):
            if "-" in part:
                a, b = part.split("-")
                want.update(range(int(a), int(b) + 1))
            else:
                want.add(int(part))
        pages = {p: v for p, v in pages.items() if p in want}

    out_pages: dict[str, list[dict]] = {}
    report: list[dict] = []
    moved = unmoved = absent = 0
    shifts: list[float] = []

    for n, page in enumerate(sorted(pages), 1):
        rows = [r for r in (pages[page] or [])
                if r.get("key") and r.get("start") is not None]
        if not rows:
            continue
        audio = os.path.join(args.audio, f"{page}.mp3")
        if not os.path.exists(audio):
            absent += 1
            out_pages[str(page)] = [
                {"key": r["key"], "start": round(float(r["start"]), 3), "end": None}
                for r in rows
            ]
            continue

        spans, total = scan(audio, args.noise, args.min_silence)

        starts = [float(r["start"]) for r in rows]
        ends: list[float | None] = [None] * len(rows)

        # كلُّ حدٍّ داخليّ ينقل طرفين: نهايةَ ما قبله وبدايةَ ما بعده.
        for i in range(1, len(rows)):
            t = starts[i]
            prev_end, new_start, span = snap(t, spans, args.window, args.lead, args.tail)
            row = {
                "page": page, "boundary": f"{rows[i-1]['key']} ← {rows[i]['key']}",
                "aligned": round(t, 3),
            }
            if span is None:
                unmoved += 1
                row |= {"snapped_start": round(t, 3), "shift": 0.0,
                        "silence": "", "flag": "لا سكتة قريبة"}
            else:
                moved += 1
                shifts.append(new_start - t)
                ends[i - 1] = round(prev_end, 3)
                starts[i] = round(new_start, 3)
                row |= {"snapped_start": round(new_start, 3),
                        "shift": round(new_start - t, 3),
                        "silence": f"{span[0]:.2f}–{span[1]:.2f}", "flag": ""}
            report.append(row)

        # أولُ آيةٍ في الوجه: تُقرَّب إلى نهاية سكتة الصدر إن وُجدت،
        # فلا يبدأ ملفُّها بثوانٍ من الفراغ.
        if spans and spans[0][0] <= 0.05:
            starts[0] = round(max(0.0, spans[0][1] - args.lead), 3)
        # وآخرُها تنتهي بانتهاء الملف، إلا أن يكون ذيلُه صمتًا فيُقلَّم.
        if total is not None:
            ends[-1] = round(total, 3)
            if spans and spans[-1][1] >= total - 0.05:
                ends[-1] = round(min(total, spans[-1][0] + args.tail), 3)

        out_pages[str(page)] = [
            {"key": r["key"], "start": s, "end": e}
            for r, s, e in zip(rows, starts, ends)
        ]
        if n % 50 == 0:
            print(f"  … {n}/{len(pages)} وجهًا", flush=True)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({
            "note": ("بدايات الآيات ونهاياتها بعد نقل الحدود إلى السكتات — "
                     "انظر tools/snap_cuts.py. النهاية لم تعد بدايةَ التالية، "
                     "فبينهما فرجةٌ لا يُسمَع فيها حرفٌ مرّتين."),
            "pages": out_pages,
        }, f, ensure_ascii=False)

    total_b = moved + unmoved
    print(f"\nحدود عُولجت      : {total_b}")
    if total_b:
        print(f"نُقلت إلى سكتة   : {moved} ({100 * moved / total_b:.1f}%)")
        print(f"بلا سكتةٍ قريبة  : {unmoved} ({100 * unmoved / total_b:.1f}%) ← هذه وحدها تُسمَع بالأذن")
    if shifts:
        shifts.sort()
        mid = shifts[len(shifts) // 2]
        late = sum(1 for s in shifts if s < 0)
        print(f"وسيطُ الإزاحة    : {mid:+.3f}s")
        print(f"منها إلى الوراء  : {late} ({100 * late / len(shifts):.1f}%) — أي أن التقدير كان متأخّرًا")
    if absent:
        print(f"أوجهٌ غائبة عن القرص: {absent} — تُركت بلا نهايات")
    print(f"المخرجات في {args.out}")

    if args.report and report:
        with open(args.report, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(report[0]))
            w.writeheader()
            w.writerows(report)
        print(f"والتقرير في {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
