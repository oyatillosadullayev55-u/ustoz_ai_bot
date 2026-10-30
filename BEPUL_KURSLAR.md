# 🎓 UstozAI — Dasturlash yo'nalishlari va bepul kurslar

Ushbu hujjatda botga integratsiya qilingan **Dasturlash** yo'nalishlari va **15 ta bepul kurs** haqida to'liq ma'lumot keltirilgan. Barcha materiallar bot ichida — tashqi havolalarsiz — rasmli kartochka, batafsil matn va 4 variantli test ko'rinishida beriladi.

---

## 📌 Dasturlash bo'limi birlashtirildi

Barcha dasturlash va IT yo'nalishlari bitta umumiy **«💻 Dasturlash»** fani ostida jamlangan.

Foydalanuvchi botda:
1. **📚 Darslar** bo'limiga kiradi.
2. **💻 Dasturlash** fanini tanlaydi.
3. 21 ta yo'nalish tugmalar ko'rinishida chiqadi.
4. Tanlangan har bir yo'nalish uchun:
   - 🖼️ rasmli kartochka ochiladi;
   - 🎯 darsning maqsadi, qisqa mazmuni va asosiy fikrlari ko'rsatiladi;
   - 📖 batafsil o'qish, ✅ darsni tugatish, 🧠 AI Ustozga savol berish va 📝 test yechish mumkin.

---

## ✨ Yangi: harakat effektlari

Bot endi jonliroq ko'rinadi:
- 👋 `/start` — salomlashish reaksiyasi;
- 📖 dars ochilganda va 📘 batafsil matnda — ko'rsatkich reaksiyalar;
- ⏳ rasm yuborilishidan oldin «🖼️ rasm yuklanmoqda» holati;
- 🎉 dars tugatilganda tabrik reaksiyasi;
- ✅/❌ testda har bir javobga darhol reaksiya, yakunda 🏆/👏/👍/💪;
- ⌨️ AI Ustoz javob tayyorlayotganda doimiy «yozmoqda» indikatori.

---

## 🚀 Yo'nalishlar ro'yxati

| № | Yo'nalish nomi | Tavsif |
|---|---|---|
| 1 | **🐍 Python: O'zgaruvchilar va turlar** | Python sintaksisi va ma'lumot turlari |
| 2 | **🐍 Python: Shart operatorlari** | `if`, `elif`, `else` va mantiqiy tekshiruvlar |
| 3 | **📱 Dart & Flutter: Dart asoslari** | Dart tili va OOP tushunchalari |
| 4 | **📱 Dart & Flutter: Widgetlar** | Flutterda interfeys qurish |
| 5 | **💻 Informatika: Kompyuter tuzilishi** | Protsessor, xotira va qurilmalar |
| 6 | **💻 Informatika: Algoritm asoslari** | Algoritm turlari va blok-sxemalar |
| 7 | **🎯 Prompt Engineering kursi** | Promptlar, RAG va javob formatini boshqarish |
| 8 | **🎨 AI Image Gen kursi** | Matndan sifatli tasvir yaratish |
| 9 | **🎬 AI Video Gen kursi** | Matn va rasmlardan video lavhalar |
| 10 | **🤖 AI Agents kursi** | Avtonom agentlar arxitekturasi |
| 11 | **🔄 Loop Engineering kursi** | Python bilan AI agentlik tizimlari |
| 12 | **📊 Pro Excel kursi** | Formulalar, Pivot, diagramma va dashboard |
| 13 | **🧮 Buxgalteriya kursi** | Debet-kredit, balans, soliq va hisobot |
| 14 | **🛡️ Raqamli xavfsizlik kursi** | Fishing, 2FA va shaxsiy ma'lumotlar himoyasi |
| 15 | **⌨️ Windows buyruqlari (CMD) kursi** | CMD buyruqlari va tarmoq diagnostikasi |
| 16 | **🖥️ Kompyuter arxitekturasi kursi** | Tranzistordan protsessorgacha, xotira ierarxiyasi |
| 17 | **⚙️ Operatsion tizimlar kursi** | Yadro, jarayonlar va xotira boshqaruvi |
| 18 | **🔀 Algoritmlar kursi** | Saralash, qidiruv, rekursiya va graflar |
| 19 | **🗂️ Ma'lumotlar tuzilmasi kursi** | Massiv, stek, navbat, xesh-jadval va daraxt |
| 20 | **🗄️ Ma'lumotlar bazasi (SQL) kursi** | SELECT, JOIN, GROUP BY va indekslar |
| 21 | **🌐 Kompyuter tarmoqlari kursi** | OSI, TCP/IP, IP manzil va DNS |

15 ta kursning to'liq matni, asosiy fikrlari va test savollari [docs/BEPUL_KURSLAR.md](docs/BEPUL_KURSLAR.md) faylida.

---

## 🛠️ Bot arxitekturasi va testlar

Loyiha to'liq tekshiruvdan o'tkazilgan:
- **8 ta fan** (7 ta umumta'lim fani + 1 ta birlashtirilgan «Dasturlash» fani);
- **35 ta to'liq dars** (har biri uchun rasmli kartochka mavjud);
- **140 ta 4 variantli test savoli**;
- Barcha oflayn va handler testlari muvaffaqiyatli o'tgan:
  ```bash
  .\.venv\Scripts\python.exe tests/test_offline.py
  .\.venv\Scripts\python.exe tests/test_handlers_offline.py
  ```

---

## 💡 Botni ishga tushirish (Run)

```bash
# Virtual muhitni faollashtirish
.\.venv\Scripts\activate

# Botni ishga tushirish
python bot.py
```
