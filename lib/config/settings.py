from abc import ABC, abstractmethod
from configparser import ConfigParser
from datetime import datetime
from genericpath import isdir
import logging
from os.path import exists, join
from pathlib import Path
from dotenv import load_dotenv
from typing_extensions import Self
from os import getenv, getlogin, makedirs, mkdir
from getpass import getuser
from socket import gethostname
from .constants import ConfigDefaults as DEFAULTS

class ConfigTemplate(ABC):
    @abstractmethod
    def from_file(self, file: ConfigParser):
        pass

class AppConfig(ConfigTemplate):
    """Configurações gerais da aplicação."""
    
    _headless_mode: bool
    _app_name = 'DocPost Bot'
    _model_lm: str
    _data_file: str

    def __init__(self) -> None:
        try:
            self._user_login: str = getlogin()
        except Exception:
            self._user_login = getuser() or getenv('USERNAME', 'unknown')
        self._version: str = '5.0'
        self._error_code: int = 1
        self._success_code: int = 0
        self._today: datetime = datetime.today()

    def from_file(self, file: ConfigParser) -> None:
        # Configurações do driver
        self.set_headless_mode(file.getboolean('DRIVER', 'headless_mode', fallback=False))
        
        # Configurações de arquivos
        try:
            self._model_lm = file.get('PATH_FILES', 'model_lm')
            self._data_file = file.get('PATH_FILES', 'sicde_base_files', fallback='')
        except KeyError as e:
            raise KeyError(f"Erro ao acessar chave de configuração em PATH_FILES: {e}")

    def set_headless_mode(self, value: bool) -> None:
        self._headless_mode = value

    @property
    def login(self) -> str: return self._user_login
    @property
    def headless_mode(self) -> bool: return self._headless_mode
    @property
    def error_code(self) -> int: return self._error_code
    @property
    def success_code(self) -> int: return self._success_code
    @property
    def today(self) -> datetime: return self._today
    @property
    def title(self) -> str: return self._app_name
    @property
    def model_lm(self) -> str: return self._model_lm
    @property
    def data_file(self) -> str: return self._data_file

    def __str__(self) -> str:
        return "\n".join(f"{var}: {getattr(self, var)}" for var in vars(self))
    
class PathConfig(ConfigTemplate):
    """Configurações de caminhos e diretórios."""
    _print_repository: str
    _file_path: str
    _driver_cache: str
    _log_dir: str
    _db_path: str
    _main_folder: str
    _repository_jpg: str
    _repository_pdf: str
    _repository_temp: str
    _not_sended_repository: str
    _sended_repository: str
    _guia: str
    _guia_rec: str

    def __init__(self) -> None:
        load_dotenv()
        self._log_dir = getenv('LOG_DIR', rf'C:\Users\{getlogin()}\Logs\DocPost')
        try:
            makedirs(self._log_dir, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Falha ao criar LOG_DIR '{self._log_dir}': {e}") from e

    def __str__(self) -> str:
        return "\n".join(f"{var}: {getattr(self, var)}" for var in vars(self))
    
    def set_database_path(self, value: str) -> None:
        if value == './data.db':
            raise ValueError("Caminho do banco de dados não pode ser o padrão './data.db'. "
                             "Altere 'PATH_FILES.database' no config.ini.")
        self._db_path = value

    def set_main_folder(self, value: str) -> None:
        if not exists(value):
            raise FileNotFoundError(f"Pasta principal não encontrada: '{value}'. "
                                    "Verifique 'PATH_FOLDER.main_folder' no config.ini")
        self._main_folder = value

    def set_print_repository(self, value: str) -> None:
        try:
            makedirs(value, exist_ok=True)
            self._print_repository = value
        except Exception as e:
            raise RuntimeError(f"Não foi possível criar o diretório '{value}': {e}") from e

    def set_driver_cache(self, value: str) -> None:
        # O diretório será criado caso não exista pelo próprio selenium
        self._driver_cache = value

    def set_file_path(self, value: str):
        if not exists(value):
            raise FileNotFoundError(f"Arquivo de dados não encontrado: '{value}'. "
                                    "Verifique 'PATH_FILES.sicde_base_files' no config.ini")
        self._file_path = value

    def from_file(self, file: ConfigParser) -> None:
        # Pasta principal
        main_folder = file.get('PATH_FOLDER', 'main_folder', fallback='./')
        self.set_main_folder(main_folder)
        
        # Configuração de diretórios relativos à pasta principal
        self._repository_jpg = join(main_folder, file.get('PATH_FOLDER', 'repository_jpg', fallback='jpg'))
        self._repository_pdf = join(main_folder, file.get('PATH_FOLDER', 'repository_pdf', fallback='pdf'))
        self._repository_temp = join(main_folder, file.get('PATH_FOLDER', 'awaiting_queue', fallback='temp'))
        self._not_sended_repository = join(main_folder, file.get('PATH_FOLDER', 'dist_files_not_sended_folder', fallback='not_sended'))
        self._sended_repository = join(main_folder, file.get('PATH_FOLDER', 'dist_files_sended', fallback='sended'))
        
        # Arquivos de orientação
        self._guia = join(main_folder, file.get('PATH_FILES', 'guidance', fallback='guia.pdf'))
        self._guia_rec = join(main_folder, file.get('PATH_FILES', 'guidance_rec', fallback='guia_rec.pdf'))
        
        # Cache do driver
        self.set_driver_cache(file.get('DRIVER', 'driver_cache', fallback='./cache'))
        
        # Banco de dados
        self.set_database_path(file.get('PATH_FILES', 'database', fallback='./data.db'))
        
        # Arquivo de dados principal
        data_file = file.get('PATH_FILES', 'sicde_base_files', fallback='')
        if data_file:
            self.set_file_path(data_file)
        
        # Log da aplicação (se especificado)
        app_log = file.get('PATH.LOG', 'app_log', fallback=self._log_dir)
        if app_log != self._log_dir:
            try:
                makedirs(app_log, exist_ok=True)
                self._log_dir = app_log
            except Exception as e:
                logging.warning(f"Aviso: Não foi possível usar log_dir '{app_log}', usando padrão: {e}")

    # Propriedades de compatibilidade com o sistema antigo
    @property
    def main_folder(self) -> str: return self._main_folder
    @property
    def repository_jpg(self) -> str: return self._repository_jpg
    @property
    def repository_pdf(self) -> str: return self._repository_pdf
    @property
    def repository_temp(self) -> str: return self._repository_temp
    @property
    def not_sended_repository(self) -> str: return self._not_sended_repository
    @property
    def sended_repository(self) -> str: return self._sended_repository
    @property
    def cache_driver_path(self) -> str: return self._driver_cache
    @property
    def guia(self) -> str: return self._guia
    @property
    def guia_rec(self) -> str: return self._guia_rec
    
    # Propriedades existentes
    @property
    def file_path(self) -> str: return getattr(self, '_file_path', '')
    @property
    def repository(self) -> str: return getattr(self, '_print_repository', '')
    @property
    def cache(self) -> str: return self._driver_cache
    @property
    def log_dir(self) -> str: return self._log_dir
    @property
    def db(self) -> str: return self._db_path

class Config():
    """Classe principal de configuração - Singleton pattern."""
    
    _instance = None
    _initialized = False
    _config: ConfigParser

    def __new__(cls, *args, **kwargs) -> Self:
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
        
    def __init__(self) -> None:
        if self.__class__._initialized:
            return
        self._read_file()
        self._app_config = AppConfig()
        self._path_config = PathConfig()
        self._load_configs()
        self.__class__._initialized = True
        self._logging_config()

    def _logging_config(self) -> None:
        path = join(self._path_config.log_dir, DEFAULTS.NAME)
        if not isdir(path):
            makedirs(path, exist_ok=True)
        file_name = join(path, f"{gethostname()}_{datetime.today().strftime('%d%m%Y')}.log")
        app_handler = logging.FileHandler(file_name, encoding='utf-8-sig')
        error_handler = logging.FileHandler(f"{file_name}_error.log", encoding='utf-8-sig')
        app_handler.setLevel(logging.INFO)
        error_handler.setLevel(logging.ERROR)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%d-%m-%Y %H:%M:%S'
        )
        app_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        root.handlers.clear()
        root.addHandler(app_handler)
        root.addHandler(error_handler)
        root.addHandler(console_handler)

    def _load_configs(self):
        """Carrega todas as configurações dos arquivos."""
        self._app_config.from_file(self._config)
        self._path_config.from_file(self._config)

    def _read_file(self):
        """Lê o arquivo de configuração config.ini."""
        self._config = ConfigParser()
        root = Path(__file__).resolve().parents[2]  # Ajustado para a estrutura atual
        cfg_env = getenv('APP_CONFIG_FILE')

        config_path = Path(cfg_env) if cfg_env else (root / 'config.ini')
        if not config_path.exists():
            raise RuntimeError(f"Arquivo config.ini não encontrado em '{config_path}'. "
                               "Defina APP_CONFIG_FILE ou posicione o arquivo na raiz do projeto.")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config.read_file(f)
        except Exception as e:
            raise RuntimeError(f"Erro ao ler arquivo de configuração '{config_path}': {e}")

    @property
    def app(self) -> AppConfig:
        """Retorna configurações da aplicação."""
        return self._app_config

    @property
    def path(self) -> PathConfig:
        """Retorna configurações de caminhos."""
        return self._path_config

    # Propriedades de compatibilidade com o sistema antigo
    @property
    def title(self) -> str:
        """Título da aplicação."""
        return self._app_config.title
    
    @property
    def generic_error_code(self) -> int:
        """Código de erro genérico."""
        return self._app_config.error_code
    
    @property
    def success_code(self) -> int:
        """Código de sucesso."""
        return self._app_config.success_code
    
    @property
    def database(self) -> str:
        """Caminho do banco de dados."""
        return self._path_config.db
    
    @property
    def data_file(self) -> str:
        """Arquivo de dados principal."""
        return self._app_config.data_file
    
    @property
    def model_lm(self) -> str:
        """Caminho do modelo de machine learning."""
        return self._app_config.model_lm
    
    @property
    def headless_mode(self) -> bool:
        """Modo headless do driver."""
        return self._app_config.headless_mode

    @classmethod
    def reset(cls) -> None:
        """Reseta o singleton para permitir reconfiguração."""
        cls._instance = None
        cls._initialized = False