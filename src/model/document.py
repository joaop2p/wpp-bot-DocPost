import logging
from os.path import basename, exists, isfile
from re import sub
from typing import Optional
from pdfminer.high_level import extract_text
from joblib import load
from pandas import DataFrame
from sklearn.linear_model import LogisticRegression
from ..config.settings.app_config import AppConfig
from ..config.templates.error_messages import ErrorsMessages

_MODEL_LM: LogisticRegression = load(AppConfig.MODEL_LM)

class Document:
    _DOCUMENT_TYPES = {
        'response': {
            'DEFERIMENTO': {
                'COMUNICADODEPROCEDENTE',
                'COMUNICADODEPROCEDENTE/IMPROCEDENTE'
            },
            'INDEFERIMENTO': {
                'COMUNICADODEINDEFERIMENTO',
                'COMUNICADODEIMPROCEDENTE'
            },
        },
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

    def __init__(self, post_path: str, tipo: str) -> None:
        self._post_path = post_path
        self._name = basename(post_path)
        self._content = self._extract_text()
        self._type_content = None
        self._type_response = None
        match tipo:
            case "E":
                self._set_type_advanced()
            case "O":
                self._set_type_standard()
            case _:
                raise ValueError(ErrorsMessages.TYPE_NOT_VALID.format(tipo=tipo))

    def read(self) -> bool:
        return self._type_content is not None and self._type_response is not None

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def post_path(self) -> str:
        return self._post_path

    @property
    def content(self) -> Optional[str]:
        return self._content

    @property
    def type_content(self) -> Optional[str]:
        return self._type_content

    @property
    def type_response(self) -> Optional[str]:
        return self._type_response

    def _extract_text(self) -> Optional[str]:
        try:
            return extract_text(self.post_path)
        except Exception as e:
            logging.error(f"Erro ao extrair texto: {e}")
            return None

    def _normalize_text(self, texto: str) -> str:
        return sub(r'\s+', '', texto).upper()

    def _set_type_advanced(self) -> None:
        if not self._content:
            return
        try:
            temp = DataFrame({
                "content_clean": [self._content],
                "arquivo": [self._name]
            })
            predicted = _MODEL_LM.predict(temp)[0]
            self._type_content = predicted
            match predicted:
                case "SOLICITAÇÃO DE DOCUMENTOS" | "COMUNICADO DE PENDENCIA":
                    self._type_response = "request"
                case "RECOLHIMENTO":
                    self._type_response = "request+"
                case _:
                    self._type_response = "response"
        except Exception:
            logging.error(ErrorsMessages.TYPE_MODEL_ERROR)

    def _set_type_standard(self) -> None:
        if not exists(self.post_path) or not isfile(self.post_path) or not self._name.lower().endswith(".pdf"):
            raise FileNotFoundError(ErrorsMessages.FILE_NOT_EXIST.format(file=self.post_path))
        if not self._content:
            return
        normalized_content = self._normalize_text(self._content)
        for tipo, valores in self._DOCUMENT_TYPES.items():
            for tipo_carta, subtipos in valores.items():
                if any(subtipo in normalized_content for subtipo in subtipos):
                    self._type_content = tipo_carta
                    self._type_response = tipo
                    return