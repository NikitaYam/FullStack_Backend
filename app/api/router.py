from fastapi import APIRouter

from app.api import books, chapters, chats, diary, posts, reviews, shelf, users

api_router = APIRouter(prefix="/api")
api_router.include_router(users.router)
api_router.include_router(books.router)
api_router.include_router(chapters.router)
api_router.include_router(reviews.router)
api_router.include_router(shelf.router)
api_router.include_router(diary.router)
api_router.include_router(posts.router)
api_router.include_router(chats.router)