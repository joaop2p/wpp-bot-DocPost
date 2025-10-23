

from datetime import datetime
import logging
from os import listdir
from os.path import join
from time import sleep
from typing import Iterable
from pandas import DataFrame
from .model.document import Document
from .services.fileServices import FileServices
from .config.settings.app_config import AppConfig
from .data.connection import Connection
from .model.client import Client
from .model.message import Message
from .model.contact import Contact
from shutil import Error
from .actions import Actions
from .data.data import Data
from .config.templates.error_messages import ErrorsMessages
from .config.templates.logging_messages import LoggingMessages

class Launcher(Data):
    current_client: Client
    
    def __init__(self, actions_instance: Actions) -> None:
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.actions = actions_instance
        self.black_list = []

    def capitalizeName(self, name: str) -> str:
        return ' '.join([sub.capitalize() for sub in name.split(" ")])
    
    def start_chat(self, number: int | None) -> int | None:
        if number is None or number in self.black_list:
            return 
        if number == 0 or not self.actions.search(number):
            self.black_list.append(number)
            return
        return number
    
    def send_final_messages(self) -> None:
        sleep(2)
        for final_message in Message.get_final_messages():
            self.actions.send_message(final_message)

    def send_initial_message(self, number: int, client: Client) -> None:
        self.actions.send_message(
            client.message.getMessage_text.format(
                processo=client.getProcess,
                telefone=Contact.format_tel(str(number), True)
            )
        )

    def buildClients(self) -> Iterable[Client] | None:
        files = listdir(AppConfig.MAIN_FOLDER)
        processes = FileServices.getProcessFromFiles(files)
        if not processes:
            logging.warning(LoggingMessages.NO_PROCESS_AVAILABLE)
            return
        contacts: list[Client] = []
        for process in processes:
            self.logger.info(LoggingMessages.CURRENT_PROCESS.format(process))
            data = self.getInfo(process)
            if data.empty:     
                self.logger.info(LoggingMessages.NO_DATA_AVAILABLE)
                continue
            row =  data.iloc[0]
            post = FileServices.buscador(str(row.COD_PROCESSO), files)
            if post is None:
                continue
            temp_post = join(AppConfig.MAIN_FOLDER, post)
            document = Document()
            # try:
            document.set_type(row.IND_PROC, temp_post, row.TIPO_ITEM)
            # except Exception as e:
            #     self.logger.error(ErrorsMessages.DOCUMENT_TYPE_ERROR.format(error_message=str(e)))
            #     continue
            new_contact = Contact(num1=row.TEL_TRAB_SOLIC, num2=row.CELULAR_SOLIC)
            # print(document.type_response)
            # print(document.type_content)
            if document.read():
                current_client = Client(
                    post=document,
                    process=process,
                    contact=new_contact,
                    ind_proc=row.IND_PROC,
                    name = row.NOM_SOLICITANTE,
                    message=Message(message_type=document.type_response), # type: ignore
                    uc=row.NUM_CDC,
                    response_mode=row.IND_TIPO_RESPOSTA_CLIENTE
                    )
                if current_client.ready:
                    contacts.append(current_client)   
                else: 
                    self.logger.error(
                        ErrorsMessages.ATT_IS_NONE.format(
                            attr=current_client.getProblem()
                            ))
            else:
                self.logger.error(ErrorsMessages.NO_MESSAGE_AVAILABLE.format(processo=process))
        return contacts  
    
    def option_send_Message(self, connection: Connection, client: Client) -> None:
        number = self.start_chat(client.contact.getNum1())
        if number is not None and number != 0:
            self.actions.send_message(
                message=Message.get_ag_message().format(
                    processo=client.getProcess,
                    telefone=Contact.format_tel(str(number), True),
                    nome_cliente=client.getName
                    ))
        connection.insert(
            # data = datetime(2025, 8, 6, 17,20,0,0),
            processo=client.getProcess,
            entregue=False,
            agencia=True,
            nome_arquivo=client.getPost.name,
            tipo=client.message.getMessage_type,
            sit=client.getIndProc,
            uc=client.getUC, 
            numero_usado=number if number is not None else 0,
            registrado=False,
            )
        FileServices.moveFile(client.getPost.post_path, False, ag=True)
        self.actions.exit_chat()
    
    def handle_delivery_status(self, number: int, connection: Connection, data: datetime, client: Client) -> None:
        status = self.actions.entregue()
        self.actions.safe_search(client.getProcess)
        if status:
            self.actions.print_page(client.getProcess)
        try:
            FileServices.moveFile(client.getPost.post_path, status)
        except Error as e:
            self.logger.error(ErrorsMessages.ERROR_LOG.format(error_message=str(e), error_details=''))
        connection.insert(
            processo=client.getProcess,
            tipo=client.message.getMessage_type,
            nome_arquivo=client.getPost.name,
            sit=client.getIndProc,
            numero_usado=number,
            entregue=status,
            data=data,
            registrado=False,
            uc=client.getUC,
            specify_type=client.getPost.type_content  # type: ignore
        )

    def send_files(self, client: Client) -> None:
        self.actions.send_file(client.getPost.post_path)
        sleep(5)
        if client.message.getMessage_type == "request":
            self.actions.send_file(AppConfig.GUIA)
        elif client.message.getMessage_type == "request+":
            self.actions.send_file(AppConfig.GUIA_REC)
        sleep(5)

    def default_send_messages(self, connection: Connection, client: Client) -> bool:
        number = self.start_chat(client.contact.getNum1())
        if number is None:
            number = self.start_chat(client.contact.getNum2())
            if number is None:
                self.actions.exit_chat()
                return False
        self.send_initial_message(number, client)
        self.send_files(client)
        data = datetime.now()
        self.handle_delivery_status(number, connection, data, client)
        self.send_final_messages()
        self.actions.exit_chat()
        self.logger.info(LoggingMessages.FOR_THE_PHONE)
        return True

    def wppProcess(self, base_path: str) -> None | bool:
        self.read(base_path)
        clients = self.buildClients()
        if clients:
            connection = Connection()
            sleep(20)
            self.actions.start_whatsapp()
            sleep(20000000)
            try:
                for client in clients:
                    self.logger.info(LoggingMessages.CURRENT_CLIENT.format(uc=client.getUC))
                    match(client.getResponseMode):
                        case "T":
                            if not self.default_send_messages(connection, client=client):
                                self.logger.warning(LoggingMessages.FOR_THE_AGENCY)
                                self.option_send_Message(connection, client)
                        case "A":
                            self.option_send_Message(connection, client)
                            self.logger.warning(LoggingMessages.FOR_THE_AGENCY)
                        case "E":
                            self.logger.warning(LoggingMessages.FOR_THE_EMAIL)
                        case _:
                            raise Exception(ErrorsMessages.TYPE_RESPONSE_ERROR)
                sleep(20)
                return True
            except KeyboardInterrupt:
                self.logger.warning(ErrorsMessages.PROCESS_CANCELED)
                return None
        return False