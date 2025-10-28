import logging
from mytools.web.advanced.actions import Actions
from lib.config import CONFIG
from lib.src.controls.file_control import FileControl
from lib.src.controls.package_control import PackageControl
from lib.src.models.interfaces.routines import Routine
from mytools.structs.files import ProcessesList

class CheckSentMessages(Routine):
    def __init__(self, actions: Actions) -> None:
        self.actions = actions
        self.file_control = FileControl()
        self._logger = logging.getLogger(self.__class__.__name__)

    def _check_message_delivered(self, num_used: int, num_process: int, file_name: str) -> bool:
        self._logger.info(f'Verificando se a mensagem do processo {num_process} foi entregue...')
        if not self.actions.wpp_started:
            self.actions.start_whatsapp()
        self.actions.search(num_used)
        result = self.actions.delivered()
        if result:
            self.actions.safe_search(num_process, False)
            self.actions.print_page(num_process)
            self.file_control.move_to_ready(path=file_name)
            self._logger.info('Mensagem entregue com sucesso.')
        else:
            self._logger.info('Mensagem não entregue.')
        self.actions.exit_chat_from_search()
        return result

    def run(self) -> None:
        package_control = PackageControl()
        pending = package_control.fetch_pending_package()
        process_list = ProcessesList.from_directory(CONFIG.path.repository_temp)
        if not pending:
            self._logger.info('Nenhum pacote pendente encontrado.')
            return
        for item in pending:
            process = process_list.find_process(item.process_id)
            if process and process.files:
                if self._check_message_delivered(item.num_used, item.process_id, process.files[0].directory):
                    item.delivered = True
                    package_control.insert_package(item)
        self._logger.info('Rotina finalizada.')