from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from fastapi_service.src.models.film import Film
from fastapi_service.src.models.person import PersonWithFilms
from fastapi_service.src.services.person import (
    PersonService,
    get_person_service,
)

router = APIRouter(prefix="/api/v1/persons", tags=["PersonService"])


@router.get(
    "/search",
    response_model=list[PersonWithFilms],
    description="Поиск по исполнителям",
)
async def search_person(
        query: str,
        page_number: int = Query(1),
        page_size: int = Query(50),
        person_service: PersonService = Depends(get_person_service),
) -> list[PersonWithFilms]:
    persons = await person_service.search(query, page_number, page_size)
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="No people were found"
        )
    return persons


@router.get(
    "/{person_id}",
    response_model=PersonWithFilms,
    description="Страница исполнителя",
)
async def get_person_details(
        person_id: str,
        person_service: PersonService = Depends(get_person_service),
) -> PersonWithFilms:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Person was not found"
        )
    return person


@router.get(
    "/{person_id}/films",
    response_model=list[Film],
    description="Фильмы исполнителя",
)
async def get_person_film_works(
        person_id: str,
        person_service: PersonService = Depends(get_person_service),
) -> list[Film]:
    person_film_works = await person_service.get_film_works_by_person_id(
        person_id
    )
    if not person_film_works:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="No film works were found"
        )
    return person_film_works
