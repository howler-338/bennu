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


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL", "postgresql://bennu:bennu@localhost:5432/bennu_test"
    )


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
