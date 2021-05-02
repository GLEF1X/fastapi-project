import pathlib
import typing

from environs import Env

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
ENV_PATH = str(BASE_DIR / '.env')

# Получает все файлы по паттерну в определенной директории
# print([file for file in Path.cwd().rglob('*.py')])
# Создает папку
# print(Path.mkdir(BASE_DIR / 'data' / 'my_lib'))

# print((BASE_DIR / 'data' / "config2.py").rename("config.py"))

env = Env()
env.read_env(ENV_PATH)

# PostgreSQL db config
DB_USER: typing.Optional[str] = env.str('DB_USER')
DB_PASS: typing.Optional[str] = env.str("DB_PASS")
DB_HOST: typing.Optional[str] = env.str("DB_HOST")
DB_NAME: typing.Optional[str] = env.str("DB_NAME")

# FastApi config
APP_NAME: typing.Optional[str] = env.str("APP_NAME")
API_VERSION: typing.Optional[str] = env.str("API_VERSION")
DOCS_URL: typing.Optional[str] = env.str("DOCS_URL")
REDOC_URL: typing.Optional[str] = env.str("REDOC_URL")
OPEN_API_ROOT: typing.Optional[str] = env.str("DEFAULT_OPEN_API_ROOT")

IS_PRODUCTION: typing.Optional[bool] = env.bool("IS_PRODUCTION")

TEMPLATES_DIR = str(BASE_DIR / "templates")

__all__ = (
    'BASE_DIR',
    'TEMPLATES_DIR',
    # database env variables
    'DB_USER',
    'DB_NAME',
    'DB_HOST',
    'DB_PASS',
    # FastApi variables
    'APP_NAME',
    'API_VERSION',
    'DOCS_URL',
    'REDOC_URL',
    # Special variables
    'IS_PRODUCTION'
)
