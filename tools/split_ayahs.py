#!/usr/bin/env python3
"""يقصّ تلاوة الأوجه إلى ملفٍ لكل آية — كما تُوزَّع تلاوات القرّاء.

تطبيقات المصحف تأخذ التلاوة ملفًا لكل آية. هكذا يُجلَب الحصري والعفاسي
في هذا التطبيق نفسه:

    https://cdn.islamic.network/quran/audio/128/ar.husary/{1..6236}.mp3

وعندنا ما يكفي لصنع مثلها: صوتُ الأوجه، ومبدأُ كل آية فيه. ونهايتُها
مبدأُ التي تليها في الوجه نفسه، وآخرُ آيةٍ في الوجه تنتهي بانتهاء ملفه.

ولا لصقَ ولا وصل: فُحصت بيانات الأوجه الـ604 فليس فيها آيةٌ لها كلماتٌ
في وجهين — أطولُها (2:282) تملأ وجهًا وحدها. فكل آيةٍ في ملفٍ واحد،
وقصُّها قصٌّ لا تركيب.

    python3 tools/split_ayahs.py TIMINGS AUDIO_DIR -o out/ --dry-run
    python3 tools/split_ayahs.py TIMINGS AUDIO_DIR -o out/

يحتاج ffmpeg:  brew install ffmpeg
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

# عدد آيات كل سورة، لحساب الترتيب العام للآية بين الـ6236.
VERSES = [
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52, 99, 128,
    111, 110, 98, 135, 112, 78, 118, 64, 77, 227, 93, 88, 69, 60, 34, 30, 73,
    54, 45, 83, 182, 88, 75, 85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60,
    49, 62, 55, 78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52,
    44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25, 22, 17, 19,
    26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11, 11, 8, 3, 9, 5, 4, 7, 3,
    6, 3, 5, 4, 5, 6,
]
TOTAL_AYAHS = 6236


def global_id(surah, ayah):
    return sum(VERSES[: surah - 1]) + ayah


def plan(timings_path):
    """خطّةُ القصّ: لكل آيةٍ ملفُها ومبدؤها ومدّتها.

    المدّة None تعني «إلى آخر الملف» — وهي آخرُ آيةٍ في كل وجه. ولا
    تُخمَّن: ffmpeg يقصّ إلى النهاية بلا أن يُقال له كم، فلا حاجة إلى
    معرفة المدّة أصلًا.
    """
    with open(timings_path, encoding="utf-8") as f:
        raw = json.load(f).get("pages") or {}
    pages = {int(k): v for k, v in raw.items() if str(k).isdigit()}

    cuts = []
    for page in sorted(pages):
        rows = [r for r in (pages[page] or [])
                if r.get("key") and r.get("start") is not None]
        for i, row in enumerate(rows):
            surah, ayah = (int(x) for x in row["key"].split(":"))
            start = float(row["start"])
            nxt = rows[i + 1]["start"] if i + 1 < len(rows) else None
            dur = None if nxt is None else round(float(nxt) - start, 3)
            # مدّةٌ صفرٌ أو سالبة علامةُ محاذاةٍ فاسدة، ولا تُقَصّ.
            if dur is not None and dur <= 0:
                print(f"::تحذير:: {surah}:{ayah} في الوجه {page} مدّتها {dur}s — تُخطّى",
                      file=sys.stderr)
                continue
            cuts.append({
                "surah": surah, "ayah": ayah, "page": page,
                "start": round(start, 3), "dur": dur,
            })
    cuts.sort(key=lambda c: (c["surah"], c["ayah"]))
    return cuts


def out_names(cut, naming):
    """المسارات المطلوبة لهذه الآية، نسبيّةً إلى مجلد الإخراج.

    التسميتان في مجلدين منفصلين حين تُطلبان معًا: خلطُهما يعطي مجلدًا
    فيه 001001.mp3 و1.mp3 لآيةٍ واحدة، فلا يُعرف أيُّ نظامٍ هو.
    """
    names = []
    if naming == "everyayah":
        names.append(f"{cut['surah']:03d}{cut['ayah']:03d}.mp3")
    elif naming == "global":
        names.append(f"{global_id(cut['surah'], cut['ayah'])}.mp3")
    else:
        names.append(os.path.join("by-ayah", f"{cut['surah']:03d}{cut['ayah']:03d}.mp3"))
        names.append(os.path.join("by-id", f"{global_id(cut['surah'], cut['ayah'])}.mp3"))
    return names


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("timings", help="ayah-timings.json")
    ap.add_argument("audio", help="مجلد ملفات الأوجه، فيه 1.mp3 … 604.mp3")
    ap.add_argument("-o", "--out", default="ayah-audio", help="مجلد الإخراج")
    ap.add_argument("--naming", choices=["everyayah", "global", "both"],
                    default="both",
                    help="everyayah: 001001.mp3 · global: 1.mp3 · both (الافتراضي)")
    ap.add_argument("--bitrate", default="128k")
    ap.add_argument("--dry-run", action="store_true",
                    help="اطبع الخطّة والنواقص ولا تقصّ شيئًا")
    args = ap.parse_args()

    cuts = plan(args.timings)
    have = {(c["surah"], c["ayah"]) for c in cuts}
    missing = [(s, a) for s in range(1, 115) for a in range(1, VERSES[s - 1] + 1)
               if (s, a) not in have]

    # ملفُ وجهٍ غائبٌ عن القرص يعني آياتٍ لا تُقَصّ وإن كانت موقَّتة.
    pages_needed = sorted({c["page"] for c in cuts})
    absent = [p for p in pages_needed if not os.path.exists(os.path.join(args.audio, f"{p}.mp3"))]

    print(f"آيات في الخطّة  : {len(cuts)} من {TOTAL_AYAHS}")
    print(f"آيات ناقصة      : {len(missing)}"
          + (f" — أولها {missing[0][0]}:{missing[0][1]}" if missing else ""))
    print(f"أوجه مطلوبة     : {len(pages_needed)}")
    if absent:
        print(f"أوجه غائبة عن القرص: {len(absent)} — {absent[:12]}"
              f"{'…' if len(absent) > 12 else ''}")
    open_end = sum(1 for c in cuts if c["dur"] is None)
    print(f"آيات تُقَصّ إلى آخر ملفّها: {open_end} (آخر آيةٍ في كل وجه)")

    if args.dry_run:
        print("\nعيّنة:")
        for c in cuts[:5]:
            names = " و".join(out_names(c, args.naming))
            d = "إلى النهاية" if c["dur"] is None else f"{c['dur']}s"
            print(f"  {c['surah']}:{c['ayah']:<3} ← {c['page']}.mp3 من {c['start']}s لمدّة {d} → {names}")
        return

    if subprocess.call(["which", "ffmpeg"], stdout=subprocess.DEVNULL) != 0:
        sys.exit("ffmpeg غير مثبَّت. جرّب: brew install ffmpeg")

    os.makedirs(args.out, exist_ok=True)
    done = failed = skipped = 0
    for i, c in enumerate(cuts, 1):
        src = os.path.join(args.audio, f"{c['page']}.mp3")
        if not os.path.exists(src):
            skipped += 1
            continue
        names = out_names(c, args.naming)
        first = os.path.join(args.out, names[0])
        os.makedirs(os.path.dirname(first) or args.out, exist_ok=True)
        # -ss قبل -i للسرعة، ومع إعادة الترميز يكون القصّ دقيقًا لا عند
        # إطارٍ سابق. و-t لا -to: الثاني يُحسَب من مبدأ الملف في بعض
        # الإصدارات ومن موضع القفز في غيرها، فتختلف النتيجة بالإصدار.
        cmd = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y",
               "-ss", str(c["start"]), "-i", src]
        if c["dur"] is not None:
            cmd += ["-t", str(c["dur"])]
        cmd += ["-vn", "-c:a", "libmp3lame", "-b:a", args.bitrate, first]
        if subprocess.call(cmd) != 0:
            print(f"::خطأ:: فشل قصّ {c['surah']}:{c['ayah']}", file=sys.stderr)
            failed += 1
            continue
        # الاسم الثاني وصلةٌ إلى الأول لا قصّةٌ ثانية: الملفّ واحد،
        # والاسمان تسميتان له. وإن منع نظامُ الملفات الوصل نُسخ.
        for extra in names[1:]:
            dst = os.path.join(args.out, extra)
            os.makedirs(os.path.dirname(dst) or args.out, exist_ok=True)
            if os.path.exists(dst):
                os.remove(dst)
            try:
                os.link(first, dst)
            except OSError:
                shutil.copyfile(first, dst)
        done += 1
        if i % 200 == 0:
            print(f"  … {i}/{len(cuts)}")

    print(f"\nتمّ {done} · فشل {failed} · تُخطّي {skipped} (وجهٌ غائب عن القرص)")
    print(f"المخرجات في {args.out}")


if __name__ == "__main__":
    main()
