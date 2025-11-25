from ..dao.ignore_repository import IgnoreRepository
from ..models.db.ignore import Ignore
from typing import Iterable

class IgnoreService:
    def __init__(self) -> None:
        self.ignore_repository = IgnoreRepository()

    def find_all_ignores(self) -> Iterable[Ignore]:
        return self.ignore_repository.find_all()