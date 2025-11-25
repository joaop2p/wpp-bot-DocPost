from ..services.ignore_service import IgnoreService
from ..models.db.ignore import Ignore
from typing import Iterable

class IgnoreControl:
    def __init__(self) -> None:
        self.ignore_service = IgnoreService()

    def get_all_ignores(self) -> Iterable[Ignore]:
        return self.ignore_service.find_all_ignores()