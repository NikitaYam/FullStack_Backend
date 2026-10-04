"""Заполнение БД демонстрационными данными (те же, что в моках фронтенда).

Запуск из папки Backend:
    python -m app.seed           — заполнить пустую БД
    python -m app.seed --reset   — очистить все таблицы и заполнить заново
"""

import argparse
import datetime as dt
import sys

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal
from app.models import (
    Book,
    Chapter,
    DiaryLog,
    Message,
    Post,
    PostComment,
    PostLike,
    Quote,
    ReadingStatus,
    Review,
    User,
    UserBook,
)

USERS = {
    "nikita": dict(name="Никита", bio="Читаю по вечерам, люблю классику и научпоп.", favorite_genres=["Роман", "Научпоп"]),
    "anna": dict(name="Анна", bio="Фэнтези и детективы. Всегда ищу, что почитать дальше.", favorite_genres=["Фэнтези", "Детектив"]),
    "dmitry": dict(name="Дмитрий", bio="Антиутопии, научная фантастика и история.", favorite_genres=["Антиутопия", "Научпоп"]),
    "maria": dict(name="Мария", bio="Классическая литература и сказки.", favorite_genres=["Роман", "Сказка"]),
}

BOOKS = {
    "master": dict(title="Мастер и Маргарита", author="Михаил Булгаков", genre="Роман", year=1967, color="#5d4037",
                   description="В Москву приезжает загадочный профессор чёрной магии, и привычная жизнь города переворачивается. Параллельно разворачивается история Понтия Пилата."),
    "crime": dict(title="Преступление и наказание", author="Фёдор Достоевский", genre="Роман", year=1866, color="#37474f",
                  description="Бедный студент Раскольников совершает преступление и пытается оправдать его теорией, но совесть не даёт ему покоя."),
    "1984": dict(title="1984", author="Джордж Оруэлл", genre="Антиутопия", year=1949, color="#b71c1c",
                 description="Мир под тотальным контролем Партии, где даже мысли могут быть преступлением. История человека, решившегося на сопротивление."),
    "prince": dict(title="Маленький принц", author="Антуан де Сент-Экзюпери", genre="Сказка", year=1943, color="#1565c0",
                   description="Лётчик, потерпевший аварию в пустыне, встречает мальчика с далёкой планеты. Философская сказка о дружбе и ответственности."),
    "sapiens": dict(title="Sapiens. Краткая история человечества", author="Юваль Ной Харари", genre="Научпоп", year=2011, color="#ef6c00",
                    description="Как человек стал доминирующим видом на планете: от когнитивной революции до современности."),
    "potter": dict(title="Гарри Поттер и философский камень", author="Дж. К. Роулинг", genre="Фэнтези", year=1997, color="#6a1b9a",
                   description="Мальчик-сирота узнаёт, что он волшебник, и отправляется учиться в школу чародейства Хогвартс."),
    "express": dict(title="Убийство в «Восточном экспрессе»", author="Агата Кристи", genre="Детектив", year=1934, color="#2e7d32",
                    description="Поезд застревает в снегах, а один из пассажиров найден убитым. Эркюль Пуаро начинает расследование."),
    "pride": dict(title="Гордость и предубеждение", author="Джейн Остин", genre="Роман", year=1813, color="#ad1457",
                  description="Остроумная история о любви, семейных ожиданиях и социальных предрассудках в английской провинции."),
}

# Демонстрационный текст для читалки: одни и те же главы у каждой книги, как на фронтенде
CHAPTERS = [
    ("Глава 1. Начало", [
        "Утро выдалось тихим. Город ещё не проснулся, и только редкие окна светились жёлтым светом в предрассветной синеве.",
        "Он долго стоял у окна, обдумывая всё, что произошло накануне. Мысли путались, но одно он знал наверняка: назад дороги нет.",
        "Наконец, взяв старый потёртый портфель, он вышел на лестницу и осторожно прикрыл за собой дверь.",
    ]),
    ("Глава 2. Дорога", [
        "Дорога к вокзалу заняла больше времени, чем он рассчитывал. Трамваи ходили редко, а пешком идти было далеко.",
        "На перроне уже собирались первые пассажиры. Кто-то читал газету, кто-то пил горячий чай из бумажного стаканчика.",
        "Когда подошёл поезд, он занял место у окна и впервые за долгое время почувствовал, что может выдохнуть.",
    ]),
    ("Глава 3. Встреча", [
        "Напротив сидела женщина с толстой книгой в потёртом переплёте. Она не подняла глаз, но чуть заметно улыбнулась.",
        "Разговор завязался сам собой: сначала о погоде, потом о книгах, а потом о том, что бывает важнее и того и другого.",
        "К концу пути он понял, что эта случайная встреча изменит многое, хотя тогда ещё не мог сказать, что именно.",
    ]),
]

REVIEWS = [
    ("master", "anna", 5, "Перечитываю уже в третий раз и каждый раз нахожу что-то новое."),
    ("master", "dmitry", 4, "Очень необычная композиция. Линия Пилата понравилась больше всего."),
    ("1984", "dmitry", 5, "Мрачно, но книга, которую стоит прочитать каждому."),
    ("prince", "maria", 5, "Простая сказка, после которой хочется звонить близким."),
]

# Полка Никиты: (книга, статус, прогресс, оценка, заметки, цитаты)
SHELF = [
    ("master", ReadingStatus.reading, 40, None, "Очень нравится сатира на московскую жизнь.", ["Рукописи не горят."]),
    ("1984", ReadingStatus.done, 100, 5, "Тяжёлая, но очень сильная книга.", []),
    ("prince", ReadingStatus.want, 0, None, "", []),
]

DIARY = [
    ("master", dt.date(2026, 9, 10), "Начал читать, очень понравилось начало и атмосфера Москвы 30-х годов."),
    ("master", dt.date(2026, 9, 15), "Дошёл до линии Пилата — она куда серьёзнее, чем я ожидал."),
    ("1984", dt.date(2026, 8, 20), "Дочитал за один вечер. Тяжёлое, но очень сильное произведение."),
]

# (ключ, автор, книга, текст, кто лайкнул, комментарии [(автор, текст)])
POSTS = [
    ("p1", "anna", "potter", "Начала перечитывать «Гарри Поттера» перед выходом нового фильма. Первая книга всё ещё держит магию!",
     ["nikita", "dmitry", "maria"], [("nikita", "Обожаю эту серию, тоже пересматриваю фильмы.")]),
    ("p2", "dmitry", "1984", "Дочитал «1984». Тяжело, но однозначно того стоило.",
     ["nikita", "anna", "maria"], []),
    ("p3", "maria", None, "Кто-нибудь может посоветовать лёгкий роман на выходные? Устала от тяжёлой классики.",
     ["anna", "nikita"], [("anna", "Попробуй «Гордость и предубеждение», она довольно лёгкая.")]),
]

# (отправитель, получатель, текст) — в хронологическом порядке
MESSAGES = [
    ("anna", "nikita", "Привет! Как тебе «Мастер и Маргарита»?"),
    ("nikita", "anna", "Только начал, но уже очень нравится!"),
    ("dmitry", "nikita", "Читал что-то из антиутопий в последнее время?"),
    ("nikita", "dmitry", "Да, только закончил «1984»."),
    ("dmitry", "nikita", "И как впечатления?"),
]


def reset(db: Session) -> None:
    tables = ", ".join(table.name for table in Base.metadata.sorted_tables)
    db.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


def seed(db: Session) -> None:
    users = {key: User(**data) for key, data in USERS.items()}
    books = {key: Book(**data) for key, data in BOOKS.items()}
    db.add_all([*users.values(), *books.values()])
    db.flush()  # получить id до создания связанных записей

    for book in books.values():
        book.chapters = [
            Chapter(number=i, title=title, paragraphs=paragraphs)
            for i, (title, paragraphs) in enumerate(CHAPTERS, start=1)
        ]

    for book, author, rating, review_text in REVIEWS:
        db.add(Review(book_id=books[book].id, author_id=users[author].id, rating=rating, text=review_text))

    nikita = users["nikita"]
    for book, status, progress, rating, notes, quotes in SHELF:
        entry = UserBook(user_id=nikita.id, book_id=books[book].id, status=status,
                         progress=progress, rating=rating, notes=notes)
        entry.quotes = [Quote(text=q) for q in quotes]
        db.add(entry)

    for book, date, log_text in DIARY:
        db.add(DiaryLog(user_id=nikita.id, book_id=books[book].id, date=date, text=log_text))

    # Явные даты, чтобы лента и чаты имели правдоподобный порядок
    # (иначе у всех записей одной транзакции было бы одинаковое now())
    now = dt.datetime.now()
    for i, (_, author, book, post_text, liked_by, comments) in enumerate(POSTS):
        post = Post(author_id=users[author].id, book_id=books[book].id if book else None,
                    text=post_text, created_at=now - dt.timedelta(days=3 - i))
        post.likes = [PostLike(user_id=users[u].id) for u in liked_by]
        post.comments = [
            PostComment(author_id=users[a].id, text=c, created_at=post.created_at + dt.timedelta(hours=1 + j))
            for j, (a, c) in enumerate(comments)
        ]
        db.add(post)

    for i, (sender, receiver, msg_text) in enumerate(MESSAGES):
        db.add(Message(sender_id=users[sender].id, receiver_id=users[receiver].id, text=msg_text,
                       created_at=now - dt.timedelta(hours=len(MESSAGES) - i)))


def main() -> None:
    parser = argparse.ArgumentParser(description="Заполнить БД демонстрационными данными")
    parser.add_argument("--reset", action="store_true", help="очистить все таблицы перед заполнением")
    args = parser.parse_args()

    with SessionLocal() as db:
        if args.reset:
            reset(db)
        elif db.scalar(select(func.count()).select_from(User)):
            sys.exit("В БД уже есть данные. Запустите с --reset, чтобы очистить их и заполнить заново.")
        seed(db)
        db.commit()

        counts = {table.name: db.scalar(select(func.count()).select_from(table)) for table in Base.metadata.sorted_tables}
    print("Готово:", ", ".join(f"{name}={n}" for name, n in counts.items()))


if __name__ == "__main__":
    main()