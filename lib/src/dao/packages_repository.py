from typing import Iterable
from sqlmodel import Session, select
from lib.config.db_config import DatabaseConfig
from ..models.db.packages import AgPackage, WppPackage

class PackagesRepository(DatabaseConfig):
    def __init__(self) -> None:
        super().__init__()

    def create_new(self, package: AgPackage | WppPackage):
        with Session(self.engine) as conn:
            conn.add(package)
            conn.commit()

    def fetch_pendings(self) -> Iterable[WppPackage] | None:
        with Session(self.engine) as conn:
            statement = (
                select(WppPackage).where(WppPackage.delivered == False)
            )
            return conn.exec(statement).all()