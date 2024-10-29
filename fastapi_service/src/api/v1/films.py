from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from fastapi_service.src.models.film import FilmDetails, Film
from fastapi_service.src.services.film import FilmService, get_film_service
from fastapi_service.src.utils.pagination import Pagination

router = APIRouter(prefix="/api/v1/films", tags=["FilmService"])


@router.get(
    "/",
    response_model=list[Film],
    description="Получение всех фильмов",
)
async def get_films(
        genre_id: str = None,
        sort: str = "-imdb_rating",
        pagination: Pagination = Depends(),
        film_service: FilmService = Depends(get_film_service),
) -> list[Film]:
    return await film_service.get_films(
        sort, pagination.page_number, pagination.page_size, genre_id=genre_id
    )


@router.get(
    "/search",
    response_model=list[Film],
    description="Поиск по фильмам",
)
async def search_film(
        query: str,
        pagination: Pagination = Depends(),
        film_service: FilmService = Depends(get_film_service),
) -> list[Film]:
    films = await film_service.search(
        query, pagination.page_number, pagination.page_size
    )
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="No films were found"
        )
    return films


@router.get(
    "/{film_id}",
    response_model=FilmDetails,
    description="Страница фильма",
)
async def get_film_details(
        film_id: str, film_service: FilmService = Depends(get_film_service)
) -> FilmDetails:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Film was not found"
        )
    return film


@router.get(
    "/{film_id}/alike",
    response_model=list[Film],
    description="Похожие фильмы",
)
async def get_films_alike(
        film_id: str, film_service: FilmService = Depends(get_film_service)
) -> list[Film]:
    film = await film_service.get_by_id(film_id)
    films_alike = await film_service.get_by_genres(film.genres)
    if not films_alike:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="No films alike"
        )
    return films_alike
