#!/usr/bin/env python3
"""يبني فهرسًا حيًّا يجعل تعديل الصوت يصل إلى كل من يستعمله.

المشكلة
───────
من أخذ `segments.csv` ونسخه في تطبيقه بقي على نسخته أبدًا: git لا يدفع
إلى أحد. ومن شغّل الصوت من روابطك بلا فهرسٍ وقع في أسوأ منها — إن عدّلتَ
`khatma/42.mp3` بقي في متصفّحه القديمُ محفوظًا (الرابط لم يتغيّر فلا سبب
لإعادة جلبه)، وإن جلبه فتوقيتاتُه المنسوخة عنده صارت تصف صوتًا آخر:
تظليلٌ على الآية الخطأ وقصٌّ في وسط الكلمة، ولا شيء يُنذر.

العلاج
──────
ملفٌّ واحدٌ على خادمك يقرؤه كلُّ تطبيقٍ عند إقلاعه، وفيه:

  • رابطُ الصوت ومعه **رقمُ مراجعته** — وهو بصمةُ الملف نفسه، فيتغيّر
    وحده إن تغيّر الملف ولا يُبنى على تذكّرك أن ترفع رقمًا. والرابطُ
    يحمله (`?v=…`)، فالمتصفّح يراه رابطًا جديدًا ويجلبه، ويبقى القديمُ
    محفوظًا سنةً بلا ضرر.
  • رابطُ التوقيتات ونسختُها.

فيتحرّك الصوتُ وما يصفه معًا: من قرأ الفهرس أخذ الاثنين أو لم يأخذ
واحدًا منهما.

    python3 tools/build_manifest.py AUDIO_ROOT -o manifest.json
    python3 tools/build_manifest.py AUDIO_ROOT -o manifest.json \\
            --base https://ibrahimquran.com/quran/ --version 1.1.0

AUDIO_ROOT هو المجلد الذي فيه khatma/ وsurah/ وpages/.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import Optional

# طولُ البصمة في الرابط. ثمانيةُ أرقامٍ ستّة عشرية = أربعة مليارات
# احتمال؛ واحتمالُ أن يتغيّر ملفٌّ فتبقى بصمتُه كما هي مهمَلٌ عمليًّا،
# وبصمةٌ كاملةٌ في الرابط تُثقله بلا فائدة.
REV_LEN = 8
DEFAULT_BASE = "https://ibrahimquran.com/quran/"


def revision(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:REV_LEN]


def entry(root: str, rel: str) -> dict:
    full = os.path.join(root, rel)
    return {
        "file": rel.replace(os.sep, "/"),
        "v": revision(full),
        "bytes": os.path.getsize(full),
    }


def scan_numbered(root: str, folder: str) -> dict:
    """khatma/ وsurah/: الاسم رقمٌ أو يبدأ برقم."""
    d = os.path.join(root, folder)
    if not os.path.isdir(d):
        return {}
    out = {}
    for name in sorted(os.listdir(d)):
        stem, ext = os.path.splitext(name)
        if ext.lower() != ".mp3":
            continue
        m = re.match(r"^(\d+)", stem)
        if not m:
            continue
        out[m.group(1)] = entry(root, os.path.join(folder, name))
    return out


def scan_pages(root: str) -> dict:
    """pages/: «{سورة} Page {رقم داخل السورة}.mp3» — المفتاح "سورة:صفحة"."""
    d = os.path.join(root, "pages")
    if not os.path.isdir(d):
        return {}
    out = {}
    for name in sorted(os.listdir(d)):
        stem, ext = os.path.splitext(name)
        if ext.lower() != ".mp3":
            continue
        m = re.match(r"^(\d+)\s+Page\s+(\d+)$", stem, re.I)
        if not m:
            continue
        out[f"{int(m.group(1))}:{int(m.group(2))}"] = entry(root, os.path.join("pages", name))
    return out


def read_version(explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "VERSION")
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip() or "0"
    except OSError:
        return "0"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio", help="المجلد الذي فيه khatma/ وsurah/ وpages/")
    ap.add_argument("-o", "--out", default="manifest.json")
    ap.add_argument("--base", default=DEFAULT_BASE, help="جذرُ روابط الصوت")
    ap.add_argument("--version", help="نسخةُ البيانات (الافتراضي: ملف VERSION)")
    ap.add_argument("--data-base", help="جذرُ روابط البيانات (الافتراضي: --base + 'data/')")
    args = ap.parse_args()

    if not os.path.isdir(args.audio):
        sys.exit(f"ليس مجلدًا: {args.audio}")

    base = args.base if args.base.endswith("/") else args.base + "/"
    data_base = args.data_base or (base + "data/")
    if not data_base.endswith("/"):
        data_base += "/"
    version = read_version(args.version)

    khatma = scan_numbered(args.audio, "khatma")
    surah = scan_numbered(args.audio, "surah")
    pages = scan_pages(args.audio)
    if not (khatma or surah or pages):
        sys.exit(f"لا ملفات صوت تحت {args.audio} — يُنتظَر khatma/ أو surah/ أو pages/")

    manifest = {
        "manifest_version": 1,
        "version": version,
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reciter": {"ar": "د. إبراهيم حسن", "en": "Dr. Ibrahim Hassan"},
        "mushaf": "Madani (Hafs)",
        "base": base,
        # التوقيتات تُجلَب من هنا لا من نسخةٍ محفوظةٍ في التطبيق: هي
        # وما تصفه يتحرّكان معًا، فمن أخذ أحدهما أخذ الآخر.
        "data": {
            "timings": f"{data_base}ayah-timings.json?v={version}",
            "segments": f"{data_base}segments.json?v={version}",
            "fingerprint": f"{data_base}audio-fingerprint.csv?v={version}",
        },
        "url_rule": "base + file + '?v=' + v",
        "notice": ("ابنِ روابط الصوت من هذا الفهرس دائمًا ولا تؤلّفها بنفسك: "
                   "`v` بصمةُ الملف، فإن عُدّل تغيّر الرابط وجلبه المتصفّح "
                   "من جديد. واجلب هذا الفهرس بـno-cache."),
        "khatma": khatma,
        "surah": surah,
        "pages": pages,
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    print(f"النسخة     : {version}")
    print(f"الجذر      : {base}")
    print(f"أوجه       : {len(khatma)}")
    print(f"سور        : {len(surah)}")
    print(f"صفحات سور  : {len(pages)}")
    print(f"المخرجات في {args.out}")
    if khatma:
        k = next(iter(khatma))
        e = khatma[k]
        print(f"\nمثال: {base}{e['file']}?v={e['v']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
