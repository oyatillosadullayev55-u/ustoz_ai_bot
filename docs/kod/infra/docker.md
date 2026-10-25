# `Dockerfile` va `.dockerignore` — konteyner obrazi

**Yo'llar:** [`Dockerfile`](../../../Dockerfile), [`.dockerignore`](../../../.dockerignore)
**Vazifasi:** botni Render, Oracle Cloud yoki lokal Docker'da bir xil muhitda ishga tushirish.

## Dockerfile tuzilishi

| Qadam | Nima qilinadi |
|---|---|
| Asos | `python:3.13-slim` |
| Muhit | `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`, `PYTHONUTF8=1`, `PIP_NO_CACHE_DIR=1` |
| Baza yo'li | `DATABASE_PATH=/app/data/ustoz_ai.db` |
| Foydalanuvchi | `ustozai` (UID/GID 10001), root emas |
| Bog'liqliklar | `requirements.txt` nusxalanadi va `pip install` qilinadi |
| Kod | `COPY --chown=ustozai:ustozai . .` |
| Papkalar | `/app/data` va `/app/logs` yaratilib, egasi `ustozai` qilinadi |
| Port | `EXPOSE 8080` |
| Ishga tushirish | `CMD ["python", "bot.py"]` |

## Nega `PYTHONUTF8=1`

Bot loglarida o'zbekcha apostrof, emoji va boshqa Unicode belgilar bor. Ba'zi
konteyner muhitlarida standart konsol kodlash UTF-8 bo'lmasligi mumkin; u holda
`print()` yoki logging `UnicodeEncodeError` bilan yiqilishi mumkin. `PYTHONUTF8=1`
Python'ning stdin/stdout/stderr oqimlarini UTF-8 rejimida ishlatishni kafolatlaydi.

## Nega non-root

Konteyner ichida bot root huquqisiz ishlaydi. Bu tasodifiy fayl o'zgarishlari yoki
kutubxona zaifligi oqibatini kamaytiradi. `/app/data` va `/app/logs` faqat kerakli
papkalar bo'lib, ularga yozish huquqi `ustozai` ga beriladi.

## `.dockerignore`

Obrazga tushmasligi kerak bo'lgan narsalar:

- `.env` va boshqa maxfiy fayllar (`.env.example` qoladi);
- `.venv`, `__pycache__`, kesh papkalari;
- `*.db`, WAL fayllari, `logs`, `data`;
- `.git`, `.github`, `.idea`, `.run`, `.vscode`;
- `tests`, `docs`, `README.md`;
- `Dockerfile`, `docker-compose.yml`, `render.yaml`.

Natijada obraz kichikroq bo'ladi va token yoki foydalanuvchi bazasi konteynerga
tasodifan tushmaydi.

## Lokal tekshirish

```powershell
docker build -t ustozai-bot .
docker run --rm --env-file .env -p 8080:8080 ustozai-bot
```

Brauzerda `http://127.0.0.1:8080/health` ochilsa, health server ishlayapti. Telegramda
botning `/start` buyrug'i ham javob berishi kerak.

## Bog'liq hujjatlar

- [`docker-compose.yml`](docker-compose.md)
- [`render.yaml`](render.md)
- [`services/health_server.py`](../services/health_server.md)
- [`docs/SERVERGA_JOYLASH.md`](../../SERVERGA_JOYLASH.md)
