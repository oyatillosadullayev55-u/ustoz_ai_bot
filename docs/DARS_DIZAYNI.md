# UstozAI — dars kartochkalari dizayni

**Yangilangan:** 2026-10-25
**Tegishli kod:** [`services/lesson_media.py`](../services/lesson_media.py),
[`handlers/lessons.py`](../handlers/lessons.py),
[`handlers/common.py`](../handlers/common.py)

## Qisqa mazmun

Har bir dars endi matnli xabar emas, balki **rasmli kartochka** ko'rinishida ochiladi:

- 16:9 nisbatdagi 1280×720 JPEG illyustratsiya;
- rasm ostida sarlavha, dars matni va holat qatori;
- pastda `Darsni tugatdim`, `Test yechish`, `Darslar` va `Bosh menyu` tugmalari;
- dars tugatilganda rasm o'chirilmaydi — faqat caption va tugmalar yangilanadi;
- rasm topilmasa yoki matn 1024 belgidan oshsa, bot matnli kartochkaga qaytadi.

![Fotosintez darsi kartochkasi](../assets/lesson_images/lesson_502.jpg)

## Kartochka tuzilishi

```text
🇬🇧 INGLIZ TILI · 1-DARS
━━━━━━━━━━━━━━
📖 Alifbo va tovushlar

Ingliz alifbosida 26 ta harf bor: 5 ta unli va 21 ta undosh.
...

━━━━━━━━━━━━━━
💡 Maslahat: Matnni o'qib, «Darsni tugatdim» tugmasini bosing.

[✅ Darsni tugatdim]
[📝 Test yechish]
[⬅️ Darslar]
[🏠 Bosh menyu]
```

Tugatilgandan keyin oxirgi qator quyidagicha o'zgaradi:

```text
✅ Tugatilgan. Natijangizda saqlandi.
```

### Nima uchun shunday

| Element | Maqsad |
|---|---|
| Fan nomi katta harflarda | Dars qaysi fanga tegishli ekanini bir qarashda ko'rsatish |
| `1-DARS` belgisi | Tartibni va kontekstni saqlash |
| `📖` bilan sarlavha | Matnning boshlanish nuqtasini ajratish |
| `━━━━` ajratgich | Sarlavha, matn va holatni vizual bo'lish |
| Pastki maslahat | Foydalanuvchiga keyingi qadamni aniq aytish |
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

## 20 ta rasm

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

### 2. Kartochka matni

`handlers/lessons.py` dagi `build_lesson_card(lesson, completed=...)`:

- fan nomi va dars raqami sarlavhasi;
- ajratgich;
- dars nomi;
- `html.escape()` qilingan dars matni;
- tugatilgan yoki tugatilmagan holat qatori.

Matn Telegram caption sifatida yuboriladi. Caption limiti — **1024 belgi**;
`LESSON_CAPTION_LIMIT` shu chegarani bildiradi.

### 3. Kartochkani yuborish

`_send_lesson_card()` oqimi:

1. Rasm va matn tayyorlanadi.
2. Rasm yo'q yoki matn 1024 belgidan uzun bo'lsa — `safe_edit()` orqali oddiy matnli
   xabar yuboriladi. Ma'lumot yo'qolmaydi.
3. Joriy xabar allaqachon foto bo'lsa — `edit_caption()` bilan caption va tugmalar
   yangilanadi.
4. Aks holda eski xabar o'chiriladi va `answer_photo()` bilan yangi kartochka yuboriladi.
5. Muvaffaqiyatli yuborilgandan keyin `file_id` keshlanadi.

### 4. Foto xabardan chiqish

`handlers/common.py` dagi `safe_edit()` endi foto xabarni ham biladi:

- xabar foto bo'lsa, u o'chiriladi va yangi matnli xabar yuboriladi;
- oddiy matnli xabar bo'lsa, avvalgidek `edit_text()` ishlatiladi;
- Telegram xatosi bo'lsa, foydalanuvchiga yangi xabar yuboriladi.

Shu tufayli `Darslar`, `Test yechish` yoki boshqa bo'limga o'tishda eski foto va uning
tugmalari chatda qolib ketmaydi.

## Dizayn qoidalari

1. **Bitta ekran — bitta harakat.** Har bir kartochkada keyingi qadam aniq ko'rsatiladi.
2. **Matn rasm ustida emas, captionda.** Bu ekran o'quvchi va qidiruv uchun qulay.
3. **Rasm mazmunni takrorlamaydi.** U mavzuni emotsional va vizual eslab qolishga yordam beradi.
4. **Kontrast.** To'q fon va yorqin urg'u ranglar kichik ekranda ham ajralib turadi.
5. **Bir xil tizim.** Barcha rasmlar bir xil palitra, yorug'lik va kompozitsiyada.
6. **Ortiqcha tugma yo'q.** To'rtta tugma yetarli; har biri bitta aniq amalni bajaradi.
7. **Matnli zaxira.** Rasm yuklanmasa ham dars to'liq o'qiladi.

## Yangi dars yoki rasm qo'shish

1. `content/seed_data.json` ga darsni qo'shing va uning `id` sini yozib oling.
2. `assets/lesson_images/lesson_<id>.jpg` nomida 16:9 rasm tayyorlang.
3. Rasmni 1280×720 JPEG (85% sifat) qilib saqlang.
4. Botni qayta ishga tushiring — `seed_content()` yangi darsni bazaga yuklaydi.
5. Tekshiring:

```powershell
python -m ruff check .
python tests\test_handlers_offline.py
```

Mavjud rasmni almashtirish uchun nomni o'zgartirmang: eski faylni yangisi bilan
almashtirib, botni qayta ishga tushiring.

## Xavfsizlik va barqarorlik

- Rasmlar statik fayllar; foydalanuvchi kiritgan matn rasm nomiga ta'sir qilmaydi.
- Dars sarlavhasi va matni `html.escape()` qilinadi.
- Rasm yuborilmasa, logga faqat dars ID si yoziladi; token yoki foydalanuvchi ma'lumoti
  yozilmaydi.
- Caption limitidan oshsa, bot matnli xabarga qaytadi — dars mazmuni yo'qolmaydi.
- Rasm fayllari `.gitignore` ga tushmaydi va repoda versiyalanadi.

## Tekshirish

`tests/test_handlers_offline.py` quyidagilarni tekshiradi:

- bazada 20 ta dars bor;
- har bir dars uchun rasm fayli mavjud;
- tugatilgan va tugatilmagan kartochkalar 1024 belgidan oshmaydi;
- dars ochilganda `SendPhoto` yuboriladi;
- dars tugatilganda foto xabarning caption'i `EditMessageCaption` bilan yangilanadi;
- foto kartochkadan darslar ro'yxatiga qaytish ishlaydi.

Kutilgan natija: `HANDLER_FLOW_OK`.
