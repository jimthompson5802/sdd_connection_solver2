"""
Minimal stub package for langchain_community used by tests.
This file exists only to satisfy imports in the test environment.
"""

from . import llms  # expose llms subpackage for tests

__all__ = ["llms"]
