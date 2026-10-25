# `docker-compose.yml` — lokal va server uchun konteyner

**Yo'l:** [`docker-compose.yml`](../../../docker-compose.yml)
**Vazifasi:** botni bitta buyruq bilan ishga tushirish va bazani/loglarni serverda saqlash.

## Xizmat

```yaml
services:
  bot:
    build: .
    container_name: ustozai-bot
    restart: unless-stopped
    env_file: .env
    environment:
      PORT: "8080"
      DATABASE_PATH: /app/data/ustoz_ai.db
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

| Sozlama | Ma'nosi |
|---|---|
| `restart: unless-stopped` | Server qayta yuklansa yoki jarayon yiqilsa, konteyner qayta ishga tushadi |
| `env_file: .env` | Token va AI kaliti faqat `.env` dan o'qiladi |
| `PORT=8080` | Health server shu portda tinglaydi |
| `DATABASE_PATH` | Baza konteyner ichida `/app/data` da |
| `ports` | Port faqat serverda ochiladi; bot polling uchun tashqi port shart emas |
| `volumes` | `./data` va `./logs` hostda saqlanadi — restartda ma'lumot yo'qolmaydi |

## Ishga tushirish

```powershell
Copy-Item .env.example .env
notepad .env          # BOT_TOKEN, ADMIN_IDS
docker compose up -d --build
docker compose logs -f
```

Tekshirish:

```powershell
curl http://127.0.0.1:8080/health
```

To'xtatish:

```powershell
docker compose down
```

## Healthcheck

Compose `python -c "urllib.request.urlopen('http://127.0.0.1:8080/health')"` bilan
har 30 soniyada serverni tekshiradi. 3 marta ketma-ket xato bo'lsa, konteyner nosog'lom
deb belgilanadi. `start_period: 30s` birinchi ishga tushishga vaqt beradi.

## Muhim jihatlar

- `.env` fayli obrazga tushmaydi (`.dockerignore`), faqat ish vaqtida ulanadi.
- `data/` papkasi `.gitignore` da; baza repoga yuborilmaydi.
- Eslatmalar va health server bitta jarayonda ishlaydi; alohida worker kerak emas.
- Bir vaqtda ikki nusxa ishga tushirilmasin — Telegram polling `Conflict` xatosini beradi.

To'liq server qo'llanmasi: [`docs/SERVERGA_JOYLASH.md`](../../SERVERGA_JOYLASH.md).
