# `requirements.txt` va `requirements-dev.txt` — paketlar

**Yo'llar:** [`requirements.txt`](../../../requirements.txt), [`requirements-dev.txt`](../../../requirements-dev.txt)
**Vazifasi:** ishlab chiqish va ishlatish uchun kerakli Python paketlarini qat'iy versiyalar bilan belgilash.

## Runtime paketlari

| Paket | Versiya | Nima uchun |
|---|---|---|
| `aiogram` | 3.22.0 | Telegram Bot API, routerlar, FSM |
| `aiosqlite` | 0.22.1 | Asinxron SQLite |
| `python-dotenv` | 1.2.4 | `.env` faylini o'qish |

`aiohttp` aiogram bilan birga o'rnatiladi va `services/ai_service.py` da AI so'rovlari uchun ishlatiladi.

## Development paketlari

`requirements-dev.txt`:

```text
-r requirements.txt
ruff==0.17.2
```

## O'rnatish

```bash
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

## Yangilash qoidasi

- Versiyalar `==` bilan qulflangan — turli kompyuterlarda bir xil natija.
- Yangilashdan oldin testlarni ishga tushiring.
- `requirements.txt` o'zgarsa, `requirements-dev.txt` dagi `-r` qatori avtomatik yangi paketni oladi.
