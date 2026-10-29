# UstozAI botini bepul serverga joylash

Bu qo'llanma botni 24/7 ishlaydigan bepul serverga chiqarishni ko'rsatadi. Ikki
yo'l bor:

| Usul | Afzalligi | Kamchiligi |
| --- | --- | --- |
| **Render (bepul web-service)** | 5 daqiqada ishga tushadi, GitHub'dan avtomatik deploy | 15 daqiqa harakatsizlikdan keyin uxlaydi; doimiy disk yo'q, SQLite bazasi restartda o'chadi |
| **Oracle Cloud Always Free** | Doimiy disk, baza saqlanadi, cheklovsiz 24/7 | Hisob yaratish va bank kartasi bilan tasdiqlash kerak; Docker bilan ishlash |

Sinov va demo uchun Render qulay. Haqiqiy foydalanuvchilar va natijalarni saqlash
kerak bo'lsa, Oracle Cloud'ni tanlang.

> **Muhim:** bot Telegram'ning polling rejimida ishlaydi. Bir vaqtda faqat **bitta**
> nusxa ishlashi mumkin. Serverga chiqargandan keyin lokal PyCharm'dagi botni
> to'xtating, aks holda `Conflict: terminated by other getUpdates request` xatosi
> chiqadi.

---

## 1. Render'ga joylash (bepul)

### 1.1. Kerakli narsalar

- GitHub'da `ustoz_ai_bot` reposi (kod push qilingan bo'lishi kerak).
- [Render](https://render.com) hisobi — GitHub bilan kirish mumkin.
- BotFather bergan `BOT_TOKEN`.
- Admin Telegram ID (ixtiyoriy, `/id` orqali olinadi).

### 1.2. Bir tugma bilan deploy

Quyidagi havola `render.yaml` faylini o'qib, web-service yaratadi:

[Render'da deploy qilish](https://render.com/deploy?repo=https://github.com/oyatillosadullayev55-u/ustoz_ai_bot)

1. Havolani oching va GitHub bilan kiring.
2. **Apply** tugmasini bosing.
3. Render so'ragan qiymatlarni kiriting:
   - `BOT_TOKEN` — majburiy, BotFather tokeni.
   - `ADMIN_IDS` — admin Telegram ID'lari, vergul bilan (bo'sh qoldirish mumkin).
   - `AI_API_KEY` — ixtiyoriy; bo'sh bo'lsa AI Ustoz dars bazasidan javob beradi.
4. **Create Web Service** ni bosing. Render `Dockerfile` asosida image quradi.
5. Deploy tugagach, xizmat manzili ochiladi: `https://<nomi>.onrender.com`.
   Brauzerda `/health` ni oching — `{"status": "ok", ...}` ko'rinishi kerak.
6. Telegramda botni ochib `/start` yuboring.

> **Muhim:** agar xizmat `render.yaml` orqali emas, **New Web Service** tugmasi bilan
> qo'lda yaratilgan bo'lsa, environment o'zgaruvchilari avtomatik qo'shilmaydi.
> **Settings → Environment** bo'limida quyidagilarni qo'lda kiriting:
>
> | Kalit | Qiymat |
> | --- | --- |
> | `BOT_TOKEN` | BotFather bergan token (majburiy) |
> | `ADMIN_IDS` | Telegram ID, faqat raqamlar (ixtiyoriy) |
> | `DATABASE_PATH` | `/app/data/ustoz_ai.db` |
> | `AI_ENABLED` | `false` (AI kaliti bo'lsa `true`) |
> | `DAILY_REMINDERS_ENABLED` | `true` |
>
> **Runtime: Docker** bo'lishi kerak; start command bo'sh qoladi, chunki buyruq
> `Dockerfile` ichidagi `CMD ["python", "bot.py"]` dan olinadi.

### 1.3. Render sozlamalari

`render.yaml` quyidagilarni avtomatik sozlaydi:

- `runtime: docker` — Python versiyasi `Dockerfile` orqali boshqariladi.
- `healthCheckPath: /health` — Render bot tirikligini tekshiradi.
- `autoDeploy: true` — `main` branch'ga har push'da qayta deploy qiladi.
- `DATABASE_PATH=/app/data/ustoz_ai.db`.
- `AI_ENABLED=false` — AI kaliti kiritilsa, dashboard'da `true` qiling.

`PORT` ni **qo'lda kiritmang**: Render uni o'zi beradi, `services/health_server.py`
shu portni tinglaydi. Lokal ishda `PORT` bo'sh bo'lsa, HTTP server umuman ochilmaydi.

### 1.4. Bepul tarifning cheklovlari

- **Uyqu rejimi:** 15 daqiqa harakatsizlikdan keyin xizmat to'xtaydi. Birinchi
  xabar 30–60 soniya kechikishi mumkin.
- **Doimiy disk yo'q:** har restart yoki yangi deployda SQLite fayli yangidan
  yaratiladi. Foydalanuvchilar, test natijalari va kunlik rejalar yo'qoladi.
- **750 soat/oy:** bitta free web-service uchun odatda yetarli, lekin bir nechta
  xizmat ishlatsangiz limit tugashi mumkin.
- **Resurslar:** free instansiya kichik (512 MB RAM atrofida). Bot uchun yetarli,
  lekin og'ir AI so'rovlarini parallel qilish tavsiya etilmaydi.

Tarif shartlari vaqt o'tishi bilan o'zgarishi mumkin — joriy ma'lumotni Render
dashboard'ida tekshiring.

### 1.5. Uyqu rejimini kamaytirish (UptimeRobot)

1. [UptimeRobot](https://uptimerobot.com) da bepul hisob yarating.
2. **Add New Monitor** → **HTTP(s)**.
3. URL: `https://<nomi>.onrender.com/health`.
4. Interval: **5 daqiqa**.
5. Saqlang. Har 5 daqiqadagi so'rov botni uyg'oq tutadi.

Bepul UptimeRobot odatda 50 tagacha monitor va 5 daqiqalik intervalni beradi.
`cron-job.org` ham xuddi shunday ishlaydi.

### 1.6. Yangilanish va loglar

- Kodni GitHub'ga push qilsangiz, Render avtomatik qayta deploy qiladi.
- Dashboard → **Logs** bo'limida `UstozAI ishga tushdi` va xatolarni ko'rasiz.
- Environment o'zgaruvchilarini **Environment** bo'limida tahrirlang; o'zgarishdan
  keyin **Manual Deploy → Deploy latest commit** qiling.
- Token yoki AI kaliti o'zgarsa, faqat Render'dagi environment qiymatini yangilang.
  Kodga yozmang.

### 1.6.1. `Deploy failed` — `Exited with status 1`

Bu xabar bot ishga tushish paytida to'xtaganini bildiradi. Deploy sahifasidagi
loglarni **eng pastga** aylantirib, quyidagi qatorlarni toping:

1. `[START] BOT_TOKEN: ...` — birinchi qator. Token qiymati emas, faqat bor-yo'qligi
   ko'rsatiladi.
   - `BOT_TOKEN: YO'Q` → **Settings → Environment** bo'limida `BOT_TOKEN` qo'shing.
   - `BOT_TOKEN: bor`, lekin keyin `401 Unauthorized` → token noto'g'ri yoki
     BotFather'da `/revoke` qilingan. Yangi tokenni environment'ga yozing.
2. `[XATO] BOT_TOKEN topilmadi...` → token kiritilmagan.
3. `ADMIN_IDS ...` xatosi → `ADMIN_IDS` faqat raqamlardan iborat bo'lsin
   (masalan `123456789`, vergul bilan bir nechta).
4. `Permission denied` yoki baza xatosi → `DATABASE_PATH=/app/data/ustoz_ai.db`
   ekanini tekshiring; bu papka `Dockerfile` ichida yaratiladi.
5. `Conflict: terminated by other getUpdates request` → bot ikkinchi joyda ham
   ishlayapti. Lokal PyCharm'dagi botni to'xtating.
6. Xizmat **Runtime: Docker** ekanini tekshiring. Python runtime tanlangan bo'lsa,
   qo'lda `pip install`/start command sozlash kerak bo'ladi — Docker'ga o'tish osonroq.

So'ng **Manual Deploy → Deploy latest commit** ni bosing. Logda quyidagilar
ko'rinishi kerak:

```text
[START] BOT_TOKEN: bor | ADMIN_IDS: bor | PORT: 10000
Health server 0.0.0.0:10000 manzilida ishga tushdi.
UstozAI ishga tushdi: @FlutterProBot
```

Oxirgi qatorda bot username'i chiqsa, deploy muvaffaqiyatli. `/health` manzili
`{"status":"ok"}` qaytaradi.

### 1.7. Render'da tekshirish

1. `https://<nomi>.onrender.com/health` → `{"status":"ok"}`.
2. Telegramda `/start` → ro'yxatdan o'tish ishlaydi.
3. **📚 Darslar** → rasmli kartochka, **📖 Batafsil o'qish**, **➡️ Keyingi dars**.
4. **📝 Testlar** → 5 savol → natija va xatolar tahlili.
5. **🧠 AI Ustoz** → savol; dars kartochkasidagi **🧠 AI Ustozga so'rash** ham ishlaydi.
6. Admin sifatida `/admin` → statistika va xabar yuborish.

---

## 2. Oracle Cloud Always Free (doimiy baza)

Bu usulda bot Oracle Cloud'ning bepul virtual mashinasida Docker Compose bilan
ishlaydi. SQLite bazasi `data/ustoz_ai.db` faylida saqlanadi va restartda
yo'qolmaydi.

### 2.1. Hisob va VM yaratish

1. [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/) da hisob yarating.
   Ro'yxatdan o'tishda bank kartasi so'raladi (tekshiruv uchun; Always Free
   resurslar uchun to'lov olinmaydi).
2. **Compute → Instances → Create Instance**.
3. Image: **Ubuntu 24.04** (yoki 22.04).
4. Shape: **Ampere A1.Flex** (1–2 OCPU, 6–12 GB RAM) yoki **VM.Standard.E2.1.Micro**
   (Always Free). Ampere ba'zi regionlarda band bo'lishi mumkin; micro ham bot uchun
   yetarli.
5. SSH kalitini yuklang yoki yaratib, `.ssh` papkasida saqlang.
6. **Create** → public IP manzilini yozib oling.

### 2.2. Serverga ulanish

PowerShell yoki Git Bash:

```bash
ssh ubuntu@<SERVER_IP>
```

Keyingi buyruqlar serverda bajariladi.

### 2.3. Docker o'rnatish

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu
```

Chiqib, qayta kiring (`exit` → `ssh ...`), shunda `docker` guruhi huquqi faollashadi.

### 2.4. Loyihani joylashtirish

```bash
git clone https://github.com/oyatillosadullayev55-u/ustoz_ai_bot.git
cd ustoz_ai_bot
cp .env.example .env
nano .env
```

`.env` ichida kamida:

```dotenv
BOT_TOKEN=BotFather_bergan_token
ADMIN_IDS=sizning_telegram_id
AI_ENABLED=false
AI_API_KEY=
DATABASE_PATH=ustoz_ai.db
```

Saqlash: `Ctrl + O`, `Enter`, `Ctrl + X`.

Docker konteyneri `10001` UID bilan ishlaydi, shuning uchun papkalarni tayyorlang:

```bash
mkdir -p data logs
sudo chown -R 10001:10001 data logs
chmod 600 .env
```

Ishga tushirish:

```bash
docker compose up -d --build
docker compose logs -f
```

Logda quyidagilar ko'rinishi kerak:

```text
database.seed | Kontent yuklandi: 8 fan, 35 dars, 140 savol.
bot | UstozAI ishga tushdi: @...
```

`Ctrl + C` faqat loglarni to'xtatadi; konteyner fonda ishlashda davom etadi.

### 2.5. Health-check va firewall

Konteyner ichida `http://127.0.0.1:8080/health` ishlaydi. Tashqaridan tekshirish
uchun Oracle **Networking → VCN → Security Lists → Ingress Rules** bo'limida
TCP `8080` portini oching (manba: `0.0.0.0/0` yoki UptimeRobot IP'lari).

```bash
curl http://127.0.0.1:8080/health
curl http://<SERVER_IP>:8080/health
```

Telegram polling uchun tashqi port ochish shart emas — bot o'zi Telegram'ga
ulanadi. 8080 ni faqat monitoring uchun ochish mumkin.

### 2.6. Yangilash

```bash
cd ustoz_ai_bot
git pull
docker compose up -d --build
docker compose logs -f --tail 50
```

Baza `data/` papkasida bo'lgani uchun yangilanishda saqlanadi.

### 2.7. Zaxira nusxa

```bash
cd ustoz_ai_bot
docker compose exec bot python -c "import sqlite3; c=sqlite3.connect('/app/data/ustoz_ai.db'); c.execute(\"VACUUM INTO '/app/data/backup.db'\"); c.close()"
docker cp ustozai-bot:/app/data/backup.db ./ustoz_ai_backup_$(date +%F).db
```

Yoki konteynerni qisqa to'xtatib, faylni nusxalang:

```bash
docker compose stop bot
cp data/ustoz_ai.db ustoz_ai_backup_$(date +%F).db
docker compose start bot
```

### 2.8. Avtomatik ishga tushish

`docker-compose.yml` da `restart: unless-stopped` bor. Docker xizmati server
yoqilganda avtomatik ishga tushadi (`systemctl enable --now docker`), konteyner
ham qayta tiklanadi.

### 2.9. Oracle'da tekshirish

1. `docker compose ps` — holat `Up` bo'lishi kerak.
2. `curl http://127.0.0.1:8080/health` — `{"status":"ok"}`.
3. Telegramda `/start`, darslar, testlar va AI Ustozni tekshiring.
4. `docker compose logs --tail 100` da xato bo'lmasligi kerak.

---

## 3. Lokal Docker sinovi (Windows)

Docker Desktop o'rnatilgan bo'lsa:

```powershell
Copy-Item .env.example .env
notepad .env
docker compose up -d --build
docker compose logs -f
```

- Health: `http://localhost:8080/health`.
- Baza: loyihadagi `data/ustoz_ai.db` (git'ga kirmaydi).
- To'xtatish: `docker compose down` (baza saqlanadi).
- Qayta qurish: `docker compose up -d --build`.

Windows'da `data` papkasidagi fayllarga Docker Desktop ruxsat beradi. Linux
serverda yuqoridagi `chown 10001:10001` qadamini unutmang.

---

## 4. Xavfsizlik

- `BOT_TOKEN` va `AI_API_KEY` faqat `.env` yoki hosting environment'ida saqlanadi.
  Kodda, README'da, skrinshotda va GitHub'da bo'lmasligi kerak.
- `.env` fayliga faqat egasi o'qiy oladigan huquq bering: `chmod 600 .env`.
- Token oshkor bo'lsa, darhol BotFather'da `/revoke` qiling va yangi tokenni
  hosting environment'iga yozing.
- Serverda SSH uchun parol emas, kalit ishlating; `root` bilan to'g'ridan-to'g'ri
  kirishni yopib qo'ying.
- Oracle Security List'da faqat kerakli portlarni oching (22 va ixtiyoriy 8080).
- AI kaliti bo'lsa, provider dashboard'ida sarf limitini belgilang.
- `.env`, `data/`, `logs/` va `*.db` GitHub'ga tushmasligini `git status` bilan
  tekshiring.

---

## 5. Nosozliklarni tuzatish

| Xato / holat | Sababi | Yechim |
| --- | --- | --- |
| `Conflict: terminated by other getUpdates request` | Bot ikki joyda ishlayapti | Lokal PyCharm'dagi botni to'xtating yoki eski Render instansiyasini o'chiring |
| `Unauthorized` / `401` | Token noto'g'ri yoki bekor qilingan | BotFather'dan yangi token oling, environment'ni yangilang |
| Render: `Exited with status 1` | Token yo'q, noto'g'ri yoki ishga tushishda xato | Log oxiridagi `[START]` va `[XATO]` qatorlarini o'qing; 1.6.1 bo'limiga amal qiling |
| `[START] BOT_TOKEN: YO'Q` | Render environment'da token berilmagan | Settings → Environment → `BOT_TOKEN` qo'shing va qayta deploy qiling |
| `BOT_TOKEN ni rad etdi (401 Unauthorized)` | Token bekor qilingan yoki xato ko'chirilgan | BotFather'da `/revoke` qilib yangi token oling va environment'ni yangilang |
| Render'da `Application failed to respond` | `PORT` tinglanmayapti yoki health server ishlamadi | `PORT` ni qo'lda yozmang; loglarda `Health server ... ishga tushdi` borligini tekshiring |
| `/health` 502 | Konteyner hali ko'tarilmagan yoki qulagan | `docker compose logs --tail 100`; `docker compose ps` |
| `Permission denied` bazaga yozishda (Linux) | `data/` papkasi UID 10001 ga tegishli emas | `sudo chown -R 10001:10001 data logs` |
| Render restartdan keyin ma'lumot yo'q | Bepul tarifda doimiy disk yo'q | Oracle + Docker'ga o'ting yoki tashqi bazadan foydalaning |
| Bot uxlab qolyapti (Render) | Free web-service spin-down | UptimeRobot bilan `/health` ni har 5 daqiqada chaqiring |
| `database is locked` | Bir vaqtda bir nechta bot nusxasi | Faqat bitta konteyner ishlashiga ishonch qiling |
| Docker build'da `pip install` xatosi | Python yoki paket versiyasi mos emas | `docker compose build --no-cache`; `requirements.txt` versiyalarini tekshiring |

Qo'shimcha loglar:

```bash
docker compose logs -f bot
docker compose exec bot ls -la /app/data /app/logs
```

---

## 6. CI va avtomatik deploy

- GitHub Actions (`.github/workflows/ci.yml`) har push'da Ruff va ikkala offline
  testni ishga tushiradi. Testlar token talab qilmaydi.
- Render `autoDeploy: true` bilan `main` branch'dagi har bir muvaffaqiyatli push'dan
  keyin qayta deploy qiladi.
- Oracle'da avtomatik deploy kerak bo'lsa, GitHub Actions'dan SSH orqali
  `git pull && docker compose up -d --build` buyrug'ini ishga tushirish mumkin.
  Buning uchun deploy kalitini GitHub Secrets'da saqlang va uni hech qachon kodga
  yozmang.

---

## 7. Qisqa cheklist

- [ ] Lokal bot to'xtatilgan (polling conflict bo'lmasin).
- [ ] `BOT_TOKEN` va `ADMIN_IDS` hosting environment'ida kiritilgan.
- [ ] `/health` 200 qaytaradi.
- [ ] Telegramda `/start`, dars, test va AI ishlaydi.
- [ ] Render bo'lsa: UptimeRobot monitori qo'shilgan.
- [ ] Oracle bo'lsa: `data/` papkasi UID 10001 ga tegishli va zaxira rejasi bor.
- [ ] `.env`, `data/`, `logs/` GitHub'ga tushmagan.
