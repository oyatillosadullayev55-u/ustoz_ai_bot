# UstozAI — dars kartochkalari dizayni

**Yangilangan:** 2026-10-25
**Tegishli kod:** [`services/lesson_media.py`](../services/lesson_media.py),
[`handlers/lessons.py`](../handlers/lessons.py),
[`handlers/common.py`](../handlers/common.py)

## Qisqa mazmun

Har bir dars endi matnli xabar emas, balki **rasmli kartochka** ko'rinishida ochiladi:

- 16:9 nisbatdagi 1280×720 JPEG illyustratsiya;
- rasm ostida sarlavha, **qisqa mazmun**, **3 ta asosiy fikr**, davomiylik va daraja;
- pastda `Batafsil o'qish`, `Darsni tugatdim`, `AI Ustozga so'rash`, `Test yechish`,
  `Oldingi/Keyingi dars`, `Darslar` va `Bosh menyu` tugmalari;
- **Batafsil o'qish** to'liq matnni alohida ekranda ochadi: maqsad, sodda tushuntirish,
  hayotiy misol, asosiy fikrlar, eslab qolish siri, mini mashq va xulosa;
- dars tugatilganda joriy ekran (kartochka yoki batafsil matn) yangilanadi;
- rasm topilmasa yoki caption 1024 belgidan oshsa, bot matnli kartochkaga qaytadi.

![Fotosintez darsi kartochkasi](../assets/lesson_images/lesson_502.jpg)

## Kartochka tuzilishi

```text
🇬🇧 INGLIZ TILI · 1-DARS
━━━━━━━━━━━━━━
📖 Alifbo va tovushlar

🎯 Ingliz alifbosida 35 ta harf bor: 5 ta unli va 21 ta undosh...

🔑 Asosiy fikrlar
• Harflar va tovushlar bir xil emas.
• Unli harflar bo'g'in hosil qiladi.
• Talaffuzni ovoz chiqarib mashq qiling.

⏱️ 7 daqiqa · 🟢 Boshlang'ich
━━━━━━━━━━━━━━
💡 Maslahat: «Batafsil o'qish» bilan mavzuni chuqurroq o'rganing.

[📖 Batafsil o'qish]
[✅ Darsni tugatdim]
[🧠 AI Ustozga so'rash]
[📝 Test yechish]
[⬅️ Oldingi dars] [➡️ Keyingi dars]
[⬅️ Darslar] [🏠 Bosh menyu]
```

Batafsil ekran:

```text
📖 Alifbo va tovushlar
🇬🇧 Ingliz tili · 1-dars
⏱️ 7 daqiqa · 🟢 Boshlang'ich
━━━━━━━━━━━━━━

🎯 Maqsad: ...
1️⃣ Oddiy tilda: ...
2️⃣ Hayotiy misol: ...
3️⃣ Asosiy fikrlar: ...
4️⃣ Eslab qolish siri: ...
✍️ Mini mashq: ...
✅ Xulosa: ...

━━━━━━━━━━━━━━
💡 Maslahat: «Batafsil o'qish» bilan mavzuni chuqurroq o'rganing.
📝 Darsni tugatgach, test orqali bilimingizni sinang.

[🖼️ Kartochkaga qaytish]
[✅ Darsni tugatdim]
[🧠 AI Ustozga so'rash]
[📝 Test yechish]
[⬅️ Oldingi dars] [➡️ Keyingi dars]
[⬅️ Darslar] [🏠 Bosh menyu]
```

Tugatilgandan keyin holat qatori quyidagicha o'zgaradi:

```text
✅ Tugatilgan. Natijangizda saqlandi.
```

### Nima uchun shunday

| Element | Maqsad |
|---|---|
| Fan nomi katta harflarda | Dars qaysi fanga tegishli ekanini bir qarashda ko'rsatish |
| `1-DARS` belgisi | Tartibni va kontekstni saqlash |
| `📖` bilan sarlavha | Matnning boshlanish nuqtasini ajratish |
| Qisqa mazmun | 2–3 gapda mavzuni tanishtirish, darhol o'qishga kirishish |
| 3 ta asosiy fikr | Diqqatni eng muhim narsalarga qaratish |
| Davomiylik va daraja | O'quvchi qancha vaqt sarflashini bilib oladi |
| `Batafsil o'qish` | Kartochkani ortiqcha matn bilan to'ldirmaslik |
| Oldingi/keyingi dars | Ketma-ket o'rganishni osonlashtirish |
| Bitta ustunli tugmalar | Telefonda tasodifiy bosishni kamaytirish |

## Vizual tizim

Barcha 20 rasm bitta uslubda tayyorlangan:

| Parametr | Qiymat |
|---|---|
| Fon | To'q yashil-ko'k (`#0B1F2A`) |
| Asosiy urg'u | Feruza (`#35D6C7`) |
| Issiq urg'u | Amber (`#FFB547`) |
| Uslub | Flat vector, paper-cut, yumshoq glow, nuqtali to'r |
| Nisbat | 16:9 |
| Hajm | 1280×720 JPEG, 85% sifat |
| Fayl hajmi | taxminan 49–130 KB |
| Jami | taxminan 1.5 MB |
| Matn | Rasmlarda matn yo'q — barcha matn caption ichida |

Rasmlarda harflar, raqamlar va logotiplar ataylab ishlatilmagan: Telegram shrifti va
tarjima qilish imkoniyati captionda qoladi, rasm esa faqat mavzuni vizual ochib beradi.

## 35 ta rasm

Fayllar `assets/lesson_images/` papkasida, nomi `lesson_<dars_id>.jpg`.

| ID | Fan | Dars | Rasm |
|---|---|---|---|
| 101 | Ingliz tili | Alifbo va tovushlar | [lesson_101.jpg](../assets/lesson_images/lesson_101.jpg) |
| 102 | Ingliz tili | Present Simple | [lesson_102.jpg](../assets/lesson_images/lesson_102.jpg) |
| 201 | Matematika | Kasrlar bilan amallar | [lesson_201.jpg](../assets/lesson_images/lesson_201.jpg) |
| 202 | Matematika | Foizlar va nisbatlar | [lesson_202.jpg](../assets/lesson_images/lesson_202.jpg) |
| 301 | Fizika | Harakat va tezlik | [lesson_301.jpg](../assets/lesson_images/lesson_301.jpg) |
| 302 | Fizika | Nyuton qonunlari | [lesson_302.jpg](../assets/lesson_images/lesson_302.jpg) |
| 401 | Kimyo | Atom va molekula | [lesson_401.jpg](../assets/lesson_images/lesson_401.jpg) |
| 402 | Kimyo | Kimyoviy reaksiyalar | [lesson_402.jpg](../assets/lesson_images/lesson_402.jpg) |
| 501 | Biologiya | Hujayra tuzilishi | [lesson_501.jpg](../assets/lesson_images/lesson_501.jpg) |
| 502 | Biologiya | Fotosintez | [lesson_502.jpg](../assets/lesson_images/lesson_502.jpg) |
| 601 | Tarix | Amir Temur davri | [lesson_601.jpg](../assets/lesson_images/lesson_601.jpg) |
| 602 | Tarix | Buyuk Ipak yo'li | [lesson_602.jpg](../assets/lesson_images/lesson_602.jpg) |
| 701 | Ona tili | So'z turkumlari | [lesson_701.jpg](../assets/lesson_images/lesson_701.jpg) |
| 702 | Ona tili | Alisher Navoiy ijodi | [lesson_702.jpg](../assets/lesson_images/lesson_702.jpg) |
| 801 | Informatika | Kompyuter tuzilishi | [lesson_801.jpg](../assets/lesson_images/lesson_801.jpg) |
| 802 | Informatika | Algoritm asoslari | [lesson_802.jpg](../assets/lesson_images/lesson_802.jpg) |
| 901 | Python | O'zgaruvchilar va turlar | [lesson_901.jpg](../assets/lesson_images/lesson_901.jpg) |
| 902 | Python | Shart operatorlari | [lesson_902.jpg](../assets/lesson_images/lesson_902.jpg) |
| 1001 | Dart va Flutter | Dart asoslari | [lesson_1001.jpg](../assets/lesson_images/lesson_1001.jpg) |
| 1002 | Dart va Flutter | Flutter va widget | [lesson_1002.jpg](../assets/lesson_images/lesson_1002.jpg) |

## Kod qanday ishlaydi

### 1. Rasmni topish

`services/lesson_media.py`:

| Funksiya | Vazifasi |
|---|---|
| `get_lesson_image_path(lesson_id)` | `.jpg`, `.jpeg`, `.png` tartibida faylni qidiradi; topilmasa `None` |
| `get_lesson_photo(lesson_id)` | avval keshlangan `file_id`, keyin `FSInputFile` qaytaradi |
| `remember_lesson_file_id(lesson_id, file_id)` | birinchi yuborilgandan keyin `file_id` ni jarayon xotirasida saqlaydi |

Birinchi ochishda rasm Telegramga yuklanadi. Keyingi ochishlarda `file_id` ishlatiladi,
shuning uchun fayl qayta yuborilmaydi. Bot qayta ishga tushsa, kesh tozalanadi va
birinchi foydalanuvchi rasmni yana bir marta yuklaydi.

### 2. Kartochka va batafsil matn

`handlers/lessons.py`:

| Funksiya | Vazifasi |
|---|---|
| `build_lesson_card(lesson, completed=...)` | Qisqa kartochka: fan, dars raqami, sarlavha, qisqa mazmun, 4 tagacha asosiy fikr, davomiylik, daraja va holat |
| `build_lesson_details(lesson, completed=...)` | To'liq matnni alohida ekranga sig'diradi: sarlavha, fan, davomiylik, daraja, `content`, holat va maslahat |
| `_adjacent_lesson_ids(lesson)` | Shu fan ichidagi oldingi va keyingi dars ID'larini qaytaradi |
| `_is_details_view(message)` | Joriy xabar batafsil ekranmi yoki kartochkami — tugma matni bo'yicha aniqlaydi |

- Kartochkada `summary` (qisqa mazmun) va `key_points` (JSON ro'yxat) ishlatiladi;
  `summary` bo'sh bo'lsa, `content` ning birinchi 220 belgisi olinadi.
- Asosiy fikrlardan ko'pi bilan 4 tasi ko'rsatiladi.
- Barcha matn `html.escape()` qilinadi.

Matn Telegram caption sifatida yuboriladi. Caption limiti — **1024 belgi**;
`LESSON_CAPTION_LIMIT` shu chegarani bildiradi. Batafsil ekran oddiy xabar sifatida
yuboriladi va `LESSON_TEXT_LIMIT = 4000` belgi bilan cheklanadi; matn uzun bo'lsa,
oxiri `…` bilan qisqartiriladi.

### 3. Kartochkani yuborish

`_send_lesson_card()` oqimi:

1. Rasm, matn va oldingi/keyingi dars ID'lari tayyorlanadi.
2. Rasm yo'q yoki matn 1024 belgidan uzun bo'lsa — `safe_edit()` orqali oddiy matnli
   xabar yuboriladi. Ma'lumot yo'qolmaydi.
3. Joriy xabar allaqachon foto bo'lsa — `edit_caption()` bilan caption va tugmalar
   yangilanadi.
4. Aks holda eski xabar o'chiriladi va `answer_photo()` bilan yangi kartochka yuboriladi.
5. Muvaffaqiyatli yuborilgandan keyin `file_id` keshlanadi.

### 4. Batafsil ekran va navigatsiya

- `lesson:read:<id>` callback'i `read_lesson()` handleriga tushadi:
  `mark_lesson_started()` chaqiriladi va `_send_lesson_details()` orqali to'liq matn
  `safe_edit()` bilan ko'rsatiladi.
- `lesson:view:<id>` kartochkaga qaytaradi.
- `⬅️ Oldingi dars` / `➡️ Keyingi dars` ham `lesson:view:<id>` ishlatadi, shuning uchun
  har bir dars avval qisqa kartochka bilan ochiladi.
- `lesson:complete:<id>` joriy ekranni aniqlaydi: batafsil ekranda bo'lsa, yangilangan
  batafsil matn, aks holda yangilangan kartochka yuboriladi. Shu tufayli foydalanuvchi
  o'qiyotgan ekrandan chiqib ketmaydi.
- Batafsil o'qishda `mark_lesson_started()` takror chaqirilsa ham progress buzilmaydi.

### 5. Dars kontekstidagi AI Ustoz

`🧠 AI Ustozga so'rash` tugmasi `lesson:ask:<id>` callback'ini yuboradi. Handler
(`handlers/ai_tutor.py`) darsning `id`, fan nomi, sarlavhasi, qisqa mazmuni va matnini
FSM ma'lumotiga `lesson_context` sifatida saqlaydi va AI rejimini ochadi.
`services/ai_service.py` bu kontekstni alohida tizim xabari sifatida provayderga
qo'shadi; AI o'chirilgan bo'lsa, javob shu dars matnidan tayyorlanadi.

### 6. Foto xabardan chiqish

`handlers/common.py` dagi `safe_edit()` endi foto xabarni ham biladi:

- xabar foto bo'lsa, u o'chiriladi va yangi matnli xabar yuboriladi;
- oddiy matnli xabar bo'lsa, avvalgidek `edit_text()` ishlatiladi;
- Telegram xatosi bo'lsa, foydalanuvchiga yangi xabar yuboriladi.

Shu tufayli `Darslar`, `Test yechish` yoki boshqa bo'limga o'tishda eski foto va uning
tugmalari chatda qolib ketmaydi.

## Dizayn qoidalari

1. **Bitta ekran — bitta harakat.** Kartochka tez tanishtiradi, batafsil ekran chuqur
   o'rgatadi, test bilimni tekshiradi.
2. **Matn rasm ustida emas, caption yoki xabar matnida.** Bu ekran o'quvchi, qidiruv va
   nusxa olish uchun qulay.
3. **Rasm mazmunni takrorlamaydi.** U mavzuni emotsional va vizual eslab qolishga yordam beradi.
4. **Kontrast.** To'q fon va yorqin urg'u ranglar kichik ekranda ham ajralib turadi.
5. **Bir xil tizim.** Barcha rasmlar bir xil palitra, yorug'lik va kompozitsiyada.
6. **Tugmalar guruhlangan.** Har bir tugma bitta amalni bajaradi; asosiy amallar bitta
   ustunda, navigatsiya juftliklari bir qatorda turadi.
7. **Matnli zaxira.** Rasm yuklanmasa ham dars to'liq o'qiladi.

## Yangi dars yoki rasm qo'shish

1. `content/seed_data.json` ga darsni qo'shing va uning `id` sini yozib oling. Majburiy
   maydonlar: `title`, `summary` (kamida 80 belgi), `key_points` (aynan 3 ta band),
   `level` (`beginner` / `intermediate` / `advanced`), `duration_min` (1–120) va
   `content` (kamida 900 belgi). Har bir darsga kamida 4 ta savol qo'shing.
2. `assets/lesson_images/lesson_<id>.jpg` nomida 16:9 rasm tayyorlang.
3. Rasmni 1280×720 JPEG (85% sifat) qilib saqlang.
4. Botni qayta ishga tushiring — `seed_content()` yangi darsni bazaga yuklaydi va mavjud
   bazadagi darslarga yangi ustunlarni migratsiya qiladi.
5. Tekshiring:

```powershell
python -m ruff check .
python tests\test_offline.py
python tests\test_handlers_offline.py
```

Mavjud rasmni almashtirish uchun nomni o'zgartirmang: eski faylni yangisi bilan
almashtirib, botni qayta ishga tushiring.

## Xavfsizlik va barqarorlik

- Rasmlar statik fayllar; foydalanuvchi kiritgan matn rasm nomiga ta'sir qilmaydi.
- Dars sarlavhasi, qisqa mazmun, asosiy fikrlar va matn `html.escape()` qilinadi.
- Rasm yuborilmasa, logga faqat dars ID si yoziladi; token yoki foydalanuvchi ma'lumoti
  yozilmaydi.
- Caption limitidan oshsa, bot matnli xabarga qaytadi — dars mazmuni yo'qolmaydi.
- Batafsil matn 4000 belgi bilan cheklanadi, shuning uchun Telegram xabar limitidan
  oshmaydi.
- `lesson_context` FSM ichida saqlanadi va faqat shu suhbat uchun ishlatiladi; bazaga
  yozilmaydi.
- Rasm fayllari `.gitignore` ga tushmaydi va repoda versiyalanadi.

## Tekshirish

`tests/test_offline.py` va `tests/test_handlers_offline.py` quyidagilarni tekshiradi:

- bazada 35 ta dars va 140 ta savol bor;
- har bir darsda `summary`, 3 ta `key_points`, `level`, `duration_min` va kamida 900
  belgili `content` mavjud;
- har bir dars uchun rasm fayli mavjud;
- tugatilgan va tugatilmagan kartochkalar 1024 belgidan oshmaydi;
- dars ochilganda `SendPhoto` yuboriladi;
- kartochkada batafsil o'qish, AI va test tugmalari bor;
- oldingi/keyingi dars tugmalari faqat mavjud qo'shnilar uchun chiqadi;
- batafsil ekran 4000 belgidan oshmaydi va `Kartochkaga qaytish` tugmasini beradi;
- dars tugatilganda foto caption yoki batafsil xabar yangilanadi va tugma olib tashlanadi;
- `lesson:ask` dars kontekstini AI rejimiga uzatadi;
- foto kartochkadan darslar ro'yxatiga qaytish ishlaydi.

Kutilgan natija: `OFFLINE_TESTS_OK` va `HANDLER_FLOW_OK`.
