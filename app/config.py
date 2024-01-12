import os

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status


class DatabaseConfig:
    # DB_NAME = os.getenv('DB_NAME', "call_system")
    # DB_PASSWORD = os.getenv('DB_PASSWORD', "WFpnJMjtPKbwpNaBZQuewNBuCGYQWMyD")
    # DB_HOST = os.getenv('DB_HOST', "65.109.25.177")
    # DB_PORT = os.getenv('DB_PORT', "5432")
    # DB_USER = os.getenv('DB_USER', "uhead")
    # DB_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    DB_NAME = os.getenv('DB_NAME', "call_system")
    DB_PASSWORD = os.getenv('DB_PASSWORD', "WFpnJMjtPKbwpNaBZQuewNBuCGYQWMyD")
    DB_HOST = os.getenv('DB_HOST', "65.109.25.177")
    DB_PORT = os.getenv('DB_PORT', "5432")
    DB_USER = os.getenv('DB_USER', "uhead")
    DB_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


class ADatabaseConfig(DatabaseConfig):
    # DB_NAME = os.getenv('DB_NAME', "call_system")
    # DB_PASSWORD = os.getenv('DB_PASSWORD', "WFpnJMjtPKbwpNaBZQuewNBuCGYQWMyD")
    # DB_HOST = os.getenv('DB_HOST', "65.109.25.177")
    # DB_PORT = os.getenv('DB_PORT', "5432")
    # DB_USER = os.getenv('DB_USER', "uhead")

    DB_NAME = os.getenv('DB_NAME', "call_system")
    DB_PASSWORD = os.getenv('DB_PASSWORD', "WFpnJMjtPKbwpNaBZQuewNBuCGYQWMyD")
    DB_HOST = os.getenv('DB_HOST', "65.109.25.177")
    DB_PORT = os.getenv('DB_PORT', "5432")
    DB_USER = os.getenv('DB_USER', "uhead")

    pg_driver = 'asyncpg'
    DB_URL = f'postgresql+{pg_driver}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


class APIConfig:
    API_PREFIX = os.getenv('API_PREFIX', '/api')

    API_HOST = os.getenv('API_HOST', '127.0.0.1')
    API_PORT = os.getenv('API_PORT', 8002)
    API_PORT_RESERVE = os.getenv('API_PORT_RESERVE', 8002)
    RESERVE = os.getenv('RESERVE', False)

    API_DOCS_URL = API_PREFIX + '/docs'
    API_OPENAPI_URL = API_PREFIX + '/openapi.json'


class ACSConfig:
    LOGS_PATH = os.getenv('ACS_LOGS_PATH', 'logs')


class TokenConfig:
    SECRET_KEY = "901ddf58c769396569689a12d3ec13f998f4ff7ebec80089a99f01ee738e7c2b"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 10080
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{APIConfig.API_PREFIX}/auth/api", auto_error=False)#OAuth2PasswordBearerCookie(tokenUrl=f"{APIConfig.API_PREFIX}/users/api", auto_error=False)
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}, )


class AsteriskConfig:
    API_KEY = "asterisk:djifndjifidfdoe3921"
    ARI_URL = "http://webrtc4.getret.ru:8088/ari/"
    SERVER = "webrtc4.getret.ru"
    AMI_USERNAME = "admin"
    AMI_PASSWORD = "ksjfidjfnsi234"
    AMI_PORT = 5038
    APP_NAME = os.getenv('APP_NAME', 'ACS_PROD')


class AcsConfig:
    PORT = os.getenv('ACS_PORT', '1234')
    SENTRY_URL = os.getenv('ACS_SENTRY_URL', 'https://8d4b0346915906c952dff3ec2cdc038e@o4505634273099776.ingest.sentry.io/4506235096072192')


class AsteriskDatabaseConfig:
    DB_NAME = "asterisk_db"
    DB_NAME_PG = "postgres"
    DB_USER = "asterisk"
    DB_PASSWORD = "Qwerty123"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    DB_URL_POSTGRES = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME_PG}"


CORS_MIDDLEWARES_OPTIONS = {
    'allow_origins': ['*'],
    # 'allow_origin_regex': ['*'],
    'allow_credentials': True,
    'allow_methods': ['*'],
    'allow_headers': ['*'],
}