from typing import Iterable, Literal
from lib.src.models.domain.client import Client
from lib.src.models.db.packages import AgPackage, WppPackage
from lib.src.services.packages_service import PackageService


class PackageControl:
    def __init__(self) -> None:
        self._package_service = PackageService()

    def insert_package_from_client(self, client: Client, mode: Literal['default', 'secondary']):
        match mode:
            case 'default':
                package = WppPackage(
                    process_id=int(client.process),
                    tp_content=client.file.type_content,
                    num_used=int(client.used),
                    delivered=client.delivered
                )
            case 'secondary':
                package = AgPackage(
                    process_id=int(client.process),
                    tp_content=client.file.type_content
                )
            case _:
                raise ValueError('A variavel "mode" deve ser "secondary" ou "default".')
        self._package_service.create_new_item(package)

    def insert_package(self, package: AgPackage | WppPackage):
        self._package_service.create_new_item(package)

    def fetch_pending_package(self) -> Iterable[WppPackage] | None:
        return self._package_service.fetch_pending_items()
