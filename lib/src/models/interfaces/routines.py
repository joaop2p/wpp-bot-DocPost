from abc import ABC, abstractmethod
from mytools.web.advanced.actions import Actions

class Routine(ABC):
    @abstractmethod
    def __init__(self, actions: Actions) -> None:
        pass

    @abstractmethod
    def run(self) -> None:
        pass