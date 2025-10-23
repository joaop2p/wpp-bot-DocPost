import logging
from lib.config import STATUS
from lib.src.models.interfaces.routines import Routine
from lib.src.routines.check_sent_messages import CheckSentMessages
from ..src.routines.despatch import Despatch
from packages.web.advanced.actions import Actions
from ..config import CONFIG, DEFAULTS

class App:
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.actions = Actions()

    def _config_actions(self) -> None:
        self.actions.set_driver_config(CONFIG.headless_mode, CONFIG.path.cache_driver_path)
        self.actions.set_path_config(CONFIG.path.repository_pdf)

    def run(self) -> STATUS | STATUS:
        self.logger.info(f'Aplicação iniciada, versão: {DEFAULTS.VERSION}')
        self._config_actions()
        routines: list[Routine] = [
            Despatch(self.actions),
            CheckSentMessages(self.actions)
        ]
        code = STATUS.SUCCESS
        for routine in routines:
                self.logger.info(f'Iniciando rotina: {routine.__class__.__name__}')
                try:
                    routine.run()
                except Exception as e:
                    self.logger.error(f"Erro ao executar a rotina: {e}")
                    code = STATUS.GENERIC_ERROR
                    break
                except KeyboardInterrupt:
                    self.logger.info("Processo interrompido pelo usuário.")
                    code = STATUS.INTERRUPTED
                    break
        self.logger.info(f"Aplicação finalizada. code: {code}")
        return code