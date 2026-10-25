# `handlers/progress.py` — statistika ekrani

**Yo'l:** [`handlers/progress.py`](../../../handlers/progress.py)
**Vazifasi:** foydalanuvchiga shaxsiy natijalar, streak va so'nggi testlarni ko'rsatish.

## Ko'rsatkichlar

- Tugatilgan darslar;
- yechilgan testlar;
- o'rtacha va eng yuqori natija;
- ketma-ket faol kunlar (`streak`);
- faol kunlar soni;
- AI'ga yozilgan savollar;
- so'nggi 5 ta test natijasi (fan nomi va sana bilan).

## Oqim

1. `📊 Mening natijalarim` tugmasi `require_user` dan keyin statistika matnini yuboradi.
2. `stats:refresh` callback xuddi shu matnni `safe_edit` bilan yangilaydi.
3. Sana `format_local_date()` orqali `dd.mm.yyyy` ko'rinishida chiqariladi.

## Ma'lumot manbalari

| Funksiya | Fayl |
|---|---|
| `get_user_stats` | `database/progress.py` |
| `get_activity_stats` | `database/progress.py` |
| `get_recent_results` | `database/progress.py` |

## Xavfsizlik

- Foydalanuvchi ismi va fan nomi HTML uchun escape qilinadi.
- Faqat joriy foydalanuvchining ma'lumotlari so'raladi; `user_id` sessiyadan emas, bazadagi yozuvdan olinadi.
