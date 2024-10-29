from typing import Annotated

from fastapi import Query


class Pagination:
    def __init__(
            self,
            page_number: Annotated[int, Query(ge=1)] = 1,
            page_size: Annotated[int, Query(ge=1)] = 50,
    ):
        self.page_number = page_number
        self.page_size = page_size
