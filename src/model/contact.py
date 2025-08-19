class Contact:
    _num1: int
    _num2: int

    def __init__(self, num1: int, num2: int) -> None:
        self._num1 = num1
        self._num2 = num2

    def getNum1(self) -> int:
        return self._num1

    def getNum2(self) -> int | None:
        if self._num2 != self._num1:
            return self._num2

    @staticmethod
    def format_tel(tel: str, sep: bool = False) -> str | int:
        '''
        <h3>Organiza a formatação dos números de telefone</h3>
        <p>Ex: xxxxxxxxxxx -> xx-x-xxxx-xxxx</p>
        '''
        tel = str(tel)
        if sep:
            return f"{tel[:2]}-{tel[2]}-{tel[3:7]}-{tel[-4:]}"if len(tel) > 10 else f"{tel[:2]}-9-{tel[3:7]}-{tel[-4:]}"
        else:
            sep_tel = list(tel)
            sep_tel.pop(2)
            new_tel = int("".join(sep_tel))
            return new_tel