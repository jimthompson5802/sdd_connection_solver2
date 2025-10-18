"""
Lightweight shim for pydantic components used by the project tests.
This is intentionally minimal and only implements the small surface area the code imports.
Do NOT use this as a replacement for real pydantic in production.
"""

from typing import Any, Callable


class ValidationError(Exception):
    pass


def field_validator(*args, **kwargs):
    def decorator(func: Callable):
        return func

    return decorator


def validator(*args, **kwargs):
    def decorator(func: Callable):
        return func

    return decorator


class Field:
    def __init__(self, *args, **kwargs):
        pass


class BaseModel:
    def __init__(self, **data: Any):
        for k, v in data.items():
            setattr(self, k, v)

    def dict(self):
        return self.__dict__

    class Config:
        pass
