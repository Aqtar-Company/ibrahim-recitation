# تلاوة د. إبراهيم حسن — توقيتات الآيات

بيانات وأدوات لدمج هذه التلاوة في تطبيق مصحف: متى تبدأ كل آية ومتى تنتهي،
وأداةٌ تقصّ التلاوة ملفًا لكل آية كما تُوزَّع تلاوات القرّاء.

**الصوت ليس هنا.** هو على خادم ibrahimquran.com، وحجمه بالغيغابايت. هنا
ما يصفه: التوقيتات، والأدوات، وتقرير ما يُغطّى منه وما لا يُغطّى.

```
الصوت    https://ibrahimquran.com/quran/khatma/{1..604}.mp3   ← وجهًا وجهًا
         https://ibrahimquran.com/quran/surah/{1..114}.mp3    ← سورةً سورة
هذا المستودع   التوقيتات والأدوات والتوثيق — ولا ميغابايت صوتٍ واحد
```

النسخة الحالية في [`VERSION`](VERSION)، وما تغيّر في [`CHANGELOG.md`](CHANGELOG.md).

---

## ما في هذا المستودع

| المسار | ما هو |
|---|---|
| `data/ayah-timings.json` | مبدأ كل آية داخل ملف وجهها، بالثواني |
| `data/segments.csv` | المقاطع مبسوطةً: سورة، آية، وجه، ملف، مبدأ ونهاية بالملّي ثانية |
| `data/segments.json` | المقاطع نفسها بصيغة JSON، ومعها وصفُ المصدر |
| `tools/export_recitation.py` | يولّد `segments.*` من التوقيتات، ويطبع تقرير التغطية |
| `tools/split_ayahs.py` | يقصّ ملفات الأوجه إلى ملفٍ لكل آية |
| `tools/snap_cuts.py` | **ينقل حدود الآيات إلى السكتة الحقيقية بينها — شغّله قبل القصّ** |
| `tools/fingerprint_audio.py` | يربط التوقيتات بالصوت الذي قيست عليه، فيُكشَف تعديلُه |
| `tools/build_manifest.py` | **يبني الفهرس الحيّ الذي يجعل تحسين الصوت يصل إلى الجميع** |
| `server/.htaccess` | إعداداتُ الذاكرة على الخادم — بدونها لا يصل التحسين |
| `CHANGELOG.md` · `VERSION` | ما تغيّر، وأيّ نسخةٍ هذه |
| `tools/publish.sh` | ينشر البيانات إلى الخادم ويجدّد الفهرس — بأمرٍ واحد |
| `tools/merge_timings.py` | يدمج نسختَي توقيتات ويقول ما في كلٍّ دون الأخرى |
| `LICENSE` | CC BY 4.0 للتلاوة والبيانات، وMIT للأدوات |
| `data/page-map.csv` | خريطة الوجه ↔ السورة ↔ اسما ملفه في التنظيمين |
| `COVERAGE.txt` | التغطية وقت آخر توليد |
| `MISSING.md` | ما ينقص، وأين يُوجَد بديلُه |
| `INTEGRATION.md` | **ابدأ هنا لو كنت تدمج هذه التلاوة في تطبيقك** |
| `PROMPT.md` | موجز المشروع كاملًا: ما تُحقِّق منه، وما لم يُتحقَّق، وما بقي |

## كيف نُسِّق الصوت

التلاوة مسجّلةٌ **وجهًا وجهًا** — ملفٌ لكل صفحة من صفحات المصحف الـ604:

```
khatma/1.mp3 … khatma/604.mp3
```

ومرفوعةٌ كذلك سورًا كاملة (114 ملفًا) وأوجهًا داخل سورها (668 ملفًا) —
وهي ثلاثةُ تنظيماتٍ لصوتٍ واحد، فما غاب عن واحدٍ يُؤخَذ من آخر. لكن
**التوقيتات هنا مقيسةٌ على ملفات الأوجه وحدها** (`khatma/*.mp3`)، لأنها هي
التي حوذيت. انظر التحذير في آخر `tools/export_recitation.py` قبل ردّها إلى
ملفات السور.

## شكل التوقيتات

```json
{
  "pages": {
    "1": [
      { "key": "1:1", "start": 4.42 },
      { "key": "1:2", "start": 8.62 }
    ]
  }
}
```

`start` بالثواني من مبدأ `khatma/{page}.mp3`. وآخرُ آيةٍ في الوجه تنتهي
بانتهاء ملفه.

> ⚠️ **لا تجعل نهاية الآية مبدأَ التي تليها.** كانت هذه هي القاعدة المكتوبة
> هنا، وهي التي أوقعت أوّل من دمج هذه التلاوة في **تكرار أوّل حرفٍ من الآية
> مرّتين** — وأظهرُ ما يكون في الواو والفاء وأوائل السور. اقرأ
> [«حدود الآيات»](INTEGRATION.md#حدود-الآيات--اقرأ-هذا-قبل-أن-تقصّ) قبل أن
> تقصّ شيئًا.

## حقيقةٌ تُيسّر الدمج

**لا آية واحدة تمتدّ عبر وجهين.** فُحصت بيانات الأوجه الـ604 كلها: ليس فيها
آيةٌ لها كلماتٌ في صفحتين — وأطولُها (البقرة 282) تملأ الوجه 48 وحدها.

فكل آيةٍ موجودةٌ بتمامها داخل ملفٍ واحد، واستخراجُها **قصٌّ لا تركيب**. وهذا
ما يجعل `split_ayahs.py` بضعةَ أسطر لا محرّكَ وصلٍ ولصق.

## ملفٌ لكل آية

```bash
brew install ffmpeg          # أو: apt install ffmpeg

# اجلب ملفات الأوجه
rsync -avz -e "ssh -p PORT" \
  USER@HOST:~/domains/ibrahimquran.com/public_html/quran/khatma/ ./khatma/

# اطّلع على الخطّة أولًا
python3 tools/split_ayahs.py data/ayah-timings.json ./khatma --dry-run

# ثم نفّذ
python3 tools/split_ayahs.py data/ayah-timings.json ./khatma -o ./ayah-audio
```

يُخرج التسميتين الشائعتين في مجلدين منفصلين:

```
ayah-audio/by-ayah/001001.mp3    كما تنشرها everyayah
ayah-audio/by-id/1.mp3           بالترتيب بين الـ6236، كما تفعل islamic.network
```

الاسم الثاني وصلةٌ صلبة إلى الأول، لا ترميزٌ ثانٍ.

## ما يسكن أين، ومن أين يُعدَّل

| | مكانُه | لماذا |
|---|---|---|
| **الصوت** (٣.٦ غيغا) | الخادم وحده | git يحفظ كل نسخةٍ إلى الأبد ولا يَنسى، فإعادةُ رفع خمسين وجهًا تزيد المستودع بها ولا تُنقصه أبدًا. وGitHub يحذّر فوق غيغا. وأهمُّ منهما: القفزُ إلى آيةٍ في وسط وجهٍ يطلب مدًى من الملف (`Range`)، وليس هذا ما تُصنَع له مستودعاتُ الكود |
| **التوقيتات والأدوات** | المستودع هو الأصل | هنا التاريخ: يُرى ما تغيّر ومتى، ويُرجَع عمّا أفسد. ويُنسَخ منه إلى الخادم |
| **الفهرس** `manifest.json` | يُبنى على الخادم | فيه بصماتُ ملفات الصوت، ولا تُعرَف إلا حيث الصوت |

**والاتجاه واحد: المستودع ← الخادم.** تُعدَّل البيانات هنا، وتُدفَع، ثم
تُنشَر. ولا يُعدَّل شيءٌ على الخادم باليد: من فعل فقد عدّل بلا تاريخٍ ولا
رجعة، وأوّلُ نشرةٍ بعده تمحو ما عمل — ثم لا يُعرَف أيُّ النسختين الصواب.

والصوتُ وحده يُرفَع إلى الخادم مباشرةً، فهو ليس هنا أصلًا. وبعد رفعه
يُنشَر لتُحسَب بصمتُه من جديد، وإلا لم يعلم به أحد.

```bash
export IBQ_HOST=… IBQ_USER=… IBQ_PORT=… IBQ_QURAN_DIR=…

tools/publish.sh --check   # أعلى الناس ما عندي أم أقدم؟
tools/publish.sh           # ارفع البيانات وجدّد الفهرس
```

`--check` يقارن نسخةَ المستودع بالفهرس الحيّ فيقول أنشرتَ آخر ما عندك
أم لا. ولا عنوانَ ولا اسمَ مستخدمٍ في هذا المستودع — تُقرأ من البيئة.

## ما تحتاجه الأدوات

| الأداة | بايثون | ffmpeg |
|---|---|---|
| `build_manifest.py` · `export_recitation.py` · `fingerprint_audio.py` | **3.6+** | لا يحتاج |
| `snap_cuts.py` · `split_ayahs.py` | **3.6+** | **نعم** |

3.6 عمدًا: هذه الأدوات تُشغَّل على الخادم الذي عليه الصوت، والاستضافةُ
المشتركة تبقى على بايثون قديم — و3.6 هو ما وجدناه على خادم هذه التلاوة.

**ولا ffmpeg على الاستضافة المشتركة ولا صلاحيةَ تنصيبه.** وليس ذلك مانعًا:
يُنزَّل بناءٌ ساكن في منزلك ويُشار إليه:

```bash
mkdir -p ~/bin && cd ~/bin
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
  | tar xJ --strip-components=1 --wildcards '*/ffmpeg'
chmod +x ffmpeg && ./ffmpeg -version | head -1

python3 snap_cuts.py data/ayah-timings.json khatma --ffmpeg ~/bin/ffmpeg -o out.json
```

فتُمسَح السكتاتُ حيث الصوتُ نفسه، ولا يُنزَّل منه ميغابايت واحد.

## الفهرس الحيّ — كيف يصل تحسينُ الصوت إلى الجميع

**اقرأ هذا الفهرس، ولا تؤلّف روابط الصوت بنفسك:**

```
https://ibrahimquran.com/quran/manifest.json
```

هو المصدرُ الحيّ. التلاوةُ تُحسَّن — تُعاد آيةٌ، يُصلَح وجه — ومن ألّف
الروابط بنفسه أو نسخ `data/` في تطبيقه يبقى على القديم ولا يدري. ومن
قرأ الفهرس يأخذ الجديد وحده.

```json
{
  "version": "1.1.0",
  "base": "https://ibrahimquran.com/quran/",
  "url_rule": "base + file + '?v=' + v",
  "data": { "timings": "…/data/ayah-timings.json?v=1.1.0", "segments": "…" },
  "khatma": { "42": { "file": "khatma/42.mp3", "v": "84e10d7a", "bytes": 6203441 } }
}
```

`v` **بصمةُ الملف نفسه** لا رقمٌ يُرفَع باليد. فإن عُدِّل وجهٌ تغيّرت
بصمتُه وحده:

```
وجه 41:  84e10d7a → 84e10d7a   كما هو ← يبقى محفوظًا في المتصفّح، لا جلب
وجه 42:  84e10d7a → fc4aefe1   تغيّر  ← رابطٌ جديد، يُجلَب من فوره
```

فلا يُحتاج إلى إبطال ذاكرةٍ ولا إلى انتظار انتهاء مدّة: الرابط الجديد
رابطٌ لم يُرَ قطّ. والقديم يبقى محفوظًا سنةً بلا ضرر — فلذلك يصحّ أن
يُخزَّن الصوت إلى الأبد.

**وينتقل الصوتُ مع ما يصفه.** `data.timings` في الفهرس نفسه وعليه رقم
النسخة، فمن قرأ الفهرس أخذ الصوتَ الجديد وتوقيتاتِه معًا — ولا يقع أن
يُشغَّل وجهٌ أُعيد تسجيله بتوقيتاتٍ تصف تسجيلَه القديم.

```ts
const m = await fetch('https://ibrahimquran.com/quran/manifest.json',
                      { cache: 'no-cache' }).then(r => r.json());

const page = m.khatma['42'];
const url = m.base + encodeURI(page.file) + '?v=' + page.v;

const timings = await fetch(m.data.timings).then(r => r.json());
```

> اجلب `manifest.json` بـ`no-cache`، وكلَّ ما عداه كما هو: روابطُه
> محمولةٌ على بصماتها فلا تكذب.

### وإن أردتَ نسخةً ثابتةً لا تتحرّك

من لا يريد أن يتغيّر تحته شيء يأخذ من وسمٍ مثبَّت:

```
https://cdn.jsdelivr.net/gh/Aqtar-Company/ibrahim-recitation@v1.1.0/data/segments.json
```

وهو يعرف حينئذٍ أنه لا يصله تحسين. و`version` مكتوبٌ داخل
`segments.json` نفسه ليُقارَن بالفهرس الحيّ فيُعرَف متى يُجدَّد.

### ما لا يصل من نفسه

git لا يدفع إلى أحد؛ الناس يسحبون. فمن نسخ `data/` في تطبيقه في يناير
يبقى على نسخة يناير — والفهرسُ الحيّ هو الخروج من ذلك.

## لو عدّلتَ الصوت

`start: 102.48` جملةٌ عن **ملفٍ بعينه كما هو اليوم**. فإن أُعيد رفعُ
`khatma/42.mp3` — قُصّ من أوّله ثانية، أو أُعيدت آيةٌ فيه، أو أُعيد
ترميزه — صارت كلُّ توقيتات ذلك الوجه كاذبة، وظلّلت التطبيقاتُ الآيةَ
الخطأ وقصّت في وسط الكلمة. ولا شيء في الأرقام يُظهر ذلك.

فلكل وجهٍ هنا أثرُه في [`data/audio-fingerprint.csv`](data/audio-fingerprint.csv):

```bash
python3 tools/fingerprint_audio.py verify data/audio-fingerprint.csv ./khatma
```

يقول لك أيُّ الأوجه تغيّر صوتها، ويخرج برمزٍ غير صفر — فيصلح شرطًا في CI.
وإن تغيّر وجه، فدورةُ إصلاحه:

```
align_page.py  →  snap_cuts.py  →  export_recitation.py  →  fingerprint_audio.py make
   أعد محاذاته     انقل حدوده        أعد توليد data/          جدّد أثره

                        ثم:  VERSION  →  build_manifest.py  →  ارفع الفهرس
                            ارفع الرقم    ابنِ الفهرس الحيّ      فيصل الجميع
```

ورفعُ الفهرس هو الخطوة التي يصل بها التحسين. وبدونها يبقى الناس على
القديم ولا يدرون — حتى لو رفعتَ الصوت الجديد على الخادم، فالرابط لم
يتغيّر فلا سبب عند المتصفّح لإعادة جلبه.

واكتب في `CHANGELOG.md` أيُّ الأوجه تغيّر: من ثبّت نسخةً بوسمٍ لا يعلم
أنّ عليه التجديد إلا أن تقول له.

## التغطية — وما ينقص

انظر `COVERAGE.txt` للأرقام الحالية. وما ينقص ينقص لثلاثة أسباب، وكلها
قابلةٌ للإصلاح:

1. **أوجهٌ لم تُحاذَ بعد.** المحاذاة تعمل وجهًا وجهًا وتُستكمل.
2. **ملفا صوتٍ غائبان** من تنظيم `khatma/` — لكنهما **موجودان** في تنظيم
   `pages/`: الوجه 504 هو `pages/46 Page 3.mp3`، والوجه 566 هو
   `pages/68 Page 3.mp3`. انظر `MISSING.md`.
3. **الوجه 268** محاذاته ضعيفة الثقة ويُستحسن سماعُها قبل الاعتماد عليها.

وكلُّ ما هنا مولَّدٌ من التوقيتات، فتحديثُ `data/ayah-timings.json` وإعادةُ
تشغيل `export_recitation.py` يكفيان.

## كيف أُنتجت التوقيتات

محاذاةٌ قسرية بـ[faster-whisper](https://github.com/SYSTRAN/faster-whisper):
تُفرَّغ تلاوةُ الوجه، ثم يُطابَق التفريغ بنصّ آياته المعروف، فيُعرف أين تبدأ
كلُّ آية. وتُرفَض الصفحة كاملةً إن ضعفت المطابقة أو اختلّ ترتيب المبادئ —
توقيتٌ مزاحٌ يضع الضوء على آيةٍ غير التي تُتلى يُعلّم الحافظ خطأً، وسكوتُ
صفحةٍ أهونُ منه.

الأداة ومعاييرها في المستودع الأصلي:
[Aqtar-Company/IbrahimQuran](https://github.com/Aqtar-Company/IbrahimQuran) —
`tools/align_page.py`.

## ما لم يُتحقَّق منه

- **ردُّ التوقيتات إلى ملفات السور** يفترض أن ملف السورة هو أوجهُها موصولةً
  بترتيبها بلا زيادة. لم يُختبَر. الفحص في دقيقتين مشروحٌ في آخر
  `tools/export_recitation.py`.
- **نهاية آخر آيةٍ في كل وجه** غير مسجّلة؛ `split_ayahs.py` لا يحتاجها
  (يقصّ إلى آخر الملف)، لكن `segments.*` تتركها فارغةً ما لم تُعطَ
  `--durations`.

---

## English

Ayah-level timings for the recitation of **Dr. Ibrahim Hassan**,
plus tools to export it as one file per ayah for inclusion in a mushaf app.

The audio itself is not in this repository — it lives on ibrahimquran.com and
runs to gigabytes. What is here describes it.

- Recorded **one file per mushaf page**, `khatma/1.mp3` … `khatma/604.mp3`.
- `data/ayah-timings.json` gives each ayah's start in seconds within its page
  file. An ayah ends where the next one begins; the last on a page ends with
  the file.
- **No ayah spans two pages** — verified across all 604 page files — so
  extracting per-ayah audio is a cut, never a join.
- `tools/split_ayahs.py` produces `001001.mp3` (everyayah) and `1.mp3`
  (islamic.network, by position among the 6236) in separate folders.
- `COVERAGE.txt` states exactly how much of the 6236 is covered and what is
  missing. Nothing here is estimated: an ayah with no measured start is absent,
  not guessed.

Timings were produced by forced alignment with faster-whisper, matching the
transcript against the known text of the page. A page whose match is weak, or
whose starts are not strictly increasing, is rejected whole.
