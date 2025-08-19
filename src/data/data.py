from os.path import isfile, basename
from pandas import DataFrame, read_table
from typing import Iterable
from ..config.templates.error_messages import ErrorsMessages
from ..config.templates.logging_messages import LoggingMessages
from ..utils.exceptions.dataExceptions import DataException

class Data:
    def __init__(self) -> None:
        super().__init__()
        
    def read(self, path: str) -> None:
        if not isfile(path):
            raise DataException(ErrorsMessages.FILE_NOT_EXIST.format(file = path))
        if not basename(path).lower().endswith('.txt'):
            raise DataException(ErrorsMessages.EXTENSION_NOT_SUPPORTED)
        try:
            df = read_table(path, encoding="ansi")
        except Exception:
            raise DataException(ErrorsMessages.DATA_CRITICAL_ERROR)
        self._df = self._fill(df)

    def _fill(self, df: DataFrame) -> DataFrame:
        df = df.fillna(0)
        df[["CELULAR_SOLIC", "TEL_TRAB_SOLIC", "TEL_SOLICITANTE"]] = df[["CELULAR_SOLIC", "TEL_TRAB_SOLIC", "TEL_SOLICITANTE"]].astype(int)
        return df

    def getInfo(self, process: int) -> DataFrame:
        return self._df.loc[self._df.COD_PROCESSO == process]

    def getData(self) -> DataFrame:
        return self._df
    
