# `.github/workflows/ci.yml` — CI workflow

**Yo'l:** [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml)
**Vazifasi:** har bir push va pull request'da kod sifatini va testlarni avtomatik tekshirish.

## Trigger'lar

- `push` — `main` branchiga;
- `pull_request` — `main` branchiga.

## Qadamlar

1. Reponi checkout qilish (`actions/checkout@v4`).
2. Python 3.13 o'rnatish (`actions/setup-python@v5`), pip cache bilan.
3. `pip install -r requirements-dev.txt`.
4. `ruff check .` — lint.
5. `python tests/test_offline.py` — ma'lumotlar qatlami.
6. `python tests/test_handlers_offline.py` — handler oqimlari.

## Nima uchun Telegram tokeni kerak emas

Testlar `BOT_TOKEN` ni o'zlari soxta qiymat bilan o'rnatadi va tarmoqqa chiqmaydi. Shuning uchun CI'da hech qanday secret qo'shish talab qilinmaydi.

## Natijani ko'rish

GitHub'da **Actions** bo'limida `CI` workflow natijasi ko'rinadi. Qizil bo'lsa, logda qaysi qadam yoki qaysi test yiqilgani ko'rsatiladi.
