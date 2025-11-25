from calendar import c
import re
import stat
from typing import Literal
from pandas import Series
from .contact import Contact
from .file import File
from .message import Message

class Client(Contact):
    _name: str
    _file: File
    _message: Message
    _process: int
    _status: str
    _response_mode: str
    _type_process: Literal['E', 'O']
    _delivered: bool = False

    def __init__(self, num: int, num2: int, process: int, status: str, response_mode: str, type_process: Literal['E', 'O'], name: str) -> None:
        super().__init__(num, num2)
        self._process = process
        self._status = status
        self._response_mode = response_mode
        self._type_process = type_process
        self._name = name

    def __str__(self) -> str:
        return f'Client(process={self._process}, status={self._status}, response_mode={self._response_mode}, type_process={self._type_process}, first_num={self.first_num}, second_num={self.second_num})'

    def set_file(self, file: File) -> None:
        self._file = file

    def set_message(self, message: Message) -> None:
        self._message = message

    def set_delivered(self, status: bool) -> None:
        self._delivered = status

    @property
    def delivered(self) -> bool: return self._delivered
    @property
    def file(self) -> File: return self._file
    @property
    def message(self) -> Message: return self._message
    @property
    def process(self) -> int: return self._process
    @property
    def status(self) -> str: return self._status
    @property
    def response_mode(self) -> str: return self._response_mode
    @property
    def type_process(self) -> Literal['E', 'O']: return self._type_process
    @property
    def name(self) -> str: return self._name
    @property
    def used(self) -> int: return self._used
    
    def ready(self) -> bool:
        for attr in vars(self):
            if getattr(self, attr) is None:
                return False
        return True
    
    @classmethod
    def from_series(cls, data: Series) -> 'Client':
        return cls(
            process=data['COD_PROCESSO'], num=data['TEL_TRAB_SOLIC'],
            num2=data['CELULAR_SOLIC'], status=data['IND_PROC'],
            response_mode=data['IND_TIPO_RESPOSTA_CLIENTE'], type_process=data['TIPO_ITEM'],
            name=data['NOM_SOLICITANTE']
            )