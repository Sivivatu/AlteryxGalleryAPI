"""
Pagination helpers for API responses.
"""

from typing import Callable, Generic, Iterator, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper.

    Attributes:
        items: List of items in the current page
        total: Total number of items across all pages
        page: Current page number (1-indexed)
        page_size: Number of items per page
        has_more: Whether more pages are available
    """

    items: list[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    has_more: bool = False


class PaginatedIterator(Generic[T]):
    """Iterator for paginated API responses.

    Automatically fetches subsequent pages as items are consumed.

    Args:
        fetch_func: Function that takes page and page_size and returns PaginatedResponse
        page_size: Number of items per page. Defaults to 20.

    Example:
        def fetch_page(page, page_size):
            return client.workflows.list(page=page, page_size=page_size)

        for workflow in PaginatedIterator(fetch_page, page_size=50):
            print(workflow.name)
    """

    def __init__(
        self,
        fetch_func: Callable[[int, int], PaginatedResponse[T]],
        page_size: int = 20,
    ):
        self.fetch_func = fetch_func
        self.page_size = page_size
        self.current_page = 1
        self.current_items: list[T] = []
        self.current_index = 0
        self._has_more = True
        self._fetched_pages: set[int] = set()

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        while True:
            if self.current_index < len(self.current_items):
                item = self.current_items[self.current_index]
                self.current_index += 1
                return item

            if not self._has_more:
                raise StopIteration

            response = self.fetch_func(self.current_page, self.page_size)
            self.current_items = response.items
            self.current_index = 0
            self._has_more = response.has_more

            if not self.current_items:
                self._has_more = False
                raise StopIteration

            self.current_page += 1
