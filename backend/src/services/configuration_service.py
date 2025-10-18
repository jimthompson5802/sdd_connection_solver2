"""
Compatibility alias module.
Re-export ConfigurationService from config_service to satisfy older imports in tests.
"""

from .config_service import ConfigurationService

__all__ = ["ConfigurationService"]
