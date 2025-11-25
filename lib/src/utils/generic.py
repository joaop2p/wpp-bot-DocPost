from enum import Enum


class ResponseType(Enum):
    STANDARD = "T"
    AGENCY = "A"
    EMAIL = "E"

class ResponseMode(Enum):
    RESPONSE = "response"
    REQUEST = "request"
    REQUEST_PLUS = "request+"

class ExceptionsMessages:
    """Centralized exception and log messages for the application."""
    
    # Wait and delivery messages
    ERRO_WAIT_UNTIL = "Erro durante wait_until: %s"
    ENTREGA_CONFIRMADA = "Entrega confirmada dentro do timeout."
    ENTREGA_NAO_CONFIRMADA = "Entrega não confirmada dentro do timeout de %.1fs."
    MENSAGEM_ENTREGUE_SUCESSO = "Mensagem entregue com sucesso."
    MENSAGEM_ENVIADA_NAO_ENTREGUE = "Mensagem enviada mas não entregue."
    
    # Client building messages
    CLIENTE_INCOMPLETO = "Cliente incompleto: %s"
    ERRO_CONSTRUIR_CLIENTE = "Erro ao construir cliente: %s"
    
    # Client handling messages
    CLIENTE_RECEBE_EMAIL = "Cliente deve receber a carta via E-mail."
    CLIENTE_NA_IGNORE_LIST = "Cliente está na lista de ignore, pulando envio de mensagem."
    NAO_POSSIVEL_INICIAR_CHAT = "Não foi possível iniciar o chat para o cliente: %s"
    NUMERO_SELECIONADO = "Número selecionado: %d"
    MODO_RESPOSTA_DESCONHECIDO = "Modo de resposta desconhecido para o cliente: %s"
    
    # Send message errors
    ERRO_ENVIAR_MENSAGEM = "Erro ao enviar mensagem para o cliente %s: %s"
    TRACEBACK = "Traceback: %s"
    
    # Processing messages
    CLIENTE_ATUAL = "Cliente atual: %s"
    ENVIO_NAO_REALIZADO = "Envio não realizado para o cliente: %s"
    MODO_ENVIO_INVALIDO = "Modo de envio inválido para o cliente: %s"
    
    # Post messages
    CARTA_JA_ENVIADA = "Carta já enviada anteriormente para o cliente: %s"
    ATUALIZANDO_NOME_ARQUIVO = "Atualizando nome do arquivo no post: %s"
    CRIANDO_NOVO_POST = "Criando novo post para o cliente: %s"
    POST_REGISTRADO_SUCESSO = "Post registrado com sucesso: %s"
    MENSAGEM_PROCESSADA = "Mensagem processada para o cliente: %s"
    ERRO_PROCESSAR_POS_ENVIO = "Erro ao processar pós-envio para o cliente %s: %s"
    
    # Routine lifecycle messages
    INICIANDO_ROTINA_DESPACHO = "Iniciando rotina de despacho de mensagens..."
    PROCESSOS_ENCONTRADOS = "Processos encontrados: %s"
    DADOS_CARREGADOS = "Dados carregados."
    CONSTRUINDO_PACOTES = "Construindo pacotes de envio."
    NENHUM_PACOTE_ENVIAR = "Nenhum pacote para enviar."
    PACOTES_CONSTRUIDOS_SUCESSO = "Pacotes construídos com sucesso. Total de pacotes: %d"
    INICIANDO_ENVIO_MENSAGENS = "Iniciando envio de mensagens via WhatsApp Web."
    ROTINA_DESPACHO_FINALIZADA = "Rotina de despacho de mensagens finalizada."
    
    # CheckSentMessages messages
    VERIFICANDO_MENSAGEM_ENTREGUE = "Verificando se a mensagem do processo %d foi entregue..."
    MENSAGEM_NAO_ENTREGUE = "Mensagem não entregue."
    NENHUM_PACOTE_PENDENTE = "Nenhum pacote pendente encontrado."
    ROTINA_FINALIZADA = "Rotina finalizada."
