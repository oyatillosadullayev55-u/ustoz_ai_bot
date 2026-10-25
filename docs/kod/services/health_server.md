# `services/health_server.py` — health-check serveri

**Yo'l:** [`services/health_server.py`](../../../services/health_server.py)
**Vazifasi:** Render kabi hostinglar uchun kichik HTTP server; bot tirikligini bildiradi.

## Nima uchun kerak

Bot Telegram bilan **polling** rejimida ishlaydi va tashqi portni tinglamaydi. Render
bepul tarifidagi web-service esa port tinglaydigan xizmatni kutadi. Shu sababli bot
ishga tushganda ixtiyoriy ravishda kichik aiohttp server ham ochiladi. U Telegram
yangilanishlarini qabul qilmaydi — faqat hostingning health-check so'roviga javob beradi.

## Funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `_read_port()` | `PORT` muhit o'zgaruvchisini o'qiydi va 1–65535 oralig'ida tekshiradi |
| `_health(request)` | `{"status": "ok", "service": "ustozai-bot", "commit": ...}` JSON qaytaradi |
| `_root(request)` | Oddiy matnli javob: bot ishlayapti va `/start` yuborish kerak |
| `start_health_server()` | `PORT` bo'lsa `web.AppRunner` yaratadi, aks holda `None` |
| `stop_health_server(runner)` | Serverni to'xtatadi va resurslarni tozalaydi |

## Marshrutlar

| Manzil | Javob |
|---|---|
| `/` | `text/plain`: "UstozAI bot ishlayapti..." |
| `/health` | JSON: `status`, `service`, `commit` |
| `/healthz` | `/health` bilan bir xil |

`commit` qiymati `RENDER_GIT_COMMIT` dan olinadi va 12 belgigacha qisqartiriladi; lokal
ishda `local` bo'ladi.

## Ishga tushish sharti

- `PORT` bo'sh yoki noto'g'ri bo'lsa, server **ochilmaydi** va bot odatdagidek ishlaydi.
- `PORT` berilganda server `0.0.0.0:<port>` manzilida tinglaydi.
- Render `PORT` ni avtomatik beradi; Docker Compose uni `8080` qiladi.

## Xavfsizlik

- Server faqat holat haqida ma'lumot qaytaradi; token, baza yo'li yoki foydalanuvchi
  ma'lumoti ko'rsatilmaydi.
- Foydalanuvchi kiritgan ma'lumot qabul qilinmaydi — faqat `GET` so'rovlari mavjud.
- Bot to'xtaganda `stop_health_server()` tozalanadi; Render keyingi deployda yangi
  jarayonni ishga tushiradi.

## Bog'liq hujjatlar

- [`bot.py`](../bot.md) — serverni ishga tushirish va to'xtatish
- [`Dockerfile`](../infra/docker.md) — konteyner ichida `EXPOSE 8080`
- [`render.yaml`](../infra/render.md) — `healthCheckPath: /health`
- [`docs/SERVERGA_JOYLASH.md`](../../SERVERGA_JOYLASH.md) — to'liq joylash qo'llanmasi
