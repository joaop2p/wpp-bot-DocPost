from os.path import join
from .file_config import config
from .env_config import LOG_PATH

class Paths:
    """Classe de repositório do projeto."""
    MAIN_FOLDER = config['PATH_FOLDER'].get('main_folder', './')
    REPOSITORY_JPG = join(MAIN_FOLDER, config['PATH_FOLDER'].get('repository_jpg', 'jpg'))
    REPOSITORY_PDF = join(MAIN_FOLDER, config['PATH_FOLDER'].get('repository_pdf', 'pdf'))
    REPOSITORY_TEMP = join(MAIN_FOLDER, config['PATH_FOLDER'].get('awaiting_queue', 'temp'))
    NOT_SENDED_REPOSITORY = join(MAIN_FOLDER, config['PATH_FOLDER'].get('dist_files_not_sended_folder', 'not_sended'))
    SENDED_REPOSITORY = join(MAIN_FOLDER, config['PATH_FOLDER'].get('dist_files_sended', 'sended'))
    CACHE_DRIVER_PATH = config['DRIVER'].get('driver_cache', 'cache')
    GUIA = join(MAIN_FOLDER, config['PATH_FILES'].get('guidance', 'guia.pdf'))
    GUIA_REC = join(MAIN_FOLDER, config['PATH_FILES'].get('guidance_rec', 'guia_rec.pdf'))
    LOG_PATH = LOG_PATH
