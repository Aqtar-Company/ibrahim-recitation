# تلاوة الشيخ إبراهيم حسن مطاولي — توقيتات الآيات

بيانات وأدوات لدمج هذه التلاوة في تطبيق مصحف: متى تبدأ كل آية ومتى تنتهي،
وأداةٌ تقصّ التلاوة ملفًا لكل آية كما تُوزَّع تلاوات القرّاء.

**الصوت ليس هنا.** هو على خادم ibrahimquran.com، وحجمه بالغيغابايت. هنا
ما يصفه: التوقيتات، والأدوات، وتقرير ما يُغطّى منه وما لا يُغطّى.

---

## ما في هذا المستودع

| المسار | ما هو |
|---|---|
| `data/ayah-timings.json` | مبدأ كل آية داخل ملف وجهها، بالثواني |
| `data/segments.csv` | المقاطع مبسوطةً: سورة، آية، وجه، ملف، مبدأ ونهاية بالملّي ثانية |
| `data/segments.json` | المقاطع نفسها بصيغة JSON، ومعها وصفُ المصدر |
| `tools/export_recitation.py` | يولّد `segments.*` من التوقيتات، ويطبع تقرير التغطية |
| `tools/split_ayahs.py` | يقصّ ملفات الأوجه إلى ملفٍ لكل آية |
| `data/page-map.csv` | خريطة الوجه ↔ السورة ↔ اسما ملفه في التنظيمين |
| `COVERAGE.txt` | التغطية وقت آخر توليد |
| `MISSING.md` | ما ينقص، وأين يُوجَد بديلُه |

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

`start` بالثواني من مبدأ `khatma/{page}.mp3`. ونهاية الآية مبدأُ التي تليها
في الوجه نفسه؛ وآخرُ آيةٍ في الوجه تنتهي بانتهاء ملفه.

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

Ayah-level timings for the recitation of **Sheikh Ibrahim Hassan Mutawally**,
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
