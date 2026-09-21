# ما ينقص، وأين يُوجَد

التلاوة مرفوعةٌ بثلاث تنظيمات لنفس الصوت: أوجهُ المصحف (`khatma/`)،
والسورُ كاملة (`surah/`)، والأوجهُ داخل سورها (`pages/`). فما غاب عن
تنظيمٍ قد يكون حاضرًا في آخر.

الخريطة الكاملة في `data/page-map.csv`. واتّساقُها محقَّق: الأزواج
(سورة، وجه) المشتقّة من بيانات المصحف **668 بالضبط**، وهو عددُ ملفات
`pages/` على الخادم — بلا فرقٍ واحد.

## ملفا صوتٍ غائبان عن khatma

| الوجه | الغائب | الموجود بدلًا منه |
|---|---|---|
| 504 | `khatma/504.mp3` | `pages/46 Page 3.mp3` |
| 566 | `khatma/566.mp3` | `pages/68 Page 3.mp3` · `pages/69 Page 1.mp3` |

## أوجهٌ لم تُحاذَ بعد (69)

كلُّها صوتُها موجود؛ ينقصها أن تُحاذى. وتُحاذى من `khatma/` أو من
مقابلها في `pages/` — الصوتُ واحد، والتوقيتُ يبقى منسوبًا إلى مبدأ
الوجه في الحالتين، فلا يختلّ شيء.

| الوجه | khatma | pages |
|---|---|---|
| 9 | `khatma/9.mp3` | `pages/2 Page 8.mp3` |
| 21 | `khatma/21.mp3` | `pages/2 Page 20.mp3` |
| 29 | `khatma/29.mp3` | `pages/2 Page 28.mp3` |
| 41 | `khatma/41.mp3` | `pages/2 Page 40.mp3` |
| 49 | `khatma/49.mp3` | `pages/2 Page 48.mp3` |
| 61 | `khatma/61.mp3` | `pages/3 Page 12.mp3` |
| 69 | `khatma/69.mp3` | `pages/3 Page 20.mp3` |
| 81 | `khatma/81.mp3` | `pages/4 Page 5.mp3` |
| 89 | `khatma/89.mp3` | `pages/4 Page 13.mp3` |
| 101 | `khatma/101.mp3` | `pages/4 Page 25.mp3` |
| 109 | `khatma/109.mp3` | `pages/5 Page 4.mp3` |
| 121 | `khatma/121.mp3` | `pages/5 Page 16.mp3` |
| 129 | `khatma/129.mp3` | `pages/6 Page 2.mp3` |
| 141 | `khatma/141.mp3` | `pages/6 Page 14.mp3` |
| 149 | `khatma/149.mp3` | `pages/6 Page 22.mp3` |
| 161 | `khatma/161.mp3` | `pages/7 Page 11.mp3` |
| 169 | `khatma/169.mp3` | `pages/7 Page 19.mp3` |
| 181 | `khatma/181.mp3` | `pages/8 Page 5.mp3` |
| 189 | `khatma/189.mp3` | `pages/9 Page 3.mp3` |
| 192 | `khatma/192.mp3` | `pages/9 Page 6.mp3` |
| 201 | `khatma/201.mp3` | `pages/9 Page 15.mp3` |
| 209 | `khatma/209.mp3` | `pages/10 Page 2.mp3` |
| 221 | `khatma/221.mp3` | `pages/10 Page 14.mp3` · `pages/11 Page 1.mp3` |
| 229 | `khatma/229.mp3` | `pages/11 Page 9.mp3` |
| 241 | `khatma/241.mp3` | `pages/12 Page 7.mp3` |
| 249 | `khatma/249.mp3` | `pages/13 Page 1.mp3` |
| 261 | `khatma/261.mp3` | `pages/14 Page 7.mp3` |
| 268 | `khatma/268.mp3` | `pages/16 Page 2.mp3` |
| 269 | `khatma/269.mp3` | `pages/16 Page 3.mp3` |
| 281 | `khatma/281.mp3` | `pages/16 Page 15.mp3` |
| 289 | `khatma/289.mp3` | `pages/17 Page 8.mp3` |
| 301 | `khatma/301.mp3` | `pages/18 Page 9.mp3` |
| 309 | `khatma/309.mp3` | `pages/19 Page 5.mp3` |
| 321 | `khatma/321.mp3` | `pages/20 Page 10.mp3` |
| 329 | `khatma/329.mp3` | `pages/21 Page 8.mp3` |
| 341 | `khatma/341.mp3` | `pages/22 Page 10.mp3` |
| 349 | `khatma/349.mp3` | `pages/23 Page 8.mp3` |
| 361 | `khatma/361.mp3` | `pages/25 Page 3.mp3` |
| 369 | `khatma/369.mp3` | `pages/26 Page 3.mp3` |
| 381 | `khatma/381.mp3` | `pages/27 Page 5.mp3` |
| 389 | `khatma/389.mp3` | `pages/28 Page 5.mp3` |
| 401 | `khatma/401.mp3` | `pages/29 Page 6.mp3` |
| 409 | `khatma/409.mp3` | `pages/30 Page 6.mp3` |
| 421 | `khatma/421.mp3` | `pages/33 Page 4.mp3` |
| 429 | `khatma/429.mp3` | `pages/34 Page 2.mp3` |
| 441 | `khatma/441.mp3` | `pages/36 Page 2.mp3` |
| 449 | `khatma/449.mp3` | `pages/37 Page 4.mp3` |
| 461 | `khatma/461.mp3` | `pages/39 Page 4.mp3` |
| 469 | `khatma/469.mp3` | `pages/40 Page 3.mp3` |
| 481 | `khatma/481.mp3` | `pages/41 Page 5.mp3` |
| 489 | `khatma/489.mp3` | `pages/42 Page 7.mp3` · `pages/43 Page 1.mp3` |
| 501 | `khatma/501.mp3` | `pages/45 Page 3.mp3` |
| 504 | `khatma/504.mp3` | `pages/46 Page 3.mp3` |
| 509 | `khatma/509.mp3` | `pages/47 Page 3.mp3` |
| 521 | `khatma/521.mp3` | `pages/51 Page 2.mp3` |
| 529 | `khatma/529.mp3` | `pages/54 Page 2.mp3` |
| 533 | `khatma/533.mp3` | `pages/55 Page 3.mp3` |
| 541 | `khatma/541.mp3` | `pages/57 Page 5.mp3` |
| 549 | `khatma/549.mp3` | `pages/60 Page 1.mp3` |
| 561 | `khatma/561.mp3` | `pages/66 Page 2.mp3` |
| 566 | `khatma/566.mp3` | `pages/68 Page 3.mp3` · `pages/69 Page 1.mp3` |
| 569 | `khatma/569.mp3` | `pages/70 Page 2.mp3` |
| 581 | `khatma/581.mp3` | `pages/77 Page 2.mp3` |
| 589 | `khatma/589.mp3` | `pages/83 Page 3.mp3` · `pages/84 Page 1.mp3` |
| 592 | `khatma/592.mp3` | `pages/87 Page 2.mp3` · `pages/88 Page 1.mp3` |
| 594 | `khatma/594.mp3` | `pages/89 Page 2.mp3` · `pages/90 Page 1.mp3` |
| 595 | `khatma/595.mp3` | `pages/90 Page 2.mp3` · `pages/91 Page 1.mp3` · `pages/92 Page 1.mp3` |
| 599 | `khatma/599.mp3` | `pages/98 Page 2.mp3` · `pages/99 Page 1.mp3` · `pages/100 Page 1.mp3` |
| 601 | `khatma/601.mp3` | `pages/103 Page 1.mp3` · `pages/104 Page 1.mp3` · `pages/105 Page 1.mp3` |

## وجهٌ محاذاتُه ضعيفة

الوجه **268** طابقت محاذاتُه بنسبةٍ منخفضة بالنموذجين معًا. توقيتاتُه
موجودةٌ في البيانات، ويُستحسن سماعُ الوجه والتأكّد من أن ملفّه تلاوةُ
هذا الوجه فعلًا قبل الاعتماد عليه.
