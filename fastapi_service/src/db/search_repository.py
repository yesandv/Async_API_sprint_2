from abc import ABC, abstractmethod


class SearchRepository(ABC):
    @abstractmethod
    async def search(self, index: str, query: dict) -> list[dict]:
        pass

    @abstractmethod
    async def get(self, index: str, id: str) -> dict:
        pass
