import logging
from os import mkdir
from os.path import isdir, join
from ..settings.env_config import LOG_PATH
from ..settings.app_config import AppConfig

class Log:
    @staticmethod
    def setup():
        """Configura o log da aplicação."""
        if not isdir(LOG_PATH):
            mkdir(LOG_PATH)
        app_handler = logging.FileHandler(join(LOG_PATH, f"{AppConfig.TITLE} app.log"))
        app_handler.setLevel(logging.INFO)
        error_handler = logging.FileHandler(join(LOG_PATH, f"{AppConfig.TITLE} error.log"))
        error_handler.setLevel(logging.ERROR)
        logging.basicConfig(
            level=logging.INFO,
            encoding="utf-8",
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                app_handler,
                error_handler,
                logging.StreamHandler()
            ]
        )