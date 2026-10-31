# UstozAI — foydalanuvchi qo'llanmasi

UstozAI — o'zbek tilida bilim olish uchun Telegram bot. Bu qo'llanma botdan
foydalanish va admin panelni sozlashni tushuntiradi.

## Boshlash

1. Botga o'ting va **Start** tugmasini bosing yoki `/start` yuboring.
2. Ismingizni yozing (2–50 belgi).
3. Bilim darajangizni tanlang:
   - 🟢 **Boshlang'ich**
   - 🟡 **O'rta**
   - 🔴 **Yuqori**
4. Tasdiqlash xabari va asosiy menyu chiqadi.

Qayta `/start` yuborsangiz, bot sizdan ismni yana so'ramaydi.

## Asosiy menyu

| Tugma | Nima qiladi |
| --- | --- |
| 🧠 AI Ustoz | Savol-javob rejimini ochadi |
| 📚 Darslar | Fan va darslarni tanlash |
| 📝 Testlar | 5 savolli testni boshlash |
| 📊 Mening natijalarim | Statistika va oxirgi natijalar |
| 📅 Kunlik reja | Kunlik maqsad va progress |
| ⚙️ Sozlamalar | Daraja va bildirishnomalar |

Darslarni tez topish uchun `/qidiruv so'z` buyrug'idan foydalanishingiz mumkin.

## Buyruqlar

| Buyruq | Vazifasi |
| --- | --- |
| `/start` | Botni ishga tushirish yoki ro'yxatdan o'tish |
| `/menu` | Bosh menyuni ochish |
| `/qidiruv` | Darslarni nomi yoki mazmuni bo'yicha qidirish |
| `/search` | `/qidiruv` buyrug'ining inglizcha nomi |
| `/help` | Yordam xabari |
| `/id` | Telegram ID raqamingizni ko'rsatish |
| `/admin` | Admin panel (faqat adminlar uchun) |
| `/backup` | Baza zaxira nusxasini yuborish (faqat adminlar uchun) |
| `/export` | Foydalanuvchilar jadvalini CSV qilib yuborish (faqat adminlar uchun) |
| `/cancel` | Admin xabar yuborish jarayonini bekor qilish |

`/qidiruv` dan keyin so'zni bo'sh joy bilan yozing, masalan `/qidiruv fotosintez`.
So'rov uzunligi 2–100 belgi bo'lishi kerak.

## Darslar

1. **📚 Darslar** tugmasini bosing.
2. Fan tanlang — yuqorida umumiy progress ko'rsatiladi, har bir fan tugmasida
   `tugatilgan/jami` dars soni (masalan, `2/5`) turadi.
3. Darsni tanlang — u 16:9 rasmli kartochka bo'lib ochiladi. Kartochkada fan nomi,
   dars raqami, **qisqa mazmun**, **3 ta asosiy fikr**, davomiylik va daraja
   (🟢 Boshlang'ich, 🟡 O'rta, 🔴 Yuqori) ko'rsatiladi.
4. Qisqa mazmun bilan tanishib, **📖 Batafsil o'qish** tugmasini bosing. To'liq dars
   quyidagi bo'limlardan iborat:
   - 🎯 **Maqsad** — bu darsda nimani o'rganasiz;
   - **Oddiy tilda tushuntirish** — murakkab atamalarsiz izoh;
   - **Hayotiy misol** — mavzuni kundalik hayotga bog'lash;
   - 🔑 **Asosiy fikrlar** — yodda qolishi kerak bo'lgan 3 ta fikr;
   - 💡 **Eslab qolish siri** — mnemonika yoki qisqa qoida;
   - ✍️ **Mini mashq** — o'zingiz bajarib ko'radigan kichik topshiriq;
   - ✅ **Xulosa** — darsning eng muhim yakuni.
5. **🖼️ Kartochkaga qaytish** rasmli ko'rinishga qaytaradi.
6. **⬅️ Oldingi dars** va **➡️ Keyingi dars** bilan shu fan ichidagi mavzular orasida
   yuring — darslar tartib bilan o'rganish uchun moslashgan.
7. **🧠 AI Ustozga so'rash** tugmasi AI rejimini aynan shu dars konteksti bilan ochadi.
   «Buni oddiyroq tushuntirib bering», «Hayotiy misol keltiring» yoki «Menga mini
   mashq bering» deb yozishingiz mumkin.
8. Darsni o'zlashtirgan bo'lsangiz, **✅ Darsni tugatdim** tugmasini bosing.
   Tugatilgan darslar ro'yxatda ✅ bilan belgilanadi.
9. **📝 Test yechish** orqali shu fan bo'yicha testni boshlashingiz mumkin.
10. **⭐ Sevimlilarga qo'shish** tugmasi darsni saqlaydi (yana bosilsa — olib
    tashlaydi). Saqlangan darslar «📊 Mening natijalarim → ⭐ Sevimlilarim» da
    ko'rinadi.

Darsni faqat bir marta tugatilgan deb belgilash mumkin — takroriy bosish kunlik
rejani qayta oshirmaydi. Tugatish kartochkada ham, batafsil o'qish ekranida ham
ishlaydi. Har bir tugatilgan dars uchun **+20 XP** beriladi (bir dars uchun faqat
bir marta).

Har bir dars uchun alohida rasm tayyorlangan. Agar rasm yuklanmasa yoki dars matni
juda uzun bo'lsa, bot darsni matnli kartochka sifatida ochadi — mazmun yo'qolmaydi.

### Darsni o'rganish tartibi

1. Kartochkadagi qisqa mazmun va asosiy fikrlarni o'qing.
2. **📖 Batafsil o'qish** da maqsad va oddiy tushuntirishni o'qing.
3. Hayotiy misolni o'zingizga moslab qayta ayting.
4. Mini mashqni daftarga yoki chatga yozib bajaring.
5. Xulosani o'qib, **✅ Darsni tugatdim** ni bosing.
6. **📝 Test yechish** bilan bilimingizni sinang; xato bo'lsa, tahlildagi izohni
   o'qib, darsga qaytib takrorlang.
7. Tushunmagan joyda **🧠 AI Ustozga so'rash** dan foydalaning.

### Fanlar

Ingliz tili, Matematika, Fizika, Kimyo, Biologiya, Tarix, Ona tili va adabiyot,
Informatika, Python, Dart va Flutter. Har bir fanda 2 tadan dars bor.

## Dars qidiruvi

1. `/qidiruv fotosintez` kabi buyruq yuboring yoki **📚 Darslar** bo'limidagi
   qidiruv haqidagi eslatmadan foydalaning.
2. Bot dars nomi va matni bo'yicha mos keladigan darslarni topadi.
3. Natijalar ro'yxatidan darsni tanlasangiz, u darhol ochiladi.
4. Mos dars topilmasa, bot qisqaroq yoki boshqacha kalit so'z bilan urinishni
   taklif qiladi.

Qidiruvda faqat faol darslar qatnashadi va ko'pi bilan 5 ta natija ko'rsatiladi.
So'rov 2–100 belgi oralig'ida bo'lishi shart.

## Testlar

1. **📝 Testlar** tugmasini bosing yoki dars ichidan **📝 Test yechish** ni tanlang.
2. Fan tanlang.
3. Har bir savolda 4 ta variant bor; bittasini bosing.
4. Savollar orasida to'g'ri javob ko'rsatilmaydi — natija test oxirida chiqadi.
5. 5 ta savoldan so'ng foiz va tavsiya ko'rsatiladi. Shu fan bo'yicha eng yaxshi
   natijangiz ham chiqadi; rekordni yangilasangiz, bot buni alohida nishonlaydi.
6. Xato javoblar bo'lsa, alohida xabarda qaysi savolda xato qilganingiz, siz tanlagan
   variant va to'g'ri javob izohi ko'rsatiladi. Barcha javob to'g'ri bo'lsa, tahlil
   xabari yuborilmaydi.
7. **🔁 Qayta yechish**, **📚 Boshqa fanlar** yoki **🏠 Bosh menyu** orqali davom eting.

Test natijasi avtomatik saqlanadi, kunlik rejaga +1 test qo'shiladi va XP beriladi:
`5 + 2 × to'g'ri javob`, 100% natija uchun qo'shimcha `+10`.

## Mening natijalarim

**📊 Mening natijalarim** bo'limida quyidagilar ko'rsatiladi:

- ism va bilim darajasi;
- darajangiz (XP bo'yicha) va jami XP;
- tugatilgan darslar soni;
- yechilgan testlar soni va o'rtacha natija;
- eng yaxshi natija;
- faol kunlar va ketma-ket kunlar (streak);
- berilgan AI savollari soni;
- oxirgi 5 ta test natijasi.

Pastdagi tugmalar orqali qo'shimcha ekranlar ochiladi:

- **🏆 Yutuqlarim** — 12 ta yutuq ro'yxati; ochilganlari yashil, qolganlari 🔒 bilan;
- **📈 Haftalik reyting** — so'nggi 7 kunlik XP bo'yicha TOP-10 va o'z o'rningiz;
- **⭐ Sevimlilarim** — saqlangan darslar; tanlansa, dars darhol ochiladi.

### Darajalar va yutuqlar

Umumiy XP bo'yicha 6 daraja bor: **🌱 Yangi boshlovchi → 📗 O'quvchi → 📘 Bilimdon →
🎓 Tajribali → 🏅 Ustoz → 👑 Afsona**. XP dars tugatish, test yechish, kunlik rejani
bajarish va AI savollari uchun beriladi.

Yutuqlarga misollar: birinchi tugatilgan dars, 5 ta dars, 15 ta dars, barcha 35 ta
dars, birinchi test, 10 ta test, 100% natija, 3 va 7 kunlik streak, 5 ta sevimli
dars, 10 ta AI savol va 5 kunlik maqsad. Yangi yutuq ochilganda bot darhol tabriklaydi.

Haftalik reytingda faqat so'nggi 7 kunda XP to'plagan foydalanuvchilar qatnashadi;
ismlar maxfiylik uchun qisqartiriladi.

Faol kunlar hisobida testlar, tugatilgan darslar va AI Ustozga yozilgan savollar
hisobga olinadi. Shu sababli faqat AI bilan suhbatlashgan kun ham streakni davom
ettiradi.

**🔄 Yangilash** tugmasi ma'lumotlarni qayta yuklaydi.

## Kunlik reja

1. **📅 Kunlik reja** tugmasini bosing.
2. Tayyor maqsadlardan birini tanlang:
   - 🟢 Oson — 1 dars + 1 test
   - 🟡 O'rta — 2 dars + 2 test
   - 🔴 Intensiv — 3 dars + 3 test
3. Dars tugatilganda va test yakunlanganda progress avtomatik yangilanadi.
4. **🔄 Yangilash** joriy holatni ko'rsatadi.

Kunlik reja har kuni yangidan boshlanadi; standart maqsad 1 dars + 1 test.

### Eslatmalar

Agar reja kun oxirigacha bajarilmasa, bot sizga eslatma yuborishi mumkin.
Eslatma faqat shu kun uchun reja ochilgan, bildirishnomalar yoqilgan va maqsad
hali bajarilmagan foydalanuvchilarga yuboriladi.

- Yuborish vaqti odatda **19:00** (O'zbekiston vaqti, UTC+5).
- Eslatmada bajarilgan va rejalashtirilgan dars/test soni ko'rsatiladi.
- Bildirishnomalarni **⚙️ Sozlamalar → 🔔 Bildirishnomalar** orqali o'chirsangiz,
  eslatma ham yuborilmaydi.
- Admin serverda vaqtni `DAILY_REMINDER_HOUR` orqali o'zgartiradi; butunlay
  o'chirish uchun `DAILY_REMINDERS_ENABLED=false` qo'yiladi.

## AI Ustoz

1. **🧠 AI Ustoz** tugmasini bosing.
2. Savolingizni yozing (2–1000 belgi). Masalan:
   - «Fotosintez nima?»
   - «Kvadrat tenglamani qanday yechaman?»
   - «Python'da for sikli qanday ishlaydi?»
3. Javob kelguncha bot yozayotganini ko'rsatadi.
4. **⬅️ Chiqish** tugmasi yoki menyu tugmasi rejimdan chiqaradi.

### Dars bo'yicha AI

Dars kartochkasi yoki batafsil o'qish ekranidagi **🧠 AI Ustozga so'rash** tugmasini
bossangiz, AI shu dars mazmuni bilan tanishib javob beradi:

- tushunarsiz joyni soddaroq qayta tushuntiradi;
- darsga mos hayotiy misol keltiradi;
- qisqa mini mashq beradi;
- darsda yo'q ma'lumot bo'lsa, buni alohida aytadi.

Savol-javob davomida dars konteksti saqlanadi. Boshqa mavzuga o'tish uchun
**⬅️ Chiqish** ni bosing yoki istalgan menyu tugmasini tanlang.

Cheklovlar:

- kuniga **30 ta** savol (sozlamaga qarab o'zgaradi);
- savollar orasida kamida **3 soniya**;
- AI kaliti sozlanmagan bo'lsa, javob dars bazasidan olinadi — dars konteksti
  bo'lsa, aynan shu darsdan parcha ko'rsatiladi.

Javob ostida mavzuga mos **2 tagacha dars tugmasi** chiqadi — bosilsa, o'sha dars
darhol ochiladi. Har bir AI savoli uchun `+1 XP` beriladi.

AI javoblari umumiy ma'lumot uchun; muhim qarorlardan oldin darslik bilan
tekshirib ko'ring.

## Sozlamalar

- **Daraja** — boshlang'ich, o'rta yoki yuqori. Tanlangan daraja AI javoblarining
  murakkabligiga ta'sir qiladi.
- **Bildirishnomalar** — yoqing yoki o'chiring. O'chirilganda admin xabarlari va
  kunlik reja eslatmalari yuborilmaydi.
- **Til** — joriy interfeys tili (hozircha o'zbekcha).
- **AI holati** — provayder ulangan yoki dars bazasidan ishlayotgani ko'rsatiladi.

## Admin panel

### Adminni sozlash

1. `.env` faylida `ADMIN_IDS` bo'sh bo'lsa, botni ishga tushiring.
2. Botga `/id` yuboring — Telegram ID raqamingiz chiqadi.
3. `.env` faylida:

   ```dotenv
   ADMIN_IDS=123456789
   ```

   Bir nechta admin: `ADMIN_IDS=123456789,987654321`.

4. Botni qayta ishga tushiring. Endi `/admin` buyrug'i va admin menyusi ishlaydi.

Agar `/admin` ni oddiy foydalanuvchi yuborsa, bot unga ID'sini va sozlash yo'lini
ko'rsatadi.

### Statistika

**📊 Statistika** quyidagilarni ko'rsatadi:

- jami foydalanuvchilar va bugun faol bo'lganlar;
- testlar soni va o'rtacha natija;
- tugatilgan darslar;
- bugungi AI so'rovlari;
- fanlar, darslar va savollar soni.

### Xabar yuborish

1. **📢 Xabar yuborish** tugmasini bosing.
2. Matnni yozing (1–3000 belgi).
3. Ko'rinishni tekshiring va **✅ Yuborish** ni bosing.
4. Jarayonni **❌ Bekor qilish** yoki `/cancel` bilan to'xtatish mumkin.
5. Yakunda yuborilgan va xato bo'lgan xabarlar soni ko'rsatiladi.

Bildirishnomalarni o'chirgan foydalanuvchilarga xabar yuborilmaydi. Telegram
tezlik limiti yuzaga kelsa, bot kutib qayta urinadi.

### Baza zaxirasi va CSV eksport

- **💾 Baza zaxirasi** — `/backup` yoki admin paneldagi shu tugma. Bot SQLite
  bazasining izchil nusxasini yaratib, `.db` fayl sifatida yuboradi. Nusxa WAL
  rejimida ham to'g'ri olinadi.
- **📤 CSV eksport** — `/export` yoki paneldagi tugma. Foydalanuvchilar jadvali
  (ism, XP, tugatilgan darslar, testlar, o'rtacha va eng yaxshi natija) `CSV`
  faylida yuboriladi; Excel va Google Sheets'da ochiladi.
- Nusxalar `BACKUP_DIR` papkasida saqlanadi (standart: loyihadagi `backups/`).
  So'nggi 5 ta fayl qoladi, eskilari avtomatik o'chiriladi. CSV fayl yuborilgach
  serverdan o'chiriladi.
- **Tiklash:** botni to'xtating, zaxira faylini `.env` dagi `DATABASE_PATH`
  ko'rsatgan fayl o'rniga qo'ying va botni qayta ishga tushiring.
- Zaxira faylida foydalanuvchilarning shaxsiy ma'lumotlari bor — uni ochiq joyda
  saqlamang va uchinchi shaxslarga yubormang.

## Ma'lumotlar va maxfiylik

- Profil, test natijalari, dars progressi va AI suhbat tarixi bot egasining
  serveridagi SQLite bazasida saqlanadi.
- AI kaliti sozlangan bo'lsa, savol matni va dars konteksti javob olish uchun
  tanlangan AI provayderiga yuboriladi.
- Bot tokeni va AI kaliti ochiq kodda saqlanmaydi; ular faqat `.env` faylida yoki
  hostingning environment o'zgaruvchilarida bo'ladi.
- `.env` fayli va baza GitHub'ga yuborilmaydi. Admin olgan zaxira nusxalari ham
  shaxsiy ma'lumotni o'z ichiga oladi — ularni xavfsiz saqlash admin zimmasida.
- Render bepul tarifida baza restartda yangilanishi mumkin; doimiy saqlash uchun
  serverga joylash qo'llanmasidagi Oracle usulidan yoki `/backup` dan foydalaning.

## Ko'p uchraydigan savollar

**Bot javob bermayapti.**
Internet aloqasini va botning ishlab turganini tekshiring. PyCharm'da qayta
**Run** qiling. Bir vaqtda ikkita bot nusxasi ishlamasin.

**«Conflict: terminated by other getUpdates request» chiqdi.**
Bot ikki joyda ishga tushirilgan. Ikkinchi jarayonni to'xtating.

**Test tugmalari eskirgan deb javob beryapti.**
Test holati bot qayta ishga tushganda tozalanadi. **📝 Testlar** orqali yangi test
boshlang.

**AI javob bermayapti.**
Kunlik limit tugagan bo'lishi mumkin yoki AI kaliti sozlanmagan. Limit ertaga
yangilanadi; kalitsiz rejimda dars bazasidan javob beriladi.

**Admin panel ko'rinmayapti.**
`ADMIN_IDS` to'g'ri to'ldirilganini va bot qayta ishga tushirilganini tekshiring.
`/id` orqali ID'ni aniqlang.

**Kunlik eslatma kelmayapti.**
Eslatma faqat o'sha kuni **📅 Kunlik reja** ochilgan, maqsad bajarilmagan va
bildirishnomalar yoqilgan foydalanuvchilarga yuboriladi. Sozlamalarda
bildirishnoma yoqilganini tekshiring. Serverda eslatmalar o'chirilgan bo'lishi ham
mumkin (`DAILY_REMINDERS_ENABLED=false`).

**Dars yoki test qo'shmoqchiman.**
`content/seed_data.json` faylini tahrirlab, botni qayta ishga tushiring. Har bir
darsda `summary`, `key_points`, `level` va `duration_min` bo'lishi kerak. Batafsil:
[LOYIHA.md](LOYIHA.md).

**Botni serverga qanday joylayman?**
[Serverga joylash qo'llanmasi](SERVERGA_JOYLASH.md) dan foydalaning. Render bepul
tarifi tez sinov uchun, Oracle Cloud Always Free esa doimiy baza uchun mos.

**Render'da bot javob bermayapti yoki uxlab qolyapti.**
Render bepul xizmati 15 daqiqa harakatsizlikdan keyin uxlaydi. UptimeRobot bilan
`/health` manzilini har 5 daqiqada tekshirib turing. Birinchi xabar 30–60 soniya
kechikishi mumkin.

**Serverdan keyin natijalarim yo'qoldi.**
Render bepul tarifida doimiy disk yo'q. Doimiy saqlash uchun Oracle Cloud Always
Free + Docker usulini tanlang. Muvaqqat yechim sifatida admin `/backup` buyrug'i
bilan bazani muntazam saqlab turing — restartdan keyin shu faylni tiklash mumkin.
