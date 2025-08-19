import logging
import sys
import traceback
from .actions import Actions, AppConfig
from .launcher import Launcher, datetime
from .search import Search
from .config.logging.log_setup import Log
from .config.templates.logging_messages import LoggingMessages
from .config.templates.error_messages import ErrorsMessages

class WhatsAppBot():
    def __init__(self) -> None:
        Log.setup()
        self.logger = logging.getLogger(self.__str__())
        self.action = Actions()
        self.logger.info(LoggingMessages.WELCOME_LOG.format(
            version=AppConfig.VERSION,
            date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        ))

    def __str__(self) -> str:
        return AppConfig.TITLE

    def run(self) -> None:
        '''       
        :param self: Instância atual da classe WhatsAppBot.
        :type self: WhatsAppBot
        :return: None
        :rtype: None
        :raises: None
        <h3>Inicia o bot do WhatsApp</h3>
        <p>Este método configura o logger, inicializa o WhatsApp e executa o processo de envio de mensagens.</p>
        <p>Utiliza a classe Actions para gerenciar as ações do bot e a classe Launcher para iniciar o processo de envio.</p>
        <p>Em caso de erro, registra a exceção e encerra o programa com um código de erro apropriado.</p> 
        '''
        
        launcher = Launcher(self.action)
        search = Search(self.action)
        code = AppConfig.SUCCESS_CODE
        try:
            operation = launcher.wppProcess(AppConfig.DATA_FILE)
            if operation is not None:
                if operation is False:
                    self.action.start_whatsapp()
                search.wpp_search()
        except Exception as e:
            self.logger.critical(ErrorsMessages.ERROR_LOG.format(error_message=str(e), error_details=traceback.format_exc()))
            code = AppConfig.GENERIC_ERROR_CODE
        finally:
            self.logger.info(LoggingMessages.EXIT.format(code=code))
            sys.exit(code)

