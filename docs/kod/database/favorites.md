# `database/favorites.py` — sevimli darslar

**Yo'l:** [`database/favorites.py`](../../../database/favorites.py)
**Vazifasi:** `favorites` jadvali orqali foydalanuvchining sevimli darslari.

## Funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `is_favorite(user_id, lesson_id)` | Dars sevimlilarda bor-yo'qligini tekshiradi |
| `toggle_favorite(user_id, lesson_id)` | Holatni almashtiradi va yangi holatni (`bool`) qaytaradi |
| `get_favorite_lessons(user_id, limit=20)` | Dars + fan nomi/emojisi bilan ro'yxat, yangisi birinchi |
| `count_favorites(user_id)` | Sevimlilar soni (yutuq sharti va statistika uchun) |

## Jadval

```sql
CREATE TABLE IF NOT EXISTS favorites (
    user_id INTEGER NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    PRIMARY KEY (user_id, lesson_id)
);
```

- `PRIMARY KEY (user_id, lesson_id)` dublikatni oldini oladi.
- `ON DELETE CASCADE` foydalanuvchi yoki dars o'chsa yozuv ham o'chadi.
- Ro'yxatda faqat `is_active = 1` dars va fanlar ko'rsatiladi.
