from calendar import c
import logging
from os.path import basename, exists, isfile
from re import sub
from turtle import st
from typing import Literal, Optional, Tuple, cast
from pdfminer.high_level import extract_text
from joblib import load
from pandas import DataFrame
from sklearn.linear_model import LogisticRegression
from win32security import GetFileSecurity, LookupAccountSid, OWNER_SECURITY_INFORMATION
from ....config.settings import Config
from mytools.structs.files import File as PackageFile
from ....config import LOG

logger = logging.getLogger(__name__)

# Tipagem auxiliar para o retorno do tipo de conteúdo
ContentTypeResponse = Tuple[Literal['response', 'request', 'request+'], str]


class File:
    """Representa um arquivo a ser classificado e interpretado.

    Responsabilidades:
    - Extrair texto do PDF
    - Classificar o tipo via modelo de ML (E) ou via regras (O)
    - Determinar o tipo de resposta / conteúdo
    """

    # Configuração e constantes
    MIN_CONTENT_LENGTH = 30

    # Modelo ML carregado sob demanda (cache em nível de classe)
    _MODEL_LM: Optional[LogisticRegression] = None

    _RESPONSE = {
        'D': 'DEFERIDO',
        'I': 'INDEFERIDO',
        'P': 'PARCIALMENTE DEFERIDO',
    }
    _REQUEST = {
        'request+': {
            'RECOLHIMENTO': {'COMUNICADODERECOLHIMENTO'}
        },
        'request': {
            'COMUNICADO DE PENDENCIA': {
                'COMUNICADODEPENDÊNCIA',
                'COMUNICAÇÃODEPENDÊNCIA'
            },
            'SOLICITAÇÃO DE DOCUMENTOS': {
                'SOLICITAÇÃODEDOCUMENTOS',
                'SOLICITAÇÃODERESSARCIMENTO'
            }
        }
    }
    # vars
    _type_content: str
    _name: str
    _type_response: str
    _post_path: str
    _creator: str

    def __str__(self) -> str:
        return f'File(name={self._name}, type_response={self._type_response}, type_content={self._type_content}, post_path={self._post_path}, creator={self._creator})'


    @classmethod
    def _get_type(cls, status: str, content: str, name: str) -> Optional[ContentTypeResponse]:
        """Classifica o documento via modelo de ML.

        - Retorna uma tupla (tipo_resposta, tipo_conteudo) quando possível;
        - Retorna None quando não há conteúdo suficiente.
        """
        if not content or len(content) < cls.MIN_CONTENT_LENGTH:
            return None

        model = cls._get_or_load_model()
        temp = DataFrame({
            "content_clean": [content],
            "arquivo": [name]
        })
        predicted: str = model.predict(temp)[0]
        cls._type_content = predicted

        type_response: Optional[str] = None
        match status:
            case "A":
                match predicted:
                    case "SOLICITAÇÃO DE DOCUMENTOS" | "COMUNICADO DE PENDENCIA":
                        type_response = "request"
                    case "RECOLHIMENTO":
                        type_response = "request+"
                    case _:
                        raise Exception(f"Tipo não confiável: {predicted}")
            case 'C':
                raise Exception("Tipo não confiável: Status do processo é cancelado")
            case _:
                type_response = 'response'

        return (type_response, predicted) if type_response else None

    @classmethod
    def new_file(cls, status: str, file: PackageFile, type_process: Literal['E', 'O']) -> 'File':
        logger.debug(LOG.FILE_PROCESSING, {"file_path": file.directory})

        path = file.directory
        if not path or not exists(path) or not isfile(path):
            logger.error(LOG.FILE_READ_ERROR, {"file_path": path})
            raise FileNotFoundError("Arquivo não encontrado ou inválido")

        content = cls._extract_text(path)
        if not content or len(content) < cls.MIN_CONTENT_LENGTH:
            logger.error(LOG.FILE_READ_ERROR, {"file_path": path})
            raise ValueError("Não foi possível extrair o conteúdo do documento")

        if type_process == 'E':
            result = cls._get_type(status, content, file.name)
        elif type_process == 'O':
            result = cls._set_type_standard(content, status, file.name)
        else:
            logger.error(LOG.FILE_READ_ERROR, {"file_path": path})
            raise ValueError("Tipo de processo não suportado")

        if not result:
            logger.error(LOG.FILE_READ_ERROR, {"file_path": path})
            raise RuntimeError("Não foi possível determinar o tipo do documento")

        type_response, type_content = result
        if not type_response or not type_content:
            logger.error(LOG.FILE_READ_ERROR, {"file_path": path})
            raise RuntimeError("Tipo de resposta ou conteúdo inválido")
        creator = cls._get_creator(path)
        instance = cls()
        instance._name = file.name
        instance._post_path = path
        instance._type_response = type_response
        instance._type_content = type_content
        instance._creator = creator
        logger.info(LOG.FILE_PROCESSED, {"file_path": path})
        return instance

    @staticmethod
    def _extract_text(path:str) -> Optional[str]:
        try:
            logger.debug(LOG.FILE_READING, {"file_path": path})
            text = extract_text(path)
            logger.debug(LOG.FILE_READ_SUCCESS, {"file_path": path})
            return text
        except Exception as e:
            logger.exception(LOG.FILE_READ_ERROR, {"file_path": path, "error": str(e)})
            return None

    @staticmethod
    def _normalize_text(texto: str) -> str:
        return sub(r'\s+', '', texto).upper()

    @classmethod
    def _set_type_standard(cls, content: str, status: str, name: str) -> Optional[ContentTypeResponse]:
        if name and content:
            match status:
                case "P" | "D" | "I":
                    return ('response', cls._RESPONSE[status])
                case "A":
                    normalized_content = cls._normalize_text(content)
                    for types, values in cls._REQUEST.items():
                        for type_post, subtipos in values.items():
                            if any(subtipo in normalized_content for subtipo in subtipos):
                                return cast(ContentTypeResponse, (types, type_post))
                case _:
                    logger.error("Status de processo inválido: %s", status)
                    raise ValueError(f"Status de processo inválido: {status}")
        else:
            raise Exception("Nome do arquivo não definido")
    
    @staticmethod
    def _get_creator(path: str) -> str:
        try:
            sd = GetFileSecurity(path, OWNER_SECURITY_INFORMATION)
            owner_sid = sd.GetSecurityDescriptorOwner()
            name = LookupAccountSid(None, owner_sid)[0]
            return name
        except Exception as e:
            logger.exception(LOG.FILE_PERMISSION_ERROR, {"file_path": path})
        return "system"

    # === Utilitários internos ===
    @classmethod
    def _get_or_load_model(cls) -> LogisticRegression:
        """Carrega o modelo de ML sob demanda e o mantém em cache."""
        if cls._MODEL_LM is None:
            model_path = Config().model_lm
            logger.debug(LOG.FILE_READING, {"file_path": model_path})
            cls._MODEL_LM = load(model_path)
        return cast(LogisticRegression, cls._MODEL_LM)

    @property
    def creator(self) -> str:
        return self._creator

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def post_path(self) -> str:
        return self._post_path

    @property
    def type_content(self) -> str:
        return self._type_content

    @property
    def type_response(self) -> str:
        return self._type_response