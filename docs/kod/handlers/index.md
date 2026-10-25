# `handlers` paketi — umumiy ko'rinish

**Yo'l:** [`handlers/`](../../../handlers)
**Vazifasi:** Telegram yangilanishlarini qabul qiluvchi routerlar va FSM oqimlari.

## Fayllar

| Fayl | Router | Vazifasi |
|---|---|---|
| [`start.py`](start.md) | `start` | `/start`, ro'yxatdan o'tish |
| [`ai_tutor.py`](ai_tutor.md) | `ai_tutor` | AI Ustoz rejimi |
| [`lessons.py`](lessons.md) | `lessons` | Darslar, qisqa kartochka, batafsil matn, navigatsiya va `/qidiruv` |
| [`quizzes.py`](quizzes.md) | `quizzes` | 4 variantli testlar |
| [`progress.py`](progress.md) | `progress` | Statistika |
| [`daily_plan.py`](daily_plan.md) | `daily_plan` | Kunlik reja |
| [`settings.py`](settings.md) | `user_settings` | Daraja va bildirishnomalar |
| [`admin.py`](admin.md) | `admin` | Admin panel va broadcast |
| [`common.py`](common.md) | — | Umumiy yordamchilar |
| [`menu.py`](menu.md) | `menu` | Zaxira handlerlar |

## Routerlar tartibi

`bot.py` routerlarni quyidagi tartibda ulaydi:

```text
start → ai_tutor → lessons → quizzes → progress → daily_plan → settings → admin → menu
```

`menu` eng oxirida turadi, chunki uning `@router.message(F.text)` va `@router.callback_query()` handlerlari boshqa routerlar tanimagan yangilanishlarni ushlaydi.

## FSM

- Barcha holatlar `StatesGroup` bilan e'lon qilinadi.
- `MemoryStorage` ishlatiladi: bot qayta ishga tushsa, tugallanmagan test yoki ro'yxatdan o'tish holati yo'qoladi.
- Har bir bo'limga kirishda `state.clear()` chaqiriladi.
- `lesson:ask` AI rejimida `lesson_context` ni FSM'da saqlaydi; chiqishda u ham
  tozalanadi.

## Xavfsizlik qoidalari

- Har bir handler avval `require_user` yoki `require_user_callback` orqali ro'yxatdan o'tganini tekshiradi.
- Foydalanuvchi matni HTML javobiga chiqarishdan oldin `html.escape` qilinadi.
- Matn uzunligi handlerlarda alohida cheklanadi.
- Callback ma'lumotlari `int` ga aylantirishda `try/except ValueError` bilan tekshiriladi.

`handlers/__init__.py` faqat paket docstring'idan iborat.
