#!/usr/bin/env python3
"""ما يقوله تقريرُ snap_cuts حين يُقرأ جملةً.

التقريرُ سطرٌ لكلِّ حدّ، وفيه من الصفوف آلاف. وقراءتُه صفًّا صفًّا
تُري الشجرةَ وتُخفي الغابة: أنّ وجهًا بعينه لم تُصِب فيه الأداةُ إلا
سُبعَ حدوده بينما أصابت في جاره ثلاثةَ أخماسها ليس نقصًا في العتبة،
بل علامةٌ على أن تقديرات ذلك الوجه بعيدةٌ عن مواضعها. فمن لم يُوازِن
الأوجهَ بعضَها ببعض لم ير ذلك.

ويُفرَد الحدُّ بين سورتين بحسابٍ وحده. فالبسملةُ تقع فيه ولا تُعَدّ
آيةً في أكثر السور، فإن أخطأ الحدُّ ابتلعتها آخرُ آيةٍ من السورة
السابقة — فيُسمَع أولُ السورة مرّتين: مرّةً في ذيل ما قبلها ومرّةً
في موضعها. وتلك شكوى بعينها، فتُقاس بعينها.

    python3 tools/report_stats.py snap-report.csv
"""

import csv
import sys
from collections import defaultdict


def surah(key):
    """«52:1» → 52، وما لم يُفهَم فلا شيء."""
    try:
        return int(key.strip().split(":")[0])
    except (ValueError, IndexError):
        return None


def pct(part, whole):
    return 100.0 * part / whole if whole else 0.0


def quantile(sorted_vals, p):
    if not sorted_vals:
        return 0.0
    i = int(round(p * (len(sorted_vals) - 1)))
    return sorted_vals[i]


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)

    rows = []
    with open(argv[1], encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    if not rows:
        sys.exit("التقرير فارغ.")

    hit_by_page = defaultdict(lambda: [0, 0])   # وجه → [أصاب، الكل]
    cross = [0, 0]                              # حدود السور → [أصاب، الكل]
    cross_rows = []
    shifts = []

    for r in rows:
        page = int(r["page"])
        found = bool(r.get("silence"))
        hit_by_page[page][1] += 1
        if found:
            hit_by_page[page][0] += 1
            shifts.append(float(r["shift"]))

        # «51:60 ← 52:1»: السهمُ يفصل السابقةَ عن التالية.
        parts = r["boundary"].split("←")
        if len(parts) == 2:
            a, b = surah(parts[0]), surah(parts[1])
            if a is not None and b is not None and a != b:
                cross[1] += 1
                if found:
                    cross[0] += 1
                else:
                    cross_rows.append((page, r["boundary"].strip(),
                                       float(r["aligned"])))

    total = len(rows)
    hits = sum(v[0] for v in hit_by_page.values())

    print("حدودٌ في التقرير : %d على %d وجهًا" % (total, len(hit_by_page)))
    print("أصابت سكتةً      : %d (%.1f%%)" % (hits, pct(hits, total)))

    # الإزاحة: المئينات تقول ما لا يقوله الوسيط وحده — الذيلُ هو موضع
    # الخطأ الفادح، والوسيطُ يخفيه.
    shifts.sort()
    if shifts:
        print("\nالإزاحة (ثوانٍ) — المئينات:")
        for p, name in ((0.0, "الأدنى"), (0.1, "١٠٪"), (0.5, "الوسيط"),
                        (0.9, "٩٠٪"), (1.0, "الأقصى")):
            print("  %-8s %+.3f" % (name, quantile(shifts, p)))
        big = len([s for s in shifts if abs(s) >= 0.5])
        print("  إزاحةٌ تجاوزت نصفَ ثانية: %d (%.1f%%)"
              % (big, pct(big, len(shifts))))

    # الأوجهُ الضعيفة: نسبةُ إصابتها دون نصف المتوسّط العام. تلك التي
    # تحتاج محاذاةً جديدة لا عتبةً جديدة.
    avg = pct(hits, total)
    weak = [(pct(h, t), p, h, t) for p, (h, t) in hit_by_page.items()
            if t >= 5 and pct(h, t) < avg / 2]
    weak.sort()
    print("\nأوجهٌ إصابتُها دون نصف المتوسّط (%.1f%%): %d وجهًا"
          % (avg / 2, len(weak)))
    for rate, page, h, t in weak[:25]:
        print("  ص%-4d %2d/%-2d  %4.1f%%" % (page, h, t, rate))
    if len(weak) > 25:
        print("  … وبقيّتُها %d" % (len(weak) - 25))

    # وحدود السور: هذه التي تُسمَع فيها البسملة مرّتين إن أخطأت.
    print("\nحدودٌ بين سورتين : %d، أصاب منها %d (%.1f%%)"
          % (cross[1], cross[0], pct(cross[0], cross[1])))
    if cross_rows:
        print("والتي لم تُصِب — وهذه تُسمَع بالأذن قبل غيرها:")
        for page, b, t in cross_rows[:40]:
            print("  ص%-4d %-18s عند %.2fs" % (page, b, t))
        if len(cross_rows) > 40:
            print("  … وبقيّتُها %d" % (len(cross_rows) - 40))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
