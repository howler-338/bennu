import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key")
    DEBUG = False
    TESTING = False

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://bennu:bennu@localhost:5432/bennu"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.path.dirname(__file__), "../../uploads"))
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

    FRONTEND_DIST = os.getenv(
        "FRONTEND_DIST",
        os.path.join(os.path.dirname(__file__), "../../../frontend/dist"),
    )

    CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
    CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.2:3b")

    RATELIMIT_STORAGE_URI = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    RATELIMIT_HEADERS_ENABLED = True

    API_TITLE = "Bennu API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL", "postgresql://bennu:bennu@postgres:5432/bennu_test"
    )
    CELERY_BROKER_URL = "memory://"
    CELERY_RESULT_BACKEND = "cache+memory://"
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    pass


_configs = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env: str = None):
    env = env or os.getenv("FLASK_ENV", "development")
    return _configs.get(env, DevelopmentConfig)
