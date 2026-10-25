# `render.yaml` — Render Blueprint

**Yo'l:** [`render.yaml`](../../../render.yaml)
**Vazifasi:** Render'da bepul web-service yaratish uchun infrastruktura ta'rifi.

## Xizmat

```yaml
services:
  - type: web
    name: ustozai-bot
    runtime: docker
    plan: free
    region: frankfurt
    dockerfilePath: ./Dockerfile
    dockerContext: .
    healthCheckPath: /health
    autoDeploy: true
```

| Maydon | Ma'nosi |
|---|---|
| `type: web` | Render port tinglaydigan xizmat kutadi |
| `runtime: docker` | Loyihadagi `Dockerfile` ishlatiladi |
| `plan: free` | Bepul tarif; 15 daqiqa harakatsizlikdan keyin uxlaydi |
| `region: frankfurt` | O'zbekistonga yaqin mintaqa |
| `healthCheckPath` | `/health` 200 qaytishi kerak |
| `autoDeploy` | `main` branch'ga push bo'lsa avtomatik qayta deploy |

## Muhit o'zgaruvchilari

| Kalit | Qiymat | Maxfiy |
|---|---|---|
| `BOT_TOKEN` | Render panelida kiritiladi | ha |
| `ADMIN_IDS` | Render panelida kiritiladi | ha |
| `AI_ENABLED` | `false` | yo'q |
| `AI_API_KEY` | Render panelida kiritiladi | ha |
| `AI_BASE_URL` | `https://api.openai.com/v1` | yo'q |
| `AI_MODEL` | `gpt-4o-mini` | yo'q |
| `DATABASE_PATH` | `/app/data/ustoz_ai.db` | yo'q |
| `DAILY_REMINDERS_ENABLED` | `true` | yo'q |
| `DAILY_REMINDER_HOUR` | `19` | yo'q |

`sync: false` — qiymat repoda saqlanmaydi, Render panelida bir marta kiritiladi va
keyingi deploylarda o'zgarmaydi. Token yoki AI kaliti hech qachon `render.yaml` ga
yozilmaydi.

## Deploy qadamlari

1. Render akkauntiga kirish va GitHub'ni ulash.
2. **New → Blueprint** → `ustoz_ai_bot` repozitoriyasini tanlash.
3. Render `render.yaml` ni o'qib, xizmatni tayyorlaydi.
4. `BOT_TOKEN`, `ADMIN_IDS` va kerak bo'lsa `AI_API_KEY` ni kiritish.
5. **Apply** → birinchi build va deploy.
6. `https://<nom>.onrender.com/health` ochib, `status: ok` ni tekshirish.

## Bepul tarif cheklovlari

- 15 daqiqa so'rov bo'lmasa xizmat uxlaydi; keyingi `/start` da qayta uyg'onadi.
- Doimiy disk yo'q: SQLite baza har deploy yoki restartda yangidan yaratiladi.
- Doimiy saqlash kerak bo'lsa, Oracle Cloud Always Free + Docker ishlatiladi.

To'liq qo'llanma: [`docs/SERVERGA_JOYLASH.md`](../../SERVERGA_JOYLASH.md).
