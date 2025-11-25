"""
Repositório de constantes e mensagens de LOG do sistema DocPost Bot.
Centraliza todas as mensagens, códigos de status e outras constantes utilizadas na aplicação.
"""

from enum import Enum, IntEnum
from datetime import datetime
from typing import Dict, Any

class LogLevel(Enum):
    """Níveis de log disponíveis."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StatusCode(IntEnum):
    """Códigos de status da aplicação."""
    SUCCESS = 0
    GENERIC_ERROR = 1
    CONFIG_ERROR = 2
    FILE_NOT_FOUND = 3
    PERMISSION_ERROR = 4
    NETWORK_ERROR = 5
    DATABASE_ERROR = 6
    VALIDATION_ERROR = 7
    TIMEOUT_ERROR = 8
    SELENIUM_ERROR = 9
    WHATSAPP_ERROR = 10
    INTERRUPTED = 11
    NO_CLIENTS = 12


class MessageType(Enum):
    """Tipos de mensagens do sistema."""
    SYSTEM = "SYSTEM"
    USER = "USER"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    INFO = "INFO"


class LogMessages:
    """Repositório centralizado de mensagens de LOG."""
    
    # === INICIALIZAÇÃO ===
    APP_STARTING = "Inicializando %(app_name)s v%(version)s."
    APP_STARTED = "%(app_name)s inicializado."
    APP_STOPPING = "Finalizando %(app_name)s."
    APP_STOPPED = "%(app_name)s finalizado."
    
    CONFIG_LOADING = "Carregando configurações de %(config_file)s."
    CONFIG_LOADED = "Configurações carregadas."
    CONFIG_ERROR = "Falha ao carregar configurações: %(error)s."
    CONFIG_FILE_NOT_FOUND = "Arquivo de configuração não localizado: %(file_path)s."
    CONFIG_VALIDATION_ERROR = "Configuração inválida: %(detail)s."
    
    # === BANCO DE DADOS ===
    DB_CONNECTING = "Conectando ao banco de dados: %(db_path)s."
    DB_CONNECTED = "Conexão com o banco de dados estabelecida."
    DB_CONNECTION_ERROR = "Falha na conexão com o banco de dados: %(error)s."
    DB_QUERY_EXECUTING = "Executando consulta SQL: %(query)s."
    DB_QUERY_SUCCESS = "Consulta executada com êxito. Registros afetados: %(rows)d."
    DB_QUERY_ERROR = "Erro na execução da consulta: %(error)s."
    DB_BACKUP_CREATING = "Iniciando backup do banco de dados."
    DB_BACKUP_SUCCESS = "Backup concluído em %(backup_path)s."
    DB_BACKUP_ERROR = "Falha ao criar backup: %(error)s."
    
    # === ARQUIVOS ===
    FILE_READING = "Lendo arquivo: %(file_path)s."
    FILE_READ_SUCCESS = "Leitura concluída: %(file_path)s."
    FILE_READ_ERROR = "Falha na leitura do arquivo %(file_path)s: %(error)s."
    FILE_WRITING = "Gravando arquivo: %(file_path)s."
    FILE_WRITE_SUCCESS = "Gravação concluída: %(file_path)s."
    FILE_WRITE_ERROR = "Falha na gravação do arquivo %(file_path)s: %(error)s."
    FILE_NOT_FOUND = "Arquivo não encontrado: %(file_path)s."
    FILE_PERMISSION_ERROR = "Permissão negada ao acessar o arquivo: %(file_path)s."
    FILE_PROCESSING = "Processando arquivo: %(file_path)s."
    FILE_PROCESSED = "Processamento concluído: %(file_path)s."
    
    # === DIRETÓRIOS ===
    DIR_CREATING = "Criando diretório: %(dir_path)s."
    DIR_CREATED = "Diretório criado: %(dir_path)s."
    DIR_EXISTS = "Diretório já existente: %(dir_path)s."
    DIR_ERROR = "Falha ao criar diretório %(dir_path)s: %(error)s."
    
    # === SELENIUM/DRIVER ===
    DRIVER_STARTING = "Inicializando driver do navegador."
    DRIVER_STARTED = "Driver inicializado."
    DRIVER_ERROR = "Falha ao inicializar o driver: %(error)s."
    DRIVER_STOPPING = "Encerrando driver do navegador."
    DRIVER_STOPPED = "Driver encerrado."
    


class SystemMessages:
    """Mensagens do sistema para interface com usuário."""
    
    # === BOAS-VINDAS ===
    WELCOME = "Bem-vindo ao %(app_name)s v%(version)s."
    WELCOME_USER = "Usuário %(user)s autenticado. Sistema inicializado."
    
    # === STATUS ===
    STATUS_READY = "Pronto."
    STATUS_BUSY = "Ocupado: processamento em andamento."
    STATUS_ERROR = "Estado de erro. Consulte os registros."
    STATUS_MAINTENANCE = "Em manutenção."
    
    # === PROGRESSO ===
    PROGRESS_STARTING = "Iniciando processamento."
    PROGRESS_RUNNING = "Processando: %(percentage)d%% concluído."
    PROGRESS_COMPLETED = "Processamento concluído com êxito."
    PROGRESS_CANCELLED = "Processamento cancelado."
        # Mensagens de log (usar placeholders do logging, sem format/concatenação)
    LOG_POST_INSERT_START = "Inserindo novo post. process_id=%s, tp_mode=%s, tp_content=%s"
    LOG_POST_INSERT_SUCCESS = "Post inserido com sucesso. post_id=%s"
    LOG_POST_INSERT_ERROR = "Falha ao inserir post no repositório."
    
    # === ERROS ===
    ERROR_UNEXPECTED = "Erro não tratado: %(error)s."
    FILE_NOT_EXIST = "Arquivo informado não existe: %(file)s."
    FILE_READ_ERROR = "Erro ao ler o arquivo: %(file)s."
    FILE_NOT_FOUND = "Arquivo não encontrado: %(file_path)s."
    EMPTY_DATA = "Nenhum dado encontrado para processar."
    ERR_INVALID_POST_FIELDS = "Valores inválidos para inserção."
    
    # === CONFIRMAÇÕES ===
    CONFIRM_SEND = "Confirmar envio de %(count)d mensagens?"
    CONFIRM_DELETE = "Confirmar exclusão de %(item)s?"
    CONFIRM_RESET = "Confirmar redefinição das configurações?"
    CONFIRM_EXIT = "Confirmar saída do sistema?"
    
    # === SUCESSO ===
    SUCCESS_SENT = "%(count)d mensagens enviadas com êxito."
    SUCCESS_PROCESSED = "%(count)d itens processados com êxito."
    SUCCESS_SAVED = "Dados salvos com êxito."
    SUCCESS_UPDATED = "Configurações atualizadas."
    
    # === ERROS PARA USUÁRIO ===
    ERROR_CONFIG = "Erro de configuração. Verifique o arquivo de parâmetros."
    ERROR_CONNECTION = "Erro de conexão. Verifique a conectividade de rede."
    ERROR_WHATSAPP = "Erro no WhatsApp Web. Tente reconectar."
    ERROR_FILE = "Erro de acesso a arquivo. Verifique permissões."
    ERROR_UNEXPECTED = "Erro inesperado. Consulte os registros."
    
    # === ORIENTAÇÕES ===
    INSTRUCTION_QR = "Leia o QR Code com o WhatsApp."
    INSTRUCTION_WAIT = "Aguarde a conclusão do processamento."
    INSTRUCTION_CHECK_LOGS = "Consulte os registros para mais detalhes."
    INSTRUCTION_RETRY = "Tente novamente ou contate o suporte."


class TimeConstants:
    """Constantes de tempo em segundos."""
    
    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    WEEK = 604800
    MONTH = 2592000  # 30 dias
    
    # Timeouts específicos
    SELENIUM_TIMEOUT = 30
    WHATSAPP_TIMEOUT = 60
    FILE_TIMEOUT = 120
    NETWORK_TIMEOUT = 30
    USER_INPUT_TIMEOUT = 300  # 5 minutos


class ConfigDefaults:
    """Valores padrão para configurações."""
    
    # Aplicação
    VERSION = "5.0.0"
    NAME = "DocPost Bot"
    
    # Timeouts
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    # Selenium
    IMPLICIT_WAIT = 10
    PAGE_LOAD_TIMEOUT = 30
    SCRIPT_TIMEOUT = 30
    
    # WhatsApp
    QR_TIMEOUT = 120
    MESSAGE_DELAY = 2
    FILE_UPLOAD_TIMEOUT = 60
    
    # Arquivos
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    CHUNK_SIZE = 8192
    BACKUP_RETENTION_DAYS = 30
    
    # Logging
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5


def format_log_message(template: str, **kwargs) -> str:
    """
    Formata uma mensagem de log com os parâmetros fornecidos.
    
    Args:
        template: Template da mensagem
        **kwargs: Parâmetros para formatação
        
    Returns:
        Mensagem formatada
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        return f"Erro na formatação da mensagem: parâmetro {e} não encontrado"
    except Exception as e:
        return f"Erro na formatação da mensagem: {e}"


def get_current_timestamp() -> str:
    """Retorna timestamp atual formatado."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_log_entry(level: LogLevel, message: str, **kwargs) -> Dict[str, Any]:
    """
    Cria uma entrada de log estruturada.
    
    Args:
        level: Nível do log
        message: Mensagem (pode ser template)
        **kwargs: Parâmetros para formatação
        
    Returns:
        Dicionário com entrada estruturada
    """
    return {
        "timestamp": get_current_timestamp(),
        "level": level.value,
        "message": format_log_message(message, **kwargs),
        "raw_message": message,
        "parameters": kwargs
    }


# Instâncias globais para uso direto
