class Contact:
    _num1: int
    _num2: int
    _used: int

    def __init__(self, num1: int, num2: int) -> None:
        self._num1 = num1
        self._num2 = num2

    @property
    def first_num(self) -> int:
        return self._num1

    @property
    def second_num(self) -> int | None:
        if self._num2 != self._num1:
            return self._num2

    @property
    def used(self) -> int:
        return self._used
    
    def set_used(self, used: int) -> None:
        self._used = used
    


    @staticmethod
    def format_tel(tel: int) -> str:
        '''
        <h3>Organiza a formatação dos números de telefone</h3>
        <p>Ex: xxxxxxxxxxx -> xx-x-xxxx-xxxx</p>
        '''
        tel_str = str(tel)
        return f"{tel_str[:2]}-{tel_str[2]}-{tel_str[3:7]}-{tel_str[-4:]}"if len(tel_str) > 10 else f"{tel_str[:2]}-9-{tel_str[3:7]}-{tel_str[-4:]}"
