#!/usr/bin/env bash
# ينشر البيانات من المستودع إلى الخادم، ويجدّد الفهرس هناك.
#
# الاتجاه واحد: المستودع ← الخادم. تُعدَّل البيانات هنا، ثم تُدفَع،
# ثم يُنشَر بهذا. ولا يُعدَّل شيءٌ على الخادم باليد — نسختان تُعدَّلان
# لا يُعرَف أيّهما الصواب، ومن عدّل على الخادم فقد عدّل بلا تاريخٍ ولا
# رجعة، وأولُ رفعةٍ بعدها تمحو ما عمل.
#
# والفهرس يُبنى على الخادم لا هنا: بصماتُ الصوت لا تُعرَف إلا حيث
# الصوت، وهو هناك.
#
# لا عناوين ولا أسماء في هذا الملف — المستودع علنيّ. تُقرأ من البيئة:
#
#     export IBQ_HOST=… IBQ_USER=… IBQ_PORT=… IBQ_QURAN_DIR=…
#     tools/publish.sh            # انشر
#     tools/publish.sh --check    # قارِن المنشور بما هنا ولا ترفع شيئًا
#
# ويُحسن أن تُوضَع في ~/.ibq.env ثم:  source ~/.ibq.env

set -euo pipefail

: "${IBQ_HOST:?ضع IBQ_HOST — عنوان الخادم}"
: "${IBQ_USER:?ضع IBQ_USER — اسم المستخدم}"
IBQ_PORT="${IBQ_PORT:-22}"
: "${IBQ_QURAN_DIR:?ضع IBQ_QURAN_DIR — مسار مجلد الصوت على الخادم}"
IBQ_SITE="${IBQ_SITE:-https://ibrahimquran.com/quran}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "$ROOT/VERSION")"
SSH=(ssh -p "$IBQ_PORT" "$IBQ_USER@$IBQ_HOST")

live_version() {
  curl -fsS --max-time 20 "$IBQ_SITE/manifest.json" 2>/dev/null \
    | sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1
}

if [[ "${1:-}" == "--check" ]]; then
  live="$(live_version || true)"
  echo "في المستودع : $VERSION"
  echo "على الخادم  : ${live:-(لا فهرس بعد)}"
  if [[ -z "$live" ]]; then
    echo "→ لم يُنشَر فهرسٌ قطّ. شغّل الأمر بلا --check."
  elif [[ "$live" == "$VERSION" ]]; then
    echo "→ متطابقان."
  else
    echo "→ مختلفان: ما عند الناس ليس ما هنا. انشر."
  fi
  exit 0
fi

# الرفعُ أولًا ثم بناءُ الفهرس: الفهرس يحمل رقم النسخة ويشير إلى
# البيانات، فلو بُني قبلها لأشار إلى ما لم يصل بعد — ولوجد من قرأه
# فهرسًا جديدًا وبياناتٍ قديمة، وهو أسوأ من ألّا يُنشَر شيء.
echo "→ يُرفَع data/ ونسخته $VERSION"
scp -P "$IBQ_PORT" -q -r "$ROOT/data" "$IBQ_USER@$IBQ_HOST:$IBQ_QURAN_DIR/"

echo "→ تُرفَع الأدوات وإعداداتُ الذاكرة"
scp -P "$IBQ_PORT" -q \
  "$ROOT/tools/build_manifest.py" \
  "$ROOT/tools/fingerprint_audio.py" \
  "$ROOT/tools/snap_cuts.py" \
  "$ROOT/tools/export_recitation.py" \
  "$ROOT/server/.htaccess" \
  "$IBQ_USER@$IBQ_HOST:$IBQ_QURAN_DIR/"

echo "→ يُبنى الفهرس حيث الصوت"
"${SSH[@]}" "cd '$IBQ_QURAN_DIR' && python3 build_manifest.py . \
    -o manifest.json --version '$VERSION' --base '$IBQ_SITE/'"

echo "→ يُتحقَّق من المنشور"
live="$(live_version || true)"
if [[ "$live" == "$VERSION" ]]; then
  echo "تمّ. الفهرس الحيّ على $VERSION — ومن يقرؤه يأخذ الجديد."
else
  echo "::تحذير:: الفهرس يقول '${live:-لا شيء}' والمنتظَر '$VERSION'."
  echo "غالبًا ذاكرةٌ وسيطة. جرّب: curl -sI $IBQ_SITE/manifest.json | grep -i cache"
  exit 1
fi
