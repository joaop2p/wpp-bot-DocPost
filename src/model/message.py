
from typing import Literal, LiteralString

class Message:
    _message: str
    _message_type: str

    def __init__(self, message_type: str) -> None:
        self._message = Message.get_initial_message(message_type)
        self._message_type = message_type

    @staticmethod
    def get_ag_message() -> str:
        return "Prezado (a) Cliente, Sr. (a) {nome_cliente}, deseja receber todas as Cartas referente ao processo de ressarcimento {processo} através do WhatsApp número {telefone}? *Apenas SIM ou NÃO*"

    @staticmethod
    def get_final_messages() -> tuple[LiteralString, LiteralString, Literal['A Energisa agradece seu contato.']]:
        return (
        "Este WhatsApp é exclusivo para o envio de cartas. Por favor, *não responda a esta mensagem, não envie documentações, e não realizamos atendimentos por ligações ou videochamadas*. Certifique-se de seguir as instruções de envio mencionadas acima",
        "Seu atendimento foi encerrado, qualquer informação entrar em contato com o 0800-083-0196, Chame a Gisa pelo chat, gisa.energisa.com.br, ou agência de atendimento.",
        "A Energisa agradece seu contato."
    )

    @staticmethod
    def get_initial_message(type: str) -> str:
        match(type):
            case 'request':
                return "Prezado (a) Cliente, conforme solicitado por V.S.ª que documentos referentes ao processo SR_{processo} fossem enviados através do WhatsApp {telefone}, estamos encaminhando solicitação de documentos necessários para análise/documentação complementar e orientação de envio dos documentos requeridos."
            case 'request+':
                return "Prezado (a) consumidor (a). Analisamos a documentação entregue acerca do seu pedido de ressarcimento, para dar andamento a sua solicitação, se faz necessário a entrega do (s) equipamento (s) ou peça (s) solicitado (s) na carta em anexo e Orientação do envio da Carta do Recolhimento referente ao processo {processo}"
            case 'response':
                return "Prezado (a) Cliente, conforme solicitado por V.S.ª que documentos referentes ao processo SR_{processo} fossem enviados através do WhatsApp {telefone}, estamos encaminhando Carta Resposta. No caso de discordância deste parecer, V.S.ª poderá formular recurso na Ouvidoria da ENERGISA-PB, pelo telefone (83) 2106-7277), e-mail: ouvidoria-pb@energisa.com.br."
            case _:
                raise Exception()
                # TODO Implementar exceção personalizada

    @property
    def getMessage_text(self) -> str:
        return self._message
    @property
    def getMessage_type(self) -> str:
        return self._message_type