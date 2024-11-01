from abc import ABC, abstractmethod


class SearchRepository(ABC):

    @abstractmethod
    async def search(self, query: dict) -> list[dict]:
        pass

    @abstractmethod
    async def get(self, doc_id: str) -> dict:
        pass
