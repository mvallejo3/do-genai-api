"""
Middleware package for authentication and response handling.
"""

from .auth import require_auth
from .decorators import handle_response

__all__ = ['require_auth', 'handle_response']

