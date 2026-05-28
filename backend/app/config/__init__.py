"""Application configuration."""

import os
from typing import Type

from app.config.settings import Config, DevelopmentConfig, ProductionConfig, TestingConfig

_config_map: dict[str, Type[Config]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(name: str | None = None) -> Type[Config]:
    """Resolve config class from FLASK_ENV or explicit name."""
    env = name or os.getenv("FLASK_ENV", "development")
    return _config_map.get(env, DevelopmentConfig)
