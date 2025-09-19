from configparser import ConfigParser
from os.path import dirname, abspath, join
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR.parent.parent.parent / 'config.ini'

# Carrega configurações do arquivo config.ini
config = ConfigParser()
try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config.read_file(f)
except FileNotFoundError:
    raise RuntimeError(f"Arquivo {CONFIG_PATH} não encontrado.")
