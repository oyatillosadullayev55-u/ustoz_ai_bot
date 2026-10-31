# `services/gamification.py` — XP, darajalar va yutuqlar

**Yo'l:** [`services/gamification.py`](../../../services/gamification.py)
**Vazifasi:** XP miqdorlari, daraja pog'onalari, 12 ta yutuq va mukofot natijasini
hisoblash. Bu qatlam `database/gamification.py` ustida ishlaydi.

## XP qiymatlari

| Hodisa | XP |
|---|---|
| Dars tugatish (`XP_LESSON`) | 20 |
| Test boshlanishi (`XP_QUIZ_BASE`) | 5 |
| Har bir to'g'ri javob (`XP_QUIZ_PER_CORRECT`) | 2 |
| 100% natija bonusi (`XP_PERFECT_BONUS`) | 10 |
| Kunlik maqsad bajarildi (`XP_GOAL_BONUS`) | 15 |
| Har bir yangi yutuq (`XP_ACHIEVEMENT`) | 15 |
| AI Ustoz savoli (`XP_AI`) | 1 |

## Darajalar

| Emoji | Nomi | Minimal XP |
|---|---|---|
| 🌱 | Yangi boshlovchi | 0 |
| 📗 | O'quvchi | 100 |
| 📘 | Bilimdon | 300 |
| 🎓 | Tajribali | 700 |
| 🏅 | Ustoz | 1500 |
| 👑 | Afsona | 3000 |

`rank_for(xp)` joriy darajani, `next_rank(xp)` keyingi darajani qaytaradi.

## Yutuqlar (12 ta)

| Kod | Nomi | Sharti |
|---|---|---|
| `first_lesson` | Birinchi qadam | 1 dars |
| `five_lessons` | Izlanuvchi | 5 dars |
| `fifteen_lessons` | Bilimdon | 15 dars |
| `all_lessons` | Marafon | 35 dars |
| `first_quiz` | Birinchi sinov | 1 test |
| `ten_quizzes` | Test ustasi | 10 test |
| `perfect_quiz` | Mukammal natija | bitta 100% test |
| `streak_3` | Uch kun | 3 kun ketma-ket |
| `streak_7` | Bir hafta | 7 kun ketma-ket |
| `favorite_5` | Kolleksioner | 5 sevimli dars |
| `ai_10` | AI hamkor | 10 AI savol |
| `goal_5` | Maqsadli | 5 kun maqsad bajarilgan |

Har bir yutuq funksiyasi `get_achievement_stats()` lug'atini tekshiradi.

## `reward(...)`

```python
result = await reward(user_id, XP_LESSON, "lesson", once_key=f"lesson:{id}")
```

1. Eski XP o'qiladi.
2. `amount > 0` bo'lsa XP yoziladi (bir marta beriladigan bo'lsa `once_key` bilan).
3. Statistika + streak yuklanadi, shartga mos yangi yutuqlar ochiladi.
4. Har bir yangi yutuq uchun `+15 XP` qo'shiladi.
5. `RewardResult(xp, xp_gained, rank, rank_up, achievements)` qaytadi.

`combine_rewards(*results)` bir amaldagi bir nechta mukofotni (masalan, dars XP +
kunlik maqsad bonusi) yagona natijaga birlashtiradi va yutuqlarni takrorlamaydi.

## Ekranlar uchun

| Funksiya | Qaytaradi |
|---|---|
| `get_profile(user_id)` | XP, daraja, keyingi daraja, haftalik XP, yutuqlar soni |
| `get_achievements_with_state(user_id)` | `[(Achievement, ochilganmi)]` |
| `get_leaderboard(user_id)` | `database.gamification.get_weekly_leaderboard` natijasi |
