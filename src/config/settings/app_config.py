
from os.path import join
from .file_config import config
from .paths import Paths
from .env_config import DATABASE_PATH


class AppConfig(Paths):
    """Classe central de configuração da aplicação."""

    TITLE = 'DocPost'
    VERSION = "4.0"
    GENERIC_ERROR_CODE = 1
    SUCCESS_CODE = 0
    DATA_BASE_FILE = DATABASE_PATH
    try:
        DATABASE = config['PATH_FILES']['database']
        DATA_FILE = config.get('PATH_FILES', 'sicde_base_files', fallback='')
        MODEL_LM = config['PATH_FILES']['model_lm']
        HEADLESS_MODE = config.getboolean('DRIVER', 'headless_mode', fallback=True)
    except KeyError as e:
        raise KeyError(f"Erro ao acessar chave de configuração em PATH_FILES: {e}")