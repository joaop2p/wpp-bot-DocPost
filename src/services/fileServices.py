from shutil import move
from tkinter.filedialog import askopenfilename
import numpy as np
from re import search

from ..config.settings.paths import Paths
from ..utils.exceptions.fileExceptions import FileExceptions
from ..config.templates.error_messages import ErrorsMessages

class FileServices:
    @staticmethod
    def buscador(target: str, files: list[str]) -> None | str:
        'Encontra itens em um array a partir de um critério'
        matching_elements = np.nonzero((np.char.find(files, target) > -1))[0]   
        if matching_elements.size > 0:
            file = files[matching_elements.item()]
            return file if len(file) > 0 else None
    
    @staticmethod
    def file_selector(value = "") -> str:
        'Selecione um arquivo apartir de uma interface'
        file = askopenfilename(filetypes=[("Text with headers", "*txt")]) if not value else value
        if not file:
            raise FileExceptions(ErrorsMessages.NO_FILE_SELECTED)
        return file

    @staticmethod
    def getProcessFromFile(file_name: str) -> str | None:
        'Encontra o número do processo na nomeclatura do arquivo.'
        match = search(r"20[1-2]\d{6}", file_name)
        if match is not None:
            return match.group()
    
    @staticmethod
    def getProcessFromFiles(files: list[str]) -> tuple[int]:
        'Encontra um conjunto de processos na nomeclatura dos arquivos de um local.'
        processos = set()
        for item in files:
            process = FileServices.getProcessFromFile(item)
            if process is not None and process not in processos:
                processos.add(int(process))
        return tuple(processos)
    
    @staticmethod
    def moveFile(file: str, delivered: bool, ag: bool = False) -> None:
        'Move o arquivo para a pasta de entregues ou não entregues.'
        if ag:
            move(file, Paths.NOT_SENDED_REPOSITORY)
        else:
            if delivered:
                move(file, Paths.SENDED_REPOSITORY)
            else:
                move(file, Paths.REPOSITORY_TEMP)
