
import logging
from os import listdir
from os.path import join
from shutil import move
from time import sleep
from .services.fileServices import FileServices
from .config.settings.app_config import AppConfig
from .config.templates.logging_messages import LoggingMessages
from .actions import Actions
from .config.settings.paths import Paths
from .data.connection import Connection

class Search():
    def __init__(self,actions: Actions) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.actions = actions
    
    def search_missing(self, target: int, process: int, connection: Connection, files: list[str]) -> None:
        logging.info(LoggingMessages.SEARCH_CONTACT_BEFORE.format(target))
        self.actions.safe_search(target)
        status = self.actions.entregue()
        post = FileServices.buscador(target=str(process), files=files)
        if status and post is not None:
            move(join(Paths.REPOSITORY_TEMP, post), Paths.SENDED_REPOSITORY)
            self.actions.print_page(process)
            connection.update_status(process, status)
        self.actions.exit_chat()
        self.actions.cancel_safe_search()

    def start_Actions(self) -> None:
        return Actions().__init__()
        
    def wpp_search(self) -> None:
        connection = Connection()
        result = connection.select()
        if not result:
            logging.warning(LoggingMessages.NO_PROCESS_TO_SEARCH)
            return
        files = listdir(Paths.REPOSITORY_TEMP)
        for process, _ in connection.select():    
            self.search_missing(target=process, process=process, connection=connection, files=files)

    