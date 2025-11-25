import logging
from time import sleep
import traceback
from typing import Callable, Literal
# from mytools.web.advanced.actions import Actions
from mytools.PyZapp.advanced.actions_v2 import Actions, ActionsConfig
from mytools.structs.files import ProcessesList, Process
from lib.src.controls.file_control import FileControl
from lib.src.controls.ignore_control import IgnoreControl
from lib.src.controls.package_control import PackageControl
from lib.src.controls.post_control import PostControl
from lib.src.data.data_file import DataFile
from lib.src.models.interfaces.routines import Routine
from ..models.domain.client import Client
from ..models.domain.file import File
from ..models.domain.message import Message
from ...config import CONFIG
from ..models.domain.contact import Contact
from ..utils.generic import ExceptionsMessages
from time import monotonic
from random import randint


class Despatch(Routine):
    _ignore_list: list[int] = []
    _post_control: PostControl
    _package_control: PackageControl
    _file_control: FileControl
    _MIN_TIME = 1
    _MAX_TIME = 3

    def __init__(self, config: ActionsConfig) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._post_control = PostControl()
        self._package_control = PackageControl()
        self._file_control = FileControl()
        self.config = config

    def _start_chat(self, action: Actions, number: int | None) -> int | None:
        if number is None or number == 0:
            return
        elif not action.search(number):
            return
        return number

    # Módulos de apoio
    def _wait_until(self, check: Callable[[], bool], timeout: float = 30.0, interval: float = 0.25) -> bool:
        start = monotonic()
        while True:
            try:
                if check():
                    return True
            except Exception as e:
                self.logger.debug(ExceptionsMessages.ERRO_WAIT_UNTIL, e)
            if monotonic() - start >= timeout:
                return False
            self._await(interval)

    def _wait_for_delivery(self, action: Actions, timeout: float = 30.0) -> bool:
        ok = self._wait_until(lambda: bool(action.delivered()), timeout=timeout, interval=0.5)
        if ok:
            self.logger.info(ExceptionsMessages.ENTREGA_CONFIRMADA)
        else:
            self.logger.warning(ExceptionsMessages.ENTREGA_NAO_CONFIRMADA, timeout)
        return ok
    
    # Ações básicas de envio de mensagens e arquivos
    def _send_final_message(self, action: Actions, client: Client) -> None:
        for message in client.message.get_final_messages():
            action.send_message(message)
            self._await(0.5)

    def _send_files(self, action: Actions, client: Client) -> None:
        action.send_file(client.file.post_path)
        match client.message.message_type:
            case 'request':
               action.send_file(CONFIG.path.guia)
            case 'request+':
               action.send_file(CONFIG.path.guia_rec)

    def _send_initial_message(self, action: Actions, client: Client) -> None:
        action.send_message(
            client.message.get_initial_message(
                processo=client.process,
                telefone=Contact.format_tel(
                    tel=client.first_num,
                )
            )
        )

    def _delivery_register(self, action: Actions, client: Client) -> bool:
        status = self._wait_for_delivery(action, timeout=60.0)
        if status:
            self.logger.info(ExceptionsMessages.MENSAGEM_ENTREGUE_SUCESSO)
            action.safe_search(client.process, False)
            action.print_page(client.process)
        else:
            self.logger.warning(ExceptionsMessages.MENSAGEM_ENVIADA_NAO_ENTREGUE)
        return status

    # Construção de clientes a partir dos processos e dados
    def _build_client(self, process: Process, data: DataFile) -> Client | None:
        client = data.get_client(process.id)
        if client is None:
            return None
        file = File.new_file(status=client.status, file=process.files[0], type_process=client.type_process)
        message = Message(file.type_response)
        client.set_file(file)
        client.set_message(message)
        if not client.ready():
            self.logger.warning(ExceptionsMessages.CLIENTE_INCOMPLETO, client)
            return None
        return client
    
    def _await(self, time: int | float | None = None) -> None:
        if time is not None:
            sleep(time)
        else:
            sleep(randint(self._MIN_TIME, self._MAX_TIME))

    def build_clients(self, processes: ProcessesList, data: DataFile) -> list[Client]:
        clients: list[Client] = []
        for process in processes:
            try:
                client = self._build_client(process, data)
                if client is None:
                    continue
            except Exception as e:
                self.logger.error(ExceptionsMessages.ERRO_CONSTRUIR_CLIENTE, e)
                continue
            clients.append(client)
        return clients
    
    # Tipos de envio de mensagens
    def _default_handle(self, action: Actions, client: Client) -> None:
        self._send_initial_message(action, client)
        self._await()
        self._send_files(action, client)
        self._await()
        delivered = self._delivery_register(action, client)
        if delivered:
            client.set_delivered(True)
        self._await()
        self._send_final_message(action, client)

    def _alternative_handle(self, action: Actions, client: Client) -> None:
        action.send_message(
            client.message.get_ag_message(
                processo=client.process,
                telefone=Contact.format_tel(tel=client.first_num), 
                nome_cliente=client.name
            )
        )
    
    # Controlador de envio de mensagens
    def _send_message(self, action: Actions, client: Client, ignore: bool) -> Literal['T', 'A', 'E'] | None:
        # Se modo de resposta for E-mail, não iniciar chat
        if client.response_mode == 'E':
            self.logger.info(ExceptionsMessages.CLIENTE_RECEBE_EMAIL)
            return 'E'
        elif ignore:
            self.logger.info(ExceptionsMessages.CLIENTE_NA_IGNORE_LIST)
            self._file_control.move_to_ag(client.file)
            return 'A'
        selected_number: int | None = None
        try:
            # Tentar iniciar chat com os números disponíveis
            for number in (client.first_num, client.second_num):
                if self._start_chat(action, number) not in (None, 0):
                    selected_number = number
                    break

            if selected_number is None:
                self.logger.warning(ExceptionsMessages.NAO_POSSIVEL_INICIAR_CHAT, client)
                return 'A'
            client.set_used(selected_number)
            self.logger.info(ExceptionsMessages.NUMERO_SELECIONADO, selected_number)
            match client.response_mode:
                case 'T':
                    self._default_handle(action, client)
                    if client.delivered:
                        self._file_control.move_to_ready(client.file)
                    else:
                        self._file_control.move_to_pending(client.file)
                    return 'T'
                case 'A':
                    self._alternative_handle(action, client)
                    self._file_control.move_to_ag(client.file)
                    return 'A'
                case _:
                    self.logger.warning(ExceptionsMessages.MODO_RESPOSTA_DESCONHECIDO, client)
                    return 'A'
        except Exception as exc:
            self.logger.error(ExceptionsMessages.ERRO_ENVIAR_MENSAGEM, client, exc)
            self.logger.debug(ExceptionsMessages.TRACEBACK, traceback.format_exc())
            return None
        finally:
            action.close_chat()

    def _send_messages(self, clients: list[Client]) -> None:
        ignore_set = {ignore.client for ignore in IgnoreControl().get_all_ignores()}
        with Actions(self.config) as action:
            for client in clients:
                self.logger.info(ExceptionsMessages.CLIENTE_ATUAL, client)
                mode = self._send_message(action, client, ignore=(client.process in ignore_set))
                try:
                    if mode is None:
                        self.logger.warning(ExceptionsMessages.ENVIO_NAO_REALIZADO, client)
                        continue
                    match mode:
                        case 'T':
                            package_mode: Literal['default', 'secondary'] = 'default'
                        case 'A':
                            package_mode = 'secondary'
                        case 'E':
                            self.logger.info(ExceptionsMessages.CLIENTE_RECEBE_EMAIL)
                            continue
                        case _:
                            self.logger.warning(ExceptionsMessages.MODO_ENVIO_INVALIDO, client)
                            continue
                    post = self._post_control.fetch_post(client)
                    if post:
                        self.logger.info(ExceptionsMessages.CARTA_JA_ENVIADA, client)
                        post.file_name = client.file.name
                        self.logger.info(ExceptionsMessages.ATUALIZANDO_NOME_ARQUIVO, post)
                    else:
                        self.logger.info(ExceptionsMessages.CRIANDO_NOVO_POST, client)
                        post = self._post_control.create_post_by_client(client)
                    self._post_control.create_post(post)
                    self.logger.info(ExceptionsMessages.POST_REGISTRADO_SUCESSO, post)
                    self._package_control.insert_package_from_client(client, package_mode)
                    self.logger.info(ExceptionsMessages.MENSAGEM_PROCESSADA, client)
                except Exception as exc:
                    self.logger.error(ExceptionsMessages.ERRO_PROCESSAR_POS_ENVIO, client, exc)
                    self.logger.debug(ExceptionsMessages.TRACEBACK, traceback.format_exc())

    def run(self) -> None:
        self.logger.info(ExceptionsMessages.INICIANDO_ROTINA_DESPACHO)
        processes_list = ProcessesList.from_directory(CONFIG.path.main_folder)
        self.logger.info(ExceptionsMessages.PROCESSOS_ENCONTRADOS, processes_list)
        data = DataFile.from_data(CONFIG.data_file, processes_list)
        self.logger.info(ExceptionsMessages.DADOS_CARREGADOS)
        self.logger.info(ExceptionsMessages.CONSTRUINDO_PACOTES)
        clients = self.build_clients(processes_list, data)
        if not clients:
            self.logger.info(ExceptionsMessages.NENHUM_PACOTE_ENVIAR)
            return
        self.logger.info(ExceptionsMessages.PACOTES_CONSTRUIDOS_SUCESSO, len(clients))
        self.logger.info(ExceptionsMessages.INICIANDO_ENVIO_MENSAGENS)
        self._send_messages(clients)
        self.logger.info(ExceptionsMessages.ROTINA_DESPACHO_FINALIZADA)