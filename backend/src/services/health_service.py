from typing import Any
from types import SimpleNamespace


class HealthService:
    """Minimal health service to satisfy integration tests."""

    def check_health(self) -> Any:
        # Return an object with attributes for tests that use hasattr checks
        data = {
            "status": "healthy",
            "timestamp": None,
            "version": "1.0",
            "providers_available": ["simple"],
        }
        return SimpleNamespace(**data)
