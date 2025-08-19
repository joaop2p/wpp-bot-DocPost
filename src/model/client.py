from .document import Document
from .message import Message
from .contact import Contact

class Client:
    _post: Document
    _process: int
    contact: Contact
    message: Message
    _ind_proc: str
    _name: str
    _uc: int
    _specify_type: str
    _problem: str
    _response_mode: str
    
    def __init__(self, post: Document, message: Message, process: int, contact: Contact, ind_proc: str, name: str, uc:int, response_mode: str) -> None:
        self._post = post
        self.contact = contact
        self._process = process
        self._ind_proc = ind_proc
        self._name = name
        self.message = message
        self._uc = uc
        self._response_mode = response_mode
        self._problem = ''

    def __str__(self) -> str:
        attrs = vars(self)
        return f'Client({"\t".format(attrs)})'

    @property
    def getUC(self) -> int:
        return self._uc
        
    @property
    def getPost(self) -> Document:
        return self._post

    @property
    def getProcess(self) -> int:
        return self._process

    @property
    def getIndProc(self) -> str:
        return self._ind_proc

    @property
    def getName(self) -> str:
        return self._name
    @property
    def getSpecify_type(self) -> str:
        return self._specify_type
    @property
    def getResponseMode(self) -> str:
        return self._response_mode

    def getProblem(self) -> str | None:
        return self._problem

    @property
    def ready(self) -> bool:
        for attr in vars(self):
            if getattr(self, attr) is None:
                self._problem = attr
                return False
        return True