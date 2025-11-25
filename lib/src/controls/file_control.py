import logging
from typing import Literal
from shutil import move
from lib.config import CONFIG
from lib.src.models.domain.file import File

class FileControl:
    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

    def move_to_ag(self, file:File):
        try:
            self._logger.info('Movendo arquivo para pasta %s', CONFIG.path.not_sended_repository)
            move(file.post_path, CONFIG.path.not_sended_repository)
            self._logger.info('Arquivo movido com sucesso.')
        except Exception as e:
            self._logger.info('Um erro aconteceu durante a transferência de arquivos... %s', e)

    def move_to_ready(self, file: File|None = None, path: str|None = None):
        try:
            self._logger.info('Movendo arquivo para pasta %s', CONFIG.path.sended_repository)
            if file:
                move(file.post_path, CONFIG.path.sended_repository)
            elif path:
                move(path, CONFIG.path.sended_repository)
            else:
                raise ValueError('Nenhum arquivo ou caminho fornecido para mover.')
            self._logger.info('Arquivo movido com sucesso.')
        except Exception as e:
            self._logger.info('Um erro aconteceu durante a transferência de arquivos... %s', e)

    def move_to_pending(self, file: File):
        try:
            self._logger.info('Movendo arquivo para pasta %s', CONFIG.path.repository_temp)
            move(file.post_path, CONFIG.path.repository_temp)
            self._logger.info('Arquivo movido com sucesso.')
        except Exception as e:
            self._logger.info('Um erro aconteceu durante a transferência de arquivos... %s', e)