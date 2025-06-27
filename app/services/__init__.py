"""
Services package for business logic and domain operations.

This package contains service classes that encapsulate business logic,
coordinate between different parts of the application, and provide
a clean API for the API layer to interact with the domain model.
"""

from .link_service import LinkService

__all__ = [
    'LinkService',
]
