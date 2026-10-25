# `.run/UstozAI Bot.run.xml` — PyCharm Run konfiguratsiyasi

**Yo'l:** [`.run/UstozAI Bot.run.xml`](../../../.run/UstozAI%20Bot.run.xml)
**Vazifasi:** PyCharm'da **Run** tugmasini bosganda `bot.py` ni virtual muhit bilan ishga tushirish.

## Konfiguratsiya mazmuni

| Sozlama | Qiymat |
|---|---|
| Nomi | `UstozAI Bot` |
| Turi | Python |
| Skript | `$PROJECT_DIR$/bot.py` |
| Ish papkasi | `$PROJECT_DIR$` |
| Interpreter | loyiha virtual muhiti (`.venv`) |
| `PYTHONUNBUFFERED` | `1` — loglar darhol konsolga chiqadi |

## Ishga tushirish

1. PyCharm'da loyihani oching.
2. **File → Settings → Project → Python Interpreter** bo'limida `.venv\Scripts\python.exe` tanlanganini tekshiring.
3. Yuqori o'ng burchakda `UstozAI Bot` konfiguratsiyasini tanlang.
4. **Run** (yashil uchburchak) ni bosing.
5. Konsolda `UstozAI ishga tushdi: @...` logi chiqsa, bot ishlayapti.

## To'xtatish va qayta ishga tushirish

- **Stop** (qizil kvadrat) botni to'xtatadi.
- Kod o'zgargandan keyin **Run** ni qayta bosish kerak — polling jarayoni eski kodni xotirada saqlaydi.
- Agar `TelegramConflictError` chiqsa, eski bot jarayoni hali ishlayapti; avval uni to'xtating.

## Eslatma

Konfiguratsiya `.env` faylini o'zi yuklamaydi — `config.py` dagi `load_dotenv()` uni loyiha ildizidan o'qiydi. Shuning uchun ish papkasi `$PROJECT_DIR$` bo'lishi muhim.
