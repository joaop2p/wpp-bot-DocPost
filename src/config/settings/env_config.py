from os import getenv
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Variáveis de ambiente com valores padrão
LOG_PATH = getenv('LOG', './')
DATABASE_PATH = getenv('DATA_BASE', 'database.sqlite')
