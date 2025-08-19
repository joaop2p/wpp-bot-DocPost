from configparser import ConfigParser

# Carrega configurações do arquivo config.ini
config = ConfigParser()
try:
    with open('config.ini', 'r', encoding='utf-8') as f:
        config.read_file(f)
except FileNotFoundError:
    raise RuntimeError("Arquivo config.ini não encontrado.")
