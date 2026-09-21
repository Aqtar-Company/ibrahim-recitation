#!/usr/bin/env python3
"""يربط التوقيتات بالصوت الذي قيست عليه.

لماذا
────
`start: 102.48` جملةٌ عن ملفٍ بعينه: `khatma/42.mp3` كما هو اليوم. فإن
أُعيد رفعُ ذلك الملف — قُصّ من أوّله ثانية، أو أُعيد تسجيل آيةٍ فيه،
أو أُعيد ترميزُه بمعدّلٍ آخر — صارت كلُّ توقيتات الوجه كاذبة. ولا شيء
في هذا المستودع كان يكشف ذلك: الأرقام تبقى كما هي، والتطبيقات تظلّل
الآية الخطأ وتقصّ في وسط الكلمة، ولا أحد يعلم متى بدأ الخلل.

فيُسجَّل لكل وجهٍ أثرُه: حجمُه ببايتاته وبصمتُه. ومن أخذ هذه البيانات
يستطيع أن يتحقّق أن نسخته من الصوت هي التي قِيست، لا نسخةً أخرى تشبهها.

    # أثرُ ما عندك الآن
    python3 tools/fingerprint_audio.py make AUDIO_DIR -o data/audio-fingerprint.csv

    # هل تغيّر شيء؟
    python3 tools/fingerprint_audio.py verify data/audio-fingerprint.csv AUDIO_DIR

ولمن لا يملك الصوت على جهازه: يُصنَع الأثر على الخادم بلا تنزيل —
انظر آخر هذا الملف.
"""

import argparse
import csv
import hashlib
import os
import re
import subprocess
import sys
from typing import List, Optional, Tuple

# يُبدَّل بـ--ffmpeg؛ وغيابُه لا يُعطّل شيئًا: المُدَد وحدها تسقط.
FFMPEG = "ffmpeg"

FIELDS = ["page", "bytes", "sha256", "duration_ms"]
DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d\d):(\d\d\.\d+)")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        # يُقرأ على دفعات: ملفات الأوجه ستّة ميغابايت، والستّ مئة منها
        # ثلاثة غيغا ونصف، ولا تُحشر في الذاكرة دفعةً واحدة.
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def duration_ms(path: str) -> Optional[int]:
    """مدّةُ الملف بالملّي ثانية، أو None إن لم يكن ffmpeg موجودًا.

    ليست شرطًا: الحجمُ والبصمةُ يكفيان للكشف عن التغيّر، والمدّةُ تُقرأ
    بالعين فتقول ما الذي تغيّر — أطال الملفُّ أم قصر.
    """
    try:
        out = subprocess.run([FFMPEG, "-nostdin", "-i", path, "-f", "null", "-"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True).stderr
    except FileNotFoundError:
        return None
    m = DURATION_RE.search(out)
    if not m:
        return None
    h, mi, s = m.groups()
    return int(round((int(h) * 3600 + int(mi) * 60 + float(s)) * 1000))


def pages_in(folder: str) -> List[Tuple[int, str]]:
    out = []
    for name in os.listdir(folder):
        stem, ext = os.path.splitext(name)
        if ext.lower() == ".mp3" and stem.isdigit():
            out.append((int(stem), os.path.join(folder, name)))
    return sorted(out)


def make(args) -> int:
    found = pages_in(args.audio)
    if not found:
        sys.exit(f"لا ملفات أوجه في {args.audio} — يُنتظَر 1.mp3 … 604.mp3")

    rows = []
    no_ffmpeg = False
    for n, (page, path) in enumerate(found, 1):
        d = None if args.quick else duration_ms(path)
        if d is None and not args.quick:
            no_ffmpeg = True
        rows.append({
            "page": page,
            "bytes": os.path.getsize(path),
            "sha256": "" if args.quick else sha256(path),
            "duration_ms": "" if d is None else d,
        })
        if n % 50 == 0:
            print(f"  … {n}/{len(found)}", flush=True)

    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"\nأوجهٌ بُصمت : {len(rows)}")
    if args.quick:
        print("الوضع السريع: حجمٌ بلا بصمة — يكشف التغيير الغالب لا كلَّه.")
    elif no_ffmpeg:
        print("ffmpeg غير موجود، فالمُدَد فارغة. الحجم والبصمة كافيان للكشف.")
    print(f"المخرجات في {args.out}")
    return 0


def verify(args) -> int:
    with open(args.fingerprint, encoding="utf-8") as f:
        want = {int(r["page"]): r for r in csv.DictReader(f)}
    found = dict(pages_in(args.audio))

    changed, missing, extra, same = [], [], [], 0
    for page, row in sorted(want.items()):
        path = found.get(page)
        if path is None:
            missing.append(page)
            continue
        size = os.path.getsize(path)
        if str(size) != row["bytes"]:
            changed.append((page, f"الحجم {row['bytes']} ← {size}"))
            continue
        # البصمةُ تُحسَب فقط حين يتطابق الحجم: ملفٌّ اختلف حجمه اختلف
        # يقينًا، ولا معنى لقراءة ستّة ميغابايت لتأكيد ما عُرف.
        if row["sha256"]:
            got = sha256(path)
            if got != row["sha256"]:
                changed.append((page, f"البصمة {row['sha256'][:12]}… ← {got[:12]}…"))
                continue
        same += 1
    extra = sorted(set(found) - set(want))

    print(f"أوجهٌ مطابقة   : {same}")
    print(f"أوجهٌ تغيّرت   : {len(changed)}")
    for page, why in changed[:40]:
        print(f"   وجه {page:>3} — {why}")
    if len(changed) > 40:
        print(f"   … و{len(changed) - 40} غيرها")
    if missing:
        print(f"أوجهٌ غائبة    : {len(missing)} — {missing[:20]}")
    if extra:
        print(f"أوجهٌ زائدة    : {len(extra)} — {extra[:20]}")

    if changed:
        print("\nتوقيتاتُ هذه الأوجه لم تعد صالحة: الصوت الذي قِيست عليه ليس هذا.")
        print("تُعاد محاذاتُها — tools/align_page.py — ثم يُعاد نقلُ حدودها")
        print("بـtools/snap_cuts.py، ثم يُعاد توليد data/ بـexport_recitation.py،")
        print("ثم يُصنَع أثرٌ جديد بهذه الأداة.")
        return 1
    print("\nالصوتُ هو الذي قِيست عليه التوقيتات.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="""
صنعُ الأثر على الخادم بلا تنزيل — لا يحتاج بايثون ولا ffmpeg:

    ssh -p PORT USER@HOST 'cd ~/…/quran/khatma && \\
      { echo "page,bytes,sha256,duration_ms"; \\
        for f in *.mp3; do \\
          printf "%s,%s,%s,\\n" "${f%.mp3}" "$(stat -c%s "$f")" \\
                 "$(sha256sum "$f" | cut -d" " -f1)"; \\
        done; } | sort -t, -k1,1n' > data/audio-fingerprint.csv
""")
    sub = ap.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("make", help="اصنع أثر الصوت الحالي")
    m.add_argument("audio", help="مجلد ملفات الأوجه")
    m.add_argument("-o", "--out", default="data/audio-fingerprint.csv")
    m.add_argument("--ffmpeg", default="ffmpeg", help="مسارُ ffmpeg إن لم يكن في PATH")
    m.add_argument("--quick", action="store_true",
                   help="حجمٌ بلا بصمة — أسرع، وأضعفُ كشفًا")
    m.set_defaults(fn=make)

    v = sub.add_parser("verify", help="هل الصوت هو الذي قِيست عليه التوقيتات؟")
    v.add_argument("fingerprint", help="data/audio-fingerprint.csv")
    v.add_argument("audio", help="مجلد ملفات الأوجه")
    v.set_defaults(fn=verify)

    args = ap.parse_args()
    global FFMPEG
    FFMPEG = getattr(args, "ffmpeg", "ffmpeg")
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
