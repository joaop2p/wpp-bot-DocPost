import logging
# from mytools.web.advanced.actions import Actions
from mytools.PyZapp.advanced.actions_v2 import Actions, ActionsConfig
from lib.config import CONFIG
from lib.src.controls.file_control import FileControl
from lib.src.controls.package_control import PackageControl
from lib.src.models.interfaces.routines import Routine
from lib.src.utils.generic import ExceptionsMessages
from mytools.structs.files import ProcessesList

class CheckSentMessages(Routine):
    def __init__(self, config: ActionsConfig) -> None:
        self.config = config
        self.file_control = FileControl()
        self._logger = logging.getLogger(self.__class__.__name__)

    def _check_message_delivered(self, action: Actions, num_used: int, num_process: int, file_name: str) -> bool:
        self._logger.info(ExceptionsMessages.VERIFICANDO_MENSAGEM_ENTREGUE, num_process)
        if not action.wpp_started:
            action.start_whatsapp()
        action.search(num_used)
        result = action.delivered()
        if result:
            action.safe_search(num_process, False)
            action.print_page(num_process)
            self.file_control.move_to_ready(path=file_name)
            self._logger.info(ExceptionsMessages.MENSAGEM_ENTREGUE_SUCESSO)
        else:
            self._logger.info(ExceptionsMessages.MENSAGEM_NAO_ENTREGUE)
        action.close_chat()
        return result

    def run(self) -> None:
        package_control = PackageControl()
        pending = package_control.fetch_pending_package()
        process_list = ProcessesList.from_directory(CONFIG.path.repository_temp)
        if not pending:
            self._logger.info(ExceptionsMessages.NENHUM_PACOTE_PENDENTE)
            return
        with Actions(self.config) as actions:
            for item in pending:
                process = process_list.find_process(item.process_id)
                if process and process.files:
                    if self._check_message_delivered(actions, item.num_used, item.process_id, process.files[0].directory):
                        item.delivered = True
                        package_control.insert_package(item)
        self._logger.info(ExceptionsMessages.ROTINA_FINALIZADA)