import logging
from os import getenv
from sqlalchemy import Engine, create_engine
from sqlmodel import SQLModel
from . import CONFIG, LOG
from typing import Self, Any

class DatabaseConfig:
    _instance = None
    _initialized = False

    def __init__(self, echo: bool = False) -> None:
        """Inicializa o engine de banco de dados como singleton com opções de pool.

        - Usa SQLite por padrão (com base em CONFIG.database).
        - Ativa pool_pre_ping para detectar conexões quebradas.
        - Para bancos não-SQLite, permite configurar pool_size, max_overflow e pool_recycle via env vars.
        - Cria o schema (SQLModel.metadata.create_all) na primeira inicialização.
        """
        url = f"sqlite:///{CONFIG.database}"
        if self.__class__._initialized:
            return

        self.logger = logging.getLogger("DatabaseConfig")
        try:
            self.logger.info(LOG.DB_CONNECTING, {"db_path": CONFIG.database})

            is_sqlite = url.startswith("sqlite:")
            engine_kwargs: dict[str, Any] = {
                "echo": echo or (getenv("DB_ECHO", "false").lower() == "true"),
                "future": True,
                "pool_pre_ping": True,
            }

            if is_sqlite:
                # Para SQLite, evitar parâmetros de QueuePool que causam TypeError
                # e permitir acesso multi-thread quando necessário
                engine_kwargs["connect_args"] = {"check_same_thread": False}
            else:
                # Parâmetros de pool para bancos não-SQLite
                try:
                    pool_size = int(getenv("DB_POOL_SIZE", "5"))
                    max_overflow = int(getenv("DB_MAX_OVERFLOW", "10"))
                    pool_recycle = int(getenv("DB_POOL_RECYCLE", "1800"))
                except ValueError:
                    # Fallback seguro caso variáveis estejam malformadas
                    pool_size, max_overflow, pool_recycle = 5, 10, 1800

                engine_kwargs.update(
                    {
                        "pool_size": pool_size,
                        "max_overflow": max_overflow,
                        "pool_recycle": pool_recycle,
                    }
                )

            self.engine: Engine = create_engine(url, **engine_kwargs)

            SQLModel.metadata.create_all(self.engine)
            self.logger.info(LOG.DB_CONNECTED)
            self.__class__._initialized = True
        except Exception as e:
            self.logger.exception(LOG.DB_CONNECTION_ERROR, {"error": str(e)})
            raise

    def __new__(cls, *args, **kwargs) -> Self:
        if cls._instance is None:
            cls._instance = super(DatabaseConfig, cls).__new__(cls)
        return cls._instance