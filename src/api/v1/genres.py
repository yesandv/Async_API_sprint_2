from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from src.models.genre import Genre
from src.services.genre import GenreService, get_genre_service

router = APIRouter(prefix="/api/v1/genres", tags=["GenreService"])


@router.get(
    "/",
    response_model=list[Genre],
    description="Получение всех жанров",
)
async def get_genres(
        genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    return await genre_service.get_genres()


@router.get(
    "/{genre_id}",
    response_model=Genre,
    description="Страница жанра",
)
async def get_genre_details(
        genre_id: str,
        genre_service: GenreService = Depends(get_genre_service),
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Genre was not found"
        )
    return genre
