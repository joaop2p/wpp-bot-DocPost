import logging
from time import sleep
import traceback
from typing import Callable, Literal
from mytools.web.advanced.actions import Actions
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
from time import monotonic
from random import randint


class Despatch(Routine):
    _ignore_list: list[int] = []
    _post_control: PostControl
    _package_control: PackageControl
    _file_control: FileControl
    _SHORT_LENGTH = [0.5, 2]

    def __init__(self, actions: Actions) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._post_control = PostControl()
        self._package_control = PackageControl()
        self._file_control = FileControl()
        self.actions = actions

    def _start_chat(self, number: int | None) -> int | None:
        if number is None or number == 0:
            return
        elif not self.actions.search(number):
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
                self.logger.debug("Erro durante wait_until: %s", e)
            if monotonic() - start >= timeout:
                return False
            sleep(interval)

    def _wait_for_delivery(self, timeout: float = 30.0) -> bool:
        ok = self._wait_until(lambda: bool(self.actions.delivered()), timeout=timeout, interval=0.5)
        if ok:
            self.logger.info("Entrega confirmada dentro do timeout.")
        else:
            self.logger.warning("Entrega não confirmada dentro do timeout de %.1fs.", timeout)
        return ok
    
    # Ações básicas de envio de mensagens e arquivos
    def _send_final_message(self, client: Client) -> None:
        for message in client.message.get_final_messages():
            self.actions.send_message(message)
            sleep(0.5)

    def _send_files(self, client: Client) -> None:
        self.actions.send_file(client.file.post_path)
        match client.message.message_type:
            case 'request':
               self.actions.send_file(CONFIG.path.guia)
            case 'request+':
               self.actions.send_file(CONFIG.path.guia_rec)

    def _send_initial_message(self, client: Client) -> None:
        self.actions.send_message(
            client.message.get_initial_message(
                processo=client.process,
                telefone=Contact.format_tel(
                    tel=client.first_num,
                )
            )
        )

    def _delivery_register(self, client: Client) -> bool:
        status = self._wait_for_delivery(timeout=60.0)
        if status:
            self.logger.info("Mensagem entregue com sucesso.")
            self.actions.safe_search(client.process, False)
            self.actions.print_page(client.process)
        else:
            self.logger.warning("Mensagem enviada mas não entregue.")
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
            self.logger.warning("Cliente incompleto: %s", client)
            return None
        return client

    def build_clients(self, processes: ProcessesList, data: DataFile) -> list[Client]:
        clients: list[Client] = []
        for process in processes:
            try:
                client = self._build_client(process, data)
                if client is None:
                    continue
            except Exception as e:
                self.logger.error("Erro ao construir cliente: %s", e)
                continue
            clients.append(client)
        return clients
    
    # Tipos de envio de mensagens
    def _default_handle(self, client: Client):
        self._send_initial_message(client)
        sleep(randint(2,4))
        self._send_files(client)
        sleep(randint(2,4))
        delivered = self._delivery_register(client)
        if delivered:
            client.set_delivered(True)
        sleep(randint(2,4))
        self._send_final_message(client)

    def _alternative_handle(self, client: Client) -> None:
        self.actions.send_message(
            client.message.get_ag_message(
                processo=client.process,
                telefone=Contact.format_tel(tel=client.first_num), 
                nome_cliente=client.name
            )
        )
    
    # Controlador de envio de mensagens
    def _send_message(self, client: Client, ignore: bool) -> Literal['T', 'A', 'E'] | None:
        # Se modo de resposta for E-mail, não iniciar chat
        if client.response_mode == 'E':
            self.logger.info("Cliente deve receber a carta via E-mail.")
            return 'E'
        elif ignore:
            self.logger.info("Cliente está na lista de ignore, pulando envio de mensagem.")
            self._file_control.move_to_ag(client.file)
            return 'A'
        selected_number: int | None = None
        try:
            # Tentar iniciar chat com os números disponíveis
            for number in (client.first_num, client.second_num):
                if self._start_chat(number) not in (None, 0):
                    selected_number = number
                    break

            if selected_number is None:
                self.logger.warning("Não foi possível iniciar o chat para o cliente: %s", client)
                return 'A'
            client.set_used(selected_number)
            self.logger.info("Número selecionado: %d", selected_number)
            match client.response_mode:
                case 'T':
                    self._default_handle(client)
                    if client.delivered:
                        self._file_control.move_to_ready(client.file)
                    else:
                        self._file_control.move_to_pending(client.file)
                    return 'T'
                case 'A':
                    self._alternative_handle(client)
                    self._file_control.move_to_ag(client.file)
                    return 'A'
                case _:
                    self.logger.warning("Modo de resposta desconhecido para o cliente: %s", client)
                    return 'A'
        except Exception as exc:
            self.logger.error("Erro ao enviar mensagem para o cliente %s: %s", client, exc)
            self.logger.debug("Traceback: %s", traceback.format_exc())
            return None
        finally:
            self.actions.exit_chat_from_message_box()

    def _send_messages(self, clients: list[Client]) -> None:
        ignore_set = {ignore.client for ignore in IgnoreControl().get_all_ignores()}
        for client in clients:
            self.logger.info("Cliente atual: %s", client)
            mode = self._send_message(client, ignore=(client.process in ignore_set))
            try:
                if mode is None:
                    self.logger.warning("Envio não realizado para o cliente: %s", client)
                    continue
                match mode:
                    case 'T':
                        package_mode: Literal['default', 'secondary'] = 'default'
                    case 'A':
                        package_mode = 'secondary'
                    case 'E':
                        self.logger.info("Cliente deve receber a carta via E-mail.")
                        continue
                    case _:
                        self.logger.warning("Modo de envio inválido para o cliente: %s", client)
                        continue
                post = self._post_control.fetch_post(client)
                if post:
                    self.logger.info("Carta já enviada anteriormente para o cliente: %s", client)
                    post.file_name = client.file.name
                    self.logger.info("Atualizando nome do arquivo no post: %s", post)
                else:
                    self.logger.info("Criando novo post para o cliente: %s", client)
                    post = self._post_control.create_post_by_client(client)
                self._post_control.create_post(post)
                self.logger.info("Post registrado com sucesso: %s", post)
                self._package_control.insert_package_from_client(client, package_mode)
                self.logger.info("Mensagem processada para o cliente: %s", client)
            except Exception as exc:
                self.logger.error("Erro ao processar pós-envio para o cliente %s: %s", client, exc)
                self.logger.debug("Traceback: %s", traceback.format_exc())

    # Execução do launcher
    def run(self) -> None:
        self.logger.info("Iniciando rotina de despacho de mensagens...")
        # path = r'\\fileserverpb.scl.corp\Dados\SGP\02.Processos\06.Gestão de Danos Elétricos\06. Processos Dgital\Cartas Pedentes de Envio\Nova pasta'
        processes_list = ProcessesList.from_directory(CONFIG.path.main_folder)
        self.logger.info("Processos encontrados: %s", processes_list)
        data = DataFile.from_data(CONFIG.data_file, processes_list)
        self.logger.info("Dados carregados.")
        self.logger.info("Construíndo pacotes de envio.")
        clients = self.build_clients(processes_list, data)
        if not clients:
            self.logger.info("Nenhuma pacote para enviar.")
            return
        self.logger.info("Pacotes construídos com sucesso. Total de pacotes: %d", len(clients))
        self.logger.info("Iniciando envio de mensagens via WhatsApp Web.")
        self.actions.start_whatsapp()
        self._send_messages(clients)
        self.logger.info("Rotina de despacho de mensagens finalizada.")