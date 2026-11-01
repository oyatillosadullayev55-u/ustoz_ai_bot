# `services/daily.py` — kunlik sovg'a va missiya mantiqi

**Yo'l:** [`services/daily.py`](../../../services/daily.py)
**Vazifasi:** sovg'a miqdori, seriya hisobi va haftalik missiya ta'riflari hamda holatini hisoblash.

## Doimiylar

| Nomi | Qiymati | Ma'nosi |
|---|---|---|
| `GIFT_MIN_XP` | 5 | Sovg'aning eng kam XP miqdori |
| `GIFT_MAX_XP` | 25 | Sovg'aning eng ko'p XP miqdori |
| `MISSIONS` | 3 ta `Mission` | Darslar, testlar va AI savollari maqsadlari |
| `MISSION_MAP` | kod → `Mission` | Callback'dan missiyani tez topish |

## Missiyalar

| Kod | Emoji | Sarlavha | Statistika kaliti | Maqsad | Mukofot |
|---|---|---|---|---|---|
| `lessons_3` | 📚 | 3 ta darsni tugatish | `lessons` | 3 | +30 XP |
| `quizzes_2` | 📝 | 2 ta test yechish | `quizzes` | 2 | +25 XP |
| `ai_3` | 🤖 | 3 ta AI savol berish | `ai_messages` | 3 | +20 XP |

## Funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `gift_amount()` | `secrets.randbelow` bilan 5–25 oralig'ida tasodifiy XP |
| `mission_once_key(code)` | `mission:<kod>:<hafta>` bir martalik kalit |
| `daily_streak(days)` | Sanalar to'plamidan ketma-ket kunlar soni |
| `get_mission_states(user_id)` | Har bir missiya uchun progress, bajarilgan va olingan holati |

## Missiya holati

`get_mission_states` haftalik faollikni (`get_weekly_activity`) va olingan
mukofotlarni (`get_claimed_missions`) oladi, so'ng har bir missiya uchun
`MissionState` qaytaradi:

- `progress = min(faollik, target)`;
- `done = progress >= target`;
- `claimed` — shu haftada mukofot olinganmi.

Progress `target` dan oshmaydi, shuning uchun UI'da `5/3` kabi ortiqcha son
chiqmaydi. Mukofotni berish `handlers/daily.py` da `reward()` va
`mission_once_key()` orqali amalga oshiriladi.
