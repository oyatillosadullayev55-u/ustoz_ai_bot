# `pyproject.toml` — Ruff sozlamalari

**Yo'l:** [`pyproject.toml`](../../../pyproject.toml)
**Vazifasi:** lint qoidalari va kod uslubini belgilash.

## Sozlamalar

```toml
[tool.ruff]
target-version = "py313"
line-length = 100
extend-exclude = [".venv", "logs", "content"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B"]
ignore = ["B008"]

[tool.ruff.lint.isort]
known-first-party = ["config", "database", "handlers", "keyboards", "services", "time_utils"]
```

## Qoidalar izohi

| Kod | Ma'nosi |
|---|---|
| `E`, `W` | pycodestyle xatolari va ogohlantirishlari |
| `F` | pyflakes: ishlatilmagan import, aniqlanmagan nom |
| `I` | import tartibi |
| `UP` | zamonaviy Python sintaksisi (masalan, `datetime.UTC`) |
| `B` | bugbear: ehtimoliy xatolar |

`B008` o'chirilgan, chunki aiogram filterlari funksiya chaqiruvini default argument sifatida ishlatadi.

## Ishlatish

```bash
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m ruff check --fix .
```

CI'da `ruff check .` har bir push'da ishlaydi. Ruff versiyasi `requirements-dev.txt` da qat'iy belgilangan.
