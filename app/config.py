"""Config."""

from dotenv import dotenv_values
from functools import lru_cache

DOTENV_FILE = "/hide/.env"


class Config:
    """Config dataclass."""

    LOG_LEVEL: str
    LOG_FORMAT: str
    LOG_FILENAME: str
    LOG_FILESIZE: int
    LOG_FILES_LIMIT: int

    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DATABASE: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_EXPIRE: int
    REDIS_DECODE: bool

    APP_NAME: str
    APP_PATH: str
    APP_URL: str
    APP_PREFIX: str
    APP_HASH_SALT: str
    APP_FERNET_KEY: bytes
    APP_JWT_SECRET: str
    APP_JWT_ALGORITHM: str

    MFA_ABSOLUTE_PATH: str
    MFA_RELATIVE_URL: str
    MFA_NAME: str
    MFA_EXTENSION: str
    MFA_VERSION: int
    MFA_SIZE: int
    MFA_BORDER: int
    MFA_FIT: str
    MFA_COLOR: str
    MFA_BACKGROUND: str


@lru_cache
def get_cfg() -> dict:
    """Create config object from dotenv file."""
    cfg_values = dotenv_values(DOTENV_FILE)
    cfg = Config()

    for key in cfg_values:
        value = cfg_values[key]

        if Config.__annotations__[key] == str:
            setattr(cfg, key, value)

        elif Config.__annotations__[key] == int:
            setattr(cfg, key, int(value))

        elif Config.__annotations__[key] == bytes:
            setattr(cfg, key, bytes(value, "utf-8"))

        elif Config.__annotations__[key] == bool:
            setattr(cfg, key, True if value.lower() == "true" else False)

        else:
            setattr(cfg, key, None)

    return cfg
