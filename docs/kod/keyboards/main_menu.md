# `keyboards/main_menu.py` — bosh menyu

**Yo'l:** [`keyboards/main_menu.py`](../../../keyboards/main_menu.py)
**Vazifasi:** doimiy (reply) klaviaturalar va ularning matnli doimiylari.

## Tugma doimiylari

| Doimiylik | Matn |
|---|---|
| `BTN_AI_TUTOR` | `🧠 AI Ustoz` |
| `BTN_LESSONS` | `📚 Darslar` |
| `BTN_QUIZZES` | `📝 Testlar` |
| `BTN_PROGRESS` | `📊 Mening natijalarim` |
| `BTN_DAILY_PLAN` | `📅 Kunlik reja` |
| `BTN_SETTINGS` | `⚙️ Sozlamalar` |
| `BTN_AI_EXIT` | `⬅️ Chiqish` |

`MAIN_MENU_TEXTS` — oltita asosiy tugma matni to'plami. `start.py` va `ai_tutor.py` foydalanuvchi matni menyu tugmasimi yoki yo'qmi shu bilan tekshiradi.

## Funksiyalar

- `get_main_menu_keyboard()` — 2 ustunli, 3 qatorli reply klaviatura; `resize_keyboard=True`.
- `get_ai_mode_keyboard()` — faqat `⬅️ Chiqish` tugmasi; input maydonida "Savolingizni yozing..." placeholder.

## Muhim jihat

Reply klaviatura matnlari handlerlardagi `F.text == BTN_*` filtrlariga bog'langan. Matnni o'zgartirsangiz, faqat shu fayldagi doimiyni o'zgartirish kifoya.
