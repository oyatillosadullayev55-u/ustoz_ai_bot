# `services/ai_service.py` — AI provayder va zaxira javob

**Yo'l:** [`services/ai_service.py`](../../../services/ai_service.py)
**Vazifasi:** OpenAI-mos API orqali javob olish va xatolikda dars bazasidan javob qaytarish.

## Asosiy qismlar

| Qism | Vazifasi |
|---|---|
| `SYSTEM_PROMPT` | UstozAI xarakteri, o'zbek tili, qisqalik va xavfsizlik qoidalari |
| `LEVEL_NAMES` | Daraja kodini o'zbekcha nomga aylantiradi |
| `AIServiceError` | Provayder xatosini bildiruvchi ichki xato |
| `_call_provider(...)` | HTTP so'rov, timeout va javob formatini tekshirish |
| `_fallback_reply(...)` | Dars bazasidan mos parcha tayyorlash |
| `ask_tutor(...)` | `(javob, manba)` qaytaruvchi asosiy funksiya |

## `ask_tutor` mantiqi

```text
ai_configured?
├── ha → _call_provider
│        ├── muvaffaqiyat → ("javob", "ai")
│        └── AIServiceError → dars bazasi + ogohlantirish → ("javob", "lessons")
└── yo'q → dars bazasi + izoh → ("javob", "lessons")
```

## Provayder so'rovi

- Manzil: `{AI_BASE_URL}/chat/completions`.
- Header: `Authorization: Bearer <AI_API_KEY>` — kalit faqat shu yerda, logga yozilmaydi.
- Timeout: `AI_TIMEOUT` (`aiohttp.ClientTimeout`).
- `temperature=0.5`, `max_tokens=AI_MAX_TOKENS`.
- Tarix xabarlari 1200 belgigacha qisqartiriladi.
- HTTP 200 bo'lmasa, JSON formati noto'g'ri bo'lsa yoki javob bo'sh bo'lsa `AIServiceError`.

## Zaxira javob

1. Savoldan kalit so'zlar ajratiladi (`extract_tokens`).
2. `search_lessons(question, limit=2)` bilan mos darslar topiladi.
3. Har bir darsdan kalit so'z atrofidagi 600 belgilik parcha olinadi.
4. Mos dars bo'lmasa, mavjud fanlar ro'yxati ko'rsatiladi.
5. Javob oxirida AI kaliti yo'qligi yoki provayder xatosi haqida izoh qo'shiladi.

## Xavfsizlik

- AI javobi handlerda `html.escape` qilinadi.
- Provayder javobi uzunligi handlerda 3900 belgi bilan cheklanadi.
- Xato loglarida API kaliti, token yoki foydalanuvchi maxfiy ma'lumoti yo'q.
- Promptda xavfli yoki haqoratli kontent bermaslik qoidasi bor.
