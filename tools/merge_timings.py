#!/usr/bin/env python3
"""يدمج نسختين من التوقيتات ويقول ما اختلفتا فيه.

لماذا
────
التوقيتات تُولَّد في أكثر من مكان: وظيفةٌ آليّة تُحاذي الأوجه وتودِعها،
ونسخةٌ تُنشَر على الخادم، ونسخةٌ في المستودع. فتفترقان: وُجد في الخادم
597 وجهًا وفي المستودع 535 — اثنان وستّون وجهًا حوذيت ولم تصل إلى هنا.

والكتابةُ فوق إحداهما بالأخرى تُتلف: الأكبرُ عددًا ليس بالضرورة
مُتضمِّنًا للأصغر، وقد يكون في الأصغر وجهٌ ليس في الأكبر — فيضيع بلا
أن يعلم أحد. فيُدمَجان، ويُقال صريحًا ما في كلٍّ منهما دون الآخر.

    python3 tools/merge_timings.py A.json B.json -o merged.json
    python3 tools/merge_timings.py A.json B.json --report   # لا يكتب شيئًا

عند اختلاف وجهٍ بين النسختين تُؤخَذ ذاتُ الآيات الأكثر — المحاذاة تزيد
ولا تنقص — ويُذكَر كل وجهٍ وقع فيه ذلك.
"""

import argparse
import json
import sys
from typing import Dict, List


def load(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    pages = d.get("pages") or {}
    return {str(k): v for k, v in pages.items() if str(k).isdigit()}, d


def ayah_keys(rows):
    return [r.get("key") for r in (rows or []) if r.get("key")]


def out_of_order(rows):
    """أوجهٌ ترتيبُ بداياتها غير تصاعديّ — علامةُ محاذاةٍ فاسدة."""
    starts = [r["start"] for r in (rows or [])
              if r.get("start") is not None]
    return any(b < a for a, b in zip(starts, starts[1:]))


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a", help="النسخة الأولى")
    ap.add_argument("b", help="النسخة الثانية")
    ap.add_argument("-o", "--out", help="أين يُكتَب المدموج")
    ap.add_argument("--report", action="store_true", help="اطبع الفروق ولا تكتب")
    args = ap.parse_args()

    A, doc_a = load(args.a)
    B, _ = load(args.b)

    only_a = sorted(set(A) - set(B), key=int)
    only_b = sorted(set(B) - set(A), key=int)
    both = sorted(set(A) & set(B), key=int)

    same, differ = [], []
    for p in both:
        (same if ayah_keys(A[p]) == ayah_keys(B[p]) and A[p] == B[p]
         else differ).append(p)

    print("الأولى  %s : %d وجهًا، %d آية"
          % (args.a, len(A), sum(len(v or []) for v in A.values())))
    print("الثانية %s : %d وجهًا، %d آية"
          % (args.b, len(B), sum(len(v or []) for v in B.values())))
    print("")
    print("في الأولى وحدها : %d %s" % (len(only_a), only_a[:15]))
    print("في الثانية وحدها: %d %s" % (len(only_b), only_b[:15]))
    print("في الاثنتين     : %d — متطابقة %d، مختلفة %d"
          % (len(both), len(same), len(differ)))
    if differ:
        print("  أوجهٌ مختلفة: %s%s" % (differ[:15], "…" if len(differ) > 15 else ""))
        for p in differ[:10]:
            print("    وجه %s: الأولى %d آية، الثانية %d آية"
                  % (p, len(A[p] or []), len(B[p] or [])))

    merged: Dict[str, List[dict]] = {}
    took_a = took_b = 0
    for p in sorted(set(A) | set(B), key=int):
        if p in A and p in B:
            # الأكثرُ آياتٍ أولى: المحاذاةُ تزيد ولا تنقص، والأقلُّ
            # غالبًا نسخةٌ حوذيت قبل أن يُصلَح ما أُسيء سماعُه فيها.
            if len(B[p] or []) > len(A[p] or []):
                merged[p] = B[p]; took_b += 1
            else:
                merged[p] = A[p]; took_a += 1
        elif p in A:
            merged[p] = A[p]; took_a += 1
        else:
            merged[p] = B[p]; took_b += 1

    bad = [p for p, rows in merged.items() if out_of_order(rows)]
    print("")
    print("المدموج : %d وجهًا، %d آية"
          % (len(merged), sum(len(v or []) for v in merged.values())))
    print("  من الأولى %d، من الثانية %d" % (took_a, took_b))
    print("أوجهٌ ترتيبُها مختلّ : %d%s"
          % (len(bad), (" — %s" % sorted(bad, key=int)[:15]) if bad else ""))

    if args.report:
        return 0
    if not args.out:
        sys.exit("يلزم -o، أو استعمل --report")

    doc_a["pages"] = merged
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(doc_a, f, ensure_ascii=False)
    print("كُتب في %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
