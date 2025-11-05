import logging
from lib.config import STATUS
from lib.src.models.interfaces.routines import Routine
from lib.src.routines.check_sent_messages import CheckSentMessages
from ..src.routines.despatch import Despatch
from mytools.PyZapp.advanced.actions_v2 import ActionsConfig

# from mytools.web.advanced.actions import Actions
from ..config import CONFIG, DEFAULTS

class App:
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
    

    def _config_actions(self) -> ActionsConfig:
        config: ActionsConfig = ActionsConfig(headless=CONFIG.headless_mode, driver_path=CONFIG.path.cache_driver_path, cache_path=CONFIG.path.repository_pdf)
        return config

    def run(self) -> STATUS | STATUS:
        self.logger.info(f'Aplicação iniciada, versão: {DEFAULTS.VERSION}')
        config = self._config_actions()
        routines: list[Routine] = [
            Despatch(config),
            CheckSentMessages(config)
        ]
        code = STATUS.SUCCESS
        for routine in routines:
                self.logger.info(f'Iniciando rotina: {routine.__class__.__name__}')
                try:
                    routine.run()
                except Exception as e:
                    self.logger.error(f"Erro ao executar a rotina: {e}")
                    self.logger.error("Detalhes do erro:", exc_info=True)
                    code = STATUS.GENERIC_ERROR
                    break
                except KeyboardInterrupt:
                    self.logger.info("Processo interrompido pelo usuário.")
                    code = STATUS.INTERRUPTED
                    break
        self.logger.info(f"Aplicação finalizada. code: {code}")
        return code