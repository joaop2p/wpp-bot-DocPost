from typing import Iterable
from lib.src.dao.packages_repository import PackagesRepository
from ..models.db.packages import AgPackage, WppPackage

class PackageService:
    def __init__(self) -> None:
        self._package_repository = PackagesRepository()

    def create_new_item(self, package: AgPackage | WppPackage):
        self._package_repository.create_new(package)

    def fetch_pending_items(self) -> Iterable[WppPackage] | None:
        return self._package_repository.fetch_pendings()