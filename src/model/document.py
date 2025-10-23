import logging
from os.path import basename, exists, isfile
from re import sub
from typing import Literal, Optional
from warnings import deprecated
from pdfminer.high_level import extract_text
from joblib import load
from pandas import DataFrame
from sklearn.linear_model import LogisticRegression
from ..config.settings.app_config import AppConfig
from ..config.templates.error_messages import ErrorsMessages

_MODEL_LM: LogisticRegression = load(AppConfig.MODEL_LM)
x = r'C:\Users\jpxns3\OneDrive - Energisa\Documentos\Projetos\Area de testes\vectorizer_tfidf.pkl'

class Document:
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

    def __init__(self) -> None:
        self._type_content = None
        self._type_response = None


    def read(self) -> bool:
        return self._type_content is not None and self._type_response is not None

    def _get_type(self, status: str, content: str, name: str) -> Optional[tuple[Literal['response', 'request', 'request+'], str]]:
        if not content or len(content) < 30:
            return
        temp = DataFrame({
                "content_clean": [content],
                "arquivo": [name]
            })
        predicted = _MODEL_LM.predict(temp)[0]
        self._type_content = predicted
        type_response = None
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
        return type_response, predicted

    
    def set_type(self, status: str, path: str, type_process: Literal['E', 'O']) -> None:
        content = self._extract_text(path)
        if content is None:
            raise Exception("Não foi possível extrair o conteúdo do documento")
        self._name = basename(path)
        self._post_path = path
        result = tuple()
        match type_process:
            case 'E':
                result = self._get_type(status, content, self._name)
                if not result:
                    raise Exception("Não foi possível determinar o tipo do documento")
            case 'O':
                result = self._set_type_standard(content, status)
                if not result:
                    raise Exception("Não foi possível determinar o tipo do documento")
            case _:
                raise Exception("Tipo de processo não suportado")
        # print(result, type_process)
        self._type_response, self._type_content = result

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def post_path(self) -> str:
        return self._post_path

    # @property
    # def content(self) -> Optional[str]:
    #     return self._content

    @property
    def type_content(self) -> Optional[str]:
        return self._type_content

    @property
    def type_response(self) -> Optional[str]:
        return self._type_response

    def _extract_text(self, path:str) -> Optional[str]:
        try:
            return extract_text(path)
        except Exception as e:
            logging.error(f"Erro ao extrair texto: {e}")
            return None

    def _normalize_text(self, texto: str) -> str:
        return sub(r'\s+', '', texto).upper()

    @deprecated('Use set_type method instead')
    def _set_type_advanced(self, path: str, content, name) -> None | Literal['request'] | Literal['request+']:
        if path and (not exists(path) or not isfile(path) or not path.lower().endswith(".pdf")):
            raise FileNotFoundError(ErrorsMessages.FILE_NOT_EXIST.format(file=path))
        name = basename(path)
        content = extract_text(path)
        if not content or len(content) < 30:
            raise ValueError(ErrorsMessages.FILE_CONTENT_NOT_VALID.format(file=path))
        if not content:
            return
        try:
            temp = DataFrame({
                "content_clean": [content],
                "arquivo": [name]
            })
            predicted = _MODEL_LM.predict(temp)[0]
            self._type_content = predicted
            match predicted:
                case "SOLICITAÇÃO DE DOCUMENTOS" | "COMUNICADO DE PENDENCIA":
                    return "request"
                case "RECOLHIMENTO":
                    return  "request+"
                case _:
                    raise Exception("Tipo não não confiaável")
        except Exception:
            logging.error(ErrorsMessages.TYPE_MODEL_ERROR)

    def _set_type_standard(self, content: str, status: str):
        if not exists(self.post_path) or not isfile(self.post_path) or not self._name.lower().endswith(".pdf"):
            raise FileNotFoundError(ErrorsMessages.FILE_NOT_EXIST.format(file=self.post_path))
        if not content:
            return
        match status:
            case "P" | "D" | "I":
                return 'response', self._RESPONSE[status]
            case "A":
                normalized_content = self._normalize_text(content)
                for types, values in self._REQUEST.items():
                    for type_post, subtipos in values.items():
                        if any(subtipo in normalized_content for subtipo in subtipos):
                            return types, type_post
            case _:
                raise ValueError(ErrorsMessages.TYPE_NOT_VALID.format(tipo=status))