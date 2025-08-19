from datetime import datetime
import logging
from sqlite3 import Cursor, connect
import warnings

from ..config.settings.app_config import AppConfig

from ..config.templates.logging_messages import LoggingMessages

warnings.filterwarnings("ignore", category=DeprecationWarning)

class Connection():
    _cursor: Cursor

    def __init__(self) -> None:
        self.con = connect(AppConfig.DATA_BASE_FILE)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Conexão com o banco de dados estabelecida.")
        self._cursor = self.con.cursor()

    def is_blocked(self, telefone: int, processo: int) -> bool:
        'Verifica se o telefone e processo estão na lista de bloqueio.'
        res = self._cursor.execute(f"SELECT telefone, processo FROM tb_not_disturbution WHERE telefone = {telefone} AND processo = {processo}")
        return len(res.fetchall()) > 0

    def insert(self, processo: int,entregue: bool, tipo: str|None = None,
               nome_arquivo: str|None = None, sit: str|None = None,
               uc: int|None = None,
               numero_usado: int|None = None, data: datetime = datetime.now(),
               registrado: bool = False,
               agencia: bool = False,
               specify_type: str = "") -> None:
        'Insere ou atualiza o registro de envio no banco de dados.'
        res = self._cursor.execute(f"SELECT processo from tb_post_sended where processo = {processo}")
        if len(res.fetchall()) < 1:
            self._insert(processo=processo, tipo= tipo, nome_arquivo=nome_arquivo, sit=sit, numero_usado=numero_usado, entregue=entregue, data=data, agencia=agencia, uc=uc, registrado=registrado, specify_type=specify_type)
        else:
            self._update(processo=processo,tipo=tipo, nome_arquivo=nome_arquivo, sit=sit, numero_usado=numero_usado, entregue=entregue, data=data, specify_type=specify_type)

    def _insert(self, processo: int,entregue: bool, tipo: str|None,
               nome_arquivo: str|None, sit: str|None,
               uc:int|None,
               specify_type: str,
               numero_usado: int|None, agencia: bool,registrado:bool, data: datetime = datetime.now(),
               ) -> None:
        'Insere um novo registro de envio no banco de dados.'
        self._cursor.execute(f"""
            INSERT INTO tb_post_sended (processo, data, tipo, nome_arquivo, sit, numero_usado, entregue, agencia, unidade, registrado, specify_type)
            VALUES ({processo}, '{data}', '{tipo}', '{nome_arquivo}', '{sit}', {numero_usado}, {entregue}, {agencia}, {uc}, {registrado}, '{specify_type}')
        """)
        self.con.commit()
        self.logger.info(LoggingMessages.INSERT_SUCCESS)

    def select(self) :
        result = self._cursor.execute("select processo, numero_usado from tb_post_sended where entregue = 0 and agencia = 0 and numero_usado != 0")
        return result.fetchall()

    def update_status(self, processo: int, entregue: bool) -> None:
        self._cursor.execute(f"UPDATE tb_post_sended SET entregue = {entregue} WHERE PROCESSO = {processo}")
        self.con.commit()
        self.logger.info(f"Status do processo {processo} atualizado para {'entregue' if entregue else 'não entregue'}.")

    def _update(self, processo: int,entregue: bool,specify_type: str, tipo: str|None = None,
               nome_arquivo: str|None = None, sit: str|None = None,
               numero_usado: int|None = None, data: datetime = datetime.now()):
        self._cursor.execute(f"""
            UPDATE tb_post_sended
            SET entregue = {entregue}, data = '{data}', tipo = '{tipo}', 
            nome_arquivo = '{nome_arquivo}', sit = '{sit}', numero_usado = {numero_usado},
            agencia = FALSE,
            specify_type= '{specify_type}'
            WHERE processo = {processo}
        """)
        self.con.commit()
        self.logger.info(f"Registro do processo {processo} atualizado com sucesso.")

    def kill(self) -> None:
        self.con.close()