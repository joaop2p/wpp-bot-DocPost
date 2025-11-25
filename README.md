# wpp-bot-DocPost-v2

Bot de WhatsApp Web para automação de envio de cartas e verificação de entrega. Ele orquestra rotinas para despachar mensagens/arquivos e checar status de entrega no WhatsApp Web, com configuração por arquivo INI/variáveis de ambiente e logs em pt-BR.

## Sumário
- Visão geral
- Requisitos
- Instalação
- Configuração (config.ini e variáveis de ambiente)
- Como executar
- Estrutura do projeto
- Testes
- Logs e observabilidade
- Segurança e privacidade
- Solução de problemas
- Próximos passos

## Visão geral
- Orquestrador: `App` (`lib/app/app.py`) coordena as rotinas.
- Rotinas principais:
  - `Despatch`: constrói clientes a partir de processos e envia mensagens/arquivos.
  - `CheckSentMessages`: verifica se mensagens pendentes foram entregues e atualiza o repositório/arquivos.
- Camadas de suporte: controls (regras/infra), dao (persistência/acesso a dados), models (domínio/DB), services e config.

## Requisitos
- Windows (desenvolvido e testado em Windows).
- Python 3.10+ (o código usa union types com `|`).
- Google Chrome/Chromium instalado (o driver do WhatsApp Web depende de um navegador compatível via `Actions`).
- Dependências Python (listagem a ser consolidada em `requirements.txt` ou `pyproject.toml`).

## Instalação
```powershell
# Clonar o projeto
cd C:\projetos
# (Se o diretório já existir, pule este passo)
# git clone <URL-do-repo> web-bot\wpp-bot-DocPost-v2

# Criar e ativar venv (PowerShell)
python -m venv .\.venv
.\.venv\Scripts\Activate.ps1

# Instalar dependências (quando o arquivo existir)
# pip install -r requirements.txt
# ou
# pip install -e .
```

## Configuração (config.ini e variáveis de ambiente)
A configuração pode vir de:
- `config.ini` na raiz do projeto;
- variáveis de ambiente (sobrescrevem o INI);
- valores padrão (DEFAULTS).

Exemplo mínimo de `config.ini` (ajuste caminhos para seu ambiente):
```ini
[app]
headless_mode = true

[path]
# Pasta de cache do driver do navegador
cache_driver_path = C:\\projetos\\web-bot\\wpp-bot-DocPost-v2\\cache
# Repositório de PDFs a enviar
repository_pdf = D:\\docs\\pdfs
# Pasta temporária usada em rotinas
repository_temp = D:\\docs\\temp
# Arquivos auxiliares de envio
guia = D:\\docs\\modelos\\guia.pdf
guia_rec = D:\\docs\\modelos\\guia_rec.pdf
```
Variáveis de ambiente com o mesmo nome (ex.: `APP__HEADLESS_MODE`, `PATH__REPOSITORY_PDF`) — quando suportado — têm precedência.

## Como executar
```powershell
# Na raiz do projeto
.\.venv\Scripts\Activate.ps1
python .\main.py
```
O fluxo padrão do `App.run()` é:
1. Configurar `Actions` com `headless_mode` e caminhos;
2. Executar rotinas em sequência: `Despatch` e `CheckSentMessages`;
3. Registrar logs e retornar um código de status (`STATUS`).

## Estrutura do projeto
```
config.ini
main.py
lib/
  app/app.py                 # Orquestrador da aplicação
  config/                    # CONFIG, DEFAULTS, constantes e settings
  src/
    controls/                # Regras/infra: file, ignore, package, post
    dao/                     # Repositórios de dados
    data/                    # Fontes de dados auxiliares
    models/
      db/                    # Modelos persistidos
      domain/                # Entidades e objetos de domínio
      interfaces/            # Interfaces (ex.: Routine)
    routines/
      despatch.py            # Envio de mensagens/arquivos
      check_sent_messages.py # Verificação de entregas
    services/                # Serviços auxiliares
repository/                  # Artefatos do domínio (ex.: saídas/estado)
tests/                       # Testes automatizados (pytest)
```

## Testes
- Framework: `pytest`.
- Para executar:
```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```
- Dicas:
  - Use mocks para `packages.web.advanced.actions.Actions` (evitar abrir navegador nos testes).
  - Cubra lógica de construção de clientes, envio (_send_message) e políticas de espera (wait_until/timeout).

## Logs e observabilidade
- Logs em pt-BR com placeholders: `logger.info("Mensagem: %s", valor)`.
- O `App` e as rotinas (`Despatch`, `CheckSentMessages`) emitem logs de início/fim e eventos-chave.
- Para aumentar verbosidade, configure `logging.basicConfig(level=logging.DEBUG)` no bootstrap, se necessário.

## Segurança e privacidade
- Não registre dados sensíveis em logs (números completos de telefone, QR, tokens, caminhos internos sensíveis).
- Armazene segredos via variáveis de ambiente.
- Restrinja permissões do diretório de cache do navegador.
- Mantenha dependências atualizadas e confiáveis.

## Solução de problemas
- WhatsApp Web não inicia: verifique instalação/compatibilidade do navegador e `cache_driver_path`.
- Mensagens não entregues: confirme busca pelo número (`search`), aguarde confirmação (`delivered`) e revise tempo de timeout.
- Caminhos inválidos: revise `config.ini` ([path]) e permissões do Windows.
- Módulo `packages` ausente: confirme a presença do pacote interno `packages` (ou submódulo) exigido por `packages.web.advanced.actions` e `packages.files`.

## Próximos passos
- Publicar `requirements.txt`/`pyproject.toml` com versões mínimas suportadas.
- Adicionar CI (lint, type-check e testes) e hooks `pre-commit` (ruff, black, mypy).
- Aumentar cobertura de testes das rotinas e controles.
- Documentar todas as opções de configuração suportadas em `lib/config`.
