"""
SEAL-Python: Python bindings for Microsoft SEAL Homomorphic Encryption Library

This package provides Python bindings for the Microsoft SEAL library,
enabling homomorphic encryption operations in Python with support for
CKKS, BFV, and BGV encryption schemes.
"""

__version__ = "4.1.5"
__author__ = "Chandradutt Patel"

# Security warning
SECURITY_WARNING = """
!!! SECURITY WARNING !!!
Handle cryptographic keys with extreme care.
Never log or transmit secret keys in plain text.
"""

# Import the compiled extension
try:
    from .seal import *
    SEAL_LOADED = True
except ImportError as e:
    SEAL_LOADED = False
    raise ImportError(
        f"Failed to import SEAL extension: {e}. Please build the extension first."
    ) from e

# Import high-level utilities
from .utils import (
    CKKSHelper,
    BFVHelper,
    create_ckks_params,
    create_bfv_params,
    serialize_to_bytes,
    deserialize_from_bytes,
)

__all__ = [
    'CKKSHelper',
    'BFVHelper',
    'create_ckks_params',
    'create_bfv_params',
    'serialize_to_bytes',
    'deserialize_from_bytes',
    'show_security_warning',
    '__version__',
]


def show_security_warning():
    """Display the package security warning on demand."""
    print(f"SEAL-Python {__version__} loaded successfully")
    print(SECURITY_WARNING)