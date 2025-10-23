from pandas import DataFrame, Series, read_table, Grouper
from os.path import exists
from ..models.domain.client import Client
from ...config import SYS_MSG
from packages.files import ProcessesList

class DataFile:
    _df: DataFrame
    _cols: tuple[str, ...] = ('COD_PROCESSO', 'CELULAR_SOLIC', 'TEL_TRAB_SOLIC', 'NOM_SOLICITANTE', 'NUM_CDC', 'IND_TIPO_RESPOSTA_CLIENTE', 'IND_PROC', 'TIPO_ITEM')

    def __init__(self) -> None:
        self._df = DataFrame()

    def __str__(self) -> str:
        return str(self._df)

    @classmethod
    def from_data(cls, path: str, processes: ProcessesList) -> 'DataFile':
        if not exists(path) or not path.lower().endswith('.txt'):
            raise FileNotFoundError('Arquivo não encontrado ou formato inválido. Apenas arquivos .txt são suportados.')
        try:
            df = read_table(path, usecols=cls._cols, dtype={'CELULAR_SOLIC': int, 'TEL_TRAB_SOLIC': int}, encoding='ansi')
        except Exception as e:
            raise ValueError(SYS_MSG.FILE_READ_ERROR, str(e))
        if df.empty:
            raise ValueError(SYS_MSG.EMPTY_DATA)
        instance = cls()
        df = cls._fill(df, processes)
        instance._df = df
        return instance

    @staticmethod
    def _fill(df: DataFrame, processes: ProcessesList) -> DataFrame:
        df.fillna(0, inplace=True)
        df[["CELULAR_SOLIC", "TEL_TRAB_SOLIC"]] = df[["CELULAR_SOLIC", "TEL_TRAB_SOLIC"]].astype(int)
        df = df.loc[df['COD_PROCESSO'].isin(processes.to_list())]
        return df
    
    def find_process(self, process: int) -> Series | None:
        if self._df.empty:
            raise ValueError('Você deve carregar os dados antes de realizar buscas.')
        value = self._df[self._df['COD_PROCESSO'] == process].squeeze()
        if not isinstance(value, Series):
            return None
        return value        
    
    def get_client(self, process: int) -> Client | None:
        data = self.find_process(process)
        if data is None:
            return None
        return Client.from_series(data)
    
    @property
    def df(self) -> DataFrame:
        if self._df.empty:
            raise ValueError('Dados não carregados. Use o método set_data() para carregar os dados.')
        return self._df