# Book App — Backend

Серверная часть приложения для читателей: каталог книг, читалка, полка и дневник чтения,
лента постов и личные сообщения.

Frontend: [FullStack_Frontend](https://github.com/NikitaYam/FullStack_Frontend)

## Стек

Python 3.12+, FastAPI, PostgreSQL, SQLAlchemy 2.0, Alembic, Pydantic.

## Структура

```
app/
├── main.py      # точка входа FastAPI
├── seed.py      # демонстрационные данные
├── core/        # настройки (.env) и обработка ошибок
├── db/          # подключение к БД и сессии
├── models/      # модели SQLAlchemy (таблицы)
├── schemas/     # схемы Pydantic (валидация запросов и ответов)
├── crud/        # операции с данными и бизнес-логика
└── api/         # маршруты API
alembic/         # миграции БД
```

## Модель данных

| Таблица | Назначение | Связи |
|---|---|---|
| `users` | пользователи | — |
| `books` | книги | — |
| `chapters` | главы книги | → `books` |
| `reviews` | рецензии (оценка 1–5, одна от пользователя на книгу) | → `books`, `users` |
| `user_books` | книга на полке: статус, прогресс, оценка, заметки | → `users`, `books` |
| `quotes` | цитаты из книги на полке | → `user_books` |
| `diary_logs` | записи дневника чтения | → `users`, `books` |
| `posts` | посты в ленте (можно привязать к книге) | → `users`, `books` |
| `post_comments` | комментарии к постам | → `posts`, `users` |
| `post_likes` | лайки (один от пользователя на пост) | → `posts`, `users` |
| `messages` | личные сообщения | → `users` (отправитель и получатель) |

Рейтинг книги, число лайков и число прочитанных книг не хранятся, а считаются при запросе.
При удалении записи связанные с ней данные удаляются каскадно.

## Запуск

Из папки `Backend` в PowerShell:

1. Установить зависимости:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Создать `.env` по примеру и указать пароль PostgreSQL в `DB_PASSWORD`:
   ```powershell
   Copy-Item .env.example .env
   ```

3. Создать базу данных `bookapp`:
   ```powershell
   & "C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres -h 127.0.0.1 bookapp
   ```

4. Создать таблицы и заполнить демонстрационными данными:
   ```powershell
   alembic upgrade head
   python -m app.seed
   ```

5. Запустить сервер:
   ```powershell
   fastapi dev app/main.py
   ```

## API

Все маршруты начинаются с `/api`, данные в JSON (camelCase).

- `/users` — пользователи
- `/books` — книги, `/books/{id}/chapters` — главы, `/books/{id}/reviews` — рецензии
- `/users/{id}/shelf` — полка, `/users/{id}/diary` — дневник
- `/posts` — посты, комментарии и лайки
- `/users/{id}/chats` — сообщения

Документация API: http://127.0.0.1:8000/docs

Ошибки возвращаются как `{"detail": "..."}` с кодом 404 (не найдено), 409 (конфликт)
или 422 (некорректные данные).