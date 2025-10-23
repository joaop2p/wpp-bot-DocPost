from typing import Iterable
from sqlmodel import Session, select
from ...config.db_config import DatabaseConfig
from ..models.db.ignore import Ignore

class IgnoreRepository(DatabaseConfig):
    def __init__(self) -> None:
        super().__init__()

    def find_all(self) -> Iterable[Ignore]:
        with Session(self.engine) as conn:
            ignores = conn.exec(select(Ignore)).all()
        return ignores