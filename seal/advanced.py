"""
Advanced features and utilities for SEAL-Python.

This module provides advanced functionality for real-world homomorphic encryption applications,
including batch processing, context managers, performance monitoring, and common computation patterns.
"""
from typing import List, Optional, Union, Tuple, Callable, Any
import numpy as np
import time
import functools
from contextlib import contextmanager


try:
    from . import seal as seal_module
    from .utils import _has_required_seal_api
    if not _has_required_seal_api(seal_module):
        raise AttributeError("SEAL extension module is missing required attributes")
    seal = seal_module
    SEAL_AVAILABLE = True
except (ImportError, AttributeError):
    SEAL_AVAILABLE = False


__all__ = [
    'SEALContext',
    'BatchProcessor',
    'PerformanceMonitor',
    'KeyManager',
    'polynomial_evaluation',
    'matrix_vector_multiply',
    'dot_product',
    'measure_performance',
]


class SEALContextManager:
    """
    Context manager for SEAL operations with automatic resource cleanup.

    Example:
        >>> with SEALContextManager(poly_modulus_degree=8192) as ctx:
        ...     encrypted = ctx.encrypt(3.14)
        ...     result = ctx.decrypt(encrypted)
    """

    def __init__(self, scheme='ckks', poly_modulus_degree=8192, **kwargs):
        if not SEAL_AVAILABLE:
            raise ImportError("SEAL extension not available")

        self.scheme = scheme
        self.poly_modulus_degree = poly_modulus_degree
        self.kwargs = kwargs
        self.helper = None

    def __enter__(self):
        if self.scheme == 'ckks':
            from .utils import CKKSHelper
            self.helper = CKKSHelper(self.poly_modulus_degree, **self.kwargs)
        elif self.scheme == 'bfv':
            from .utils import BFVHelper
            self.helper = BFVHelper(self.poly_modulus_degree, **self.kwargs)
        else:
            raise ValueError(f"Unknown scheme: {self.scheme}")
        return self.helper

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup if needed
        if self.helper and hasattr(self.helper, '_ciphertext_metadata'):
            self.helper._ciphertext_metadata.clear()
        return False


class BatchProcessor:
    """
    Efficient batch processing for multiple ciphertexts.

    Example:
        >>> helper = CKKSHelper()
        >>> processor = BatchProcessor(helper)
        >>> encrypted_batch = processor.encrypt_batch([1.0, 2.0, 3.0, 4.0, 5.0])
        >>> results = processor.decrypt_batch(encrypted_batch)
    """

    def __init__(self, helper):
        """
        Initialize batch processor with a SEAL helper instance.

        Args:
            helper: CKKSHelper or BFVHelper instance
        """
        self.helper = helper

    def encrypt_batch(self, values: List[Union[float, int]]) -> List:
        """
        Encrypt a batch of values in parallel.

        Args:
            values: List of values to encrypt

        Returns:
            List of encrypted ciphertexts
        """
        return [self.helper.encrypt(v) for v in values]

    def decrypt_batch(self, ciphertexts: List) -> List[Union[float, int]]:
        """
        Decrypt a batch of ciphertexts.

        Args:
            ciphertexts: List of ciphertexts to decrypt

        Returns:
            List of decrypted values
        """
        return [self.helper.decrypt(ct) for ct in ciphertexts]

    def add_batch(self, batch1: List, batch2: List) -> List:
        """
        Element-wise addition of two batches of ciphertexts.

        Args:
            batch1: First batch of ciphertexts
            batch2: Second batch of ciphertexts

        Returns:
            List of summed ciphertexts
        """
        if len(batch1) != len(batch2):
            raise ValueError("Batches must have same length")
        return [self.helper.add(ct1, ct2) for ct1, ct2 in zip(batch1, batch2)]

    def multiply_batch(self, batch1: List, batch2: List) -> List:
        """
        Element-wise multiplication of two batches of ciphertexts.

        Args:
            batch1: First batch of ciphertexts
            batch2: Second batch of ciphertexts

        Returns:
            List of multiplied ciphertexts
        """
        if len(batch1) != len(batch2):
            raise ValueError("Batches must have same length")
        return [self.helper.multiply(ct1, ct2) for ct1, ct2 in zip(batch1, batch2)]


class PerformanceMonitor:
    """
    Monitor performance of homomorphic encryption operations.

    Example:
        >>> monitor = PerformanceMonitor()
        >>> with monitor.measure("encryption"):
        ...     encrypted = helper.encrypt(3.14)
        >>> print(monitor.get_stats())
    """

    def __init__(self):
        self.stats = {}

    @contextmanager
    def measure(self, operation_name: str):
        """
        Context manager to measure operation time.

        Args:
            operation_name: Name of the operation being measured
        """
        start_time = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start_time
            if operation_name not in self.stats:
                self.stats[operation_name] = []
            self.stats[operation_name].append(elapsed)

    def get_stats(self, operation_name: Optional[str] = None) -> dict:
        """
        Get performance statistics.

        Args:
            operation_name: Specific operation to get stats for, or None for all

        Returns:
            Dictionary with min/max/avg/total times
        """
        if operation_name:
            times = self.stats.get(operation_name, [])
            if not times:
                return {}
            return {
                'operation': operation_name,
                'count': len(times),
                'total': sum(times),
                'avg': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
            }

        return {
            op: {
                'count': len(times),
                'total': sum(times),
                'avg': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
            }
            for op, times in self.stats.items()
        }

    def reset(self):
        """Clear all statistics."""
        self.stats.clear()


class KeyManager:
    """
    Manage and serialize encryption keys.

    Example:
        >>> helper = CKKSHelper()
        >>> manager = KeyManager(helper)
        >>> manager.save_keys("keys/")
        >>> # Later...
        >>> manager.load_keys("keys/")
    """

    def __init__(self, helper):
        """
        Initialize key manager with a SEAL helper instance.

        Args:
            helper: CKKSHelper or BFVHelper instance
        """
        self.helper = helper

    def save_keys(self, directory: str):
        """
        Save all keys to a directory.

        Args:
            directory: Directory path to save keys
        """
        import os
        os.makedirs(directory, exist_ok=True)

        from .utils import serialize_to_bytes

        # Save public key
        with open(os.path.join(directory, 'public_key.bin'), 'wb') as f:
            f.write(serialize_to_bytes(self.helper.public_key))

        # Save secret key
        with open(os.path.join(directory, 'secret_key.bin'), 'wb') as f:
            f.write(serialize_to_bytes(self.helper.secret_key))

        # Save relinearization keys
        with open(os.path.join(directory, 'relin_keys.bin'), 'wb') as f:
            f.write(serialize_to_bytes(self.helper.relin_keys))

    def load_keys(self, directory: str):
        """
        Load keys from a directory.

        Args:
            directory: Directory path containing saved keys
        """
        import os
        from .utils import deserialize_from_bytes

        # Load public key
        with open(os.path.join(directory, 'public_key.bin'), 'rb') as f:
            self.helper.public_key = deserialize_from_bytes(f.read(), seal.PublicKey)

        # Load secret key
        with open(os.path.join(directory, 'secret_key.bin'), 'rb') as f:
            self.helper.secret_key = deserialize_from_bytes(f.read(), seal.SecretKey)

        # Load relinearization keys
        with open(os.path.join(directory, 'relin_keys.bin'), 'rb') as f:
            self.helper.relin_keys = deserialize_from_bytes(f.read(), seal.RelinKeys)


def polynomial_evaluation(helper, coefficients: List[float], encrypted_x) -> 'seal.Ciphertext':
    """
    Evaluate a polynomial on encrypted data using Horner's method.

    f(x) = a_n * x^n + a_(n-1) * x^(n-1) + ... + a_1 * x + a_0

    Args:
        helper: CKKSHelper instance
        coefficients: Polynomial coefficients [a_0, a_1, ..., a_n]
        encrypted_x: Encrypted input value

    Returns:
        Encrypted result of polynomial evaluation

    Example:
        >>> helper = CKKSHelper()
        >>> encrypted_x = helper.encrypt(2.0)
        >>> # Evaluate f(x) = 3x^2 + 2x + 1
        >>> result = polynomial_evaluation(helper, [1, 2, 3], encrypted_x)
    """
    if not coefficients:
        raise ValueError("Coefficients list cannot be empty")

    # Start with highest degree coefficient
    result = helper.encrypt(coefficients[-1])

    # Horner's method: ((...(a_n * x + a_(n-1)) * x + ...) + a_1) * x + a_0
    for coef in reversed(coefficients[:-1]):
        result = helper.multiply(result, encrypted_x)
        encrypted_coef = helper.encrypt(coef)
        result = helper.add(result, encrypted_coef)

    return result


def matrix_vector_multiply(helper, matrix: List[List[float]],
                          encrypted_vector: List) -> List:
    """
    Multiply a plaintext matrix by an encrypted vector.

    Args:
        helper: CKKSHelper or BFVHelper instance
        matrix: Plaintext matrix (list of lists)
        encrypted_vector: List of encrypted values

    Returns:
        List of encrypted results

    Example:
        >>> helper = CKKSHelper()
        >>> matrix = [[1, 2], [3, 4]]
        >>> encrypted_vec = [helper.encrypt(5.0), helper.encrypt(6.0)]
        >>> result = matrix_vector_multiply(helper, matrix, encrypted_vec)
    """
    if not matrix or not encrypted_vector:
        raise ValueError("Matrix and vector cannot be empty")

    result = []
    for row in matrix:
        if len(row) != len(encrypted_vector):
            raise ValueError("Matrix columns must match vector length")

        # Compute dot product of row with encrypted vector
        encrypted_products = []
        for val, enc_val in zip(row, encrypted_vector):
            encrypted_scalar = helper.encrypt(val)
            encrypted_products.append(helper.multiply(encrypted_scalar, enc_val))

        # Sum all products
        row_sum = encrypted_products[0]
        for prod in encrypted_products[1:]:
            row_sum = helper.add(row_sum, prod)
        result.append(row_sum)

    return result


def dot_product(helper, encrypted_vec1: List, encrypted_vec2: List) -> 'seal.Ciphertext':
    """
    Compute dot product of two encrypted vectors.

    Args:
        helper: CKKSHelper or BFVHelper instance
        encrypted_vec1: First encrypted vector
        encrypted_vec2: Second encrypted vector

    Returns:
        Encrypted dot product result

    Example:
        >>> helper = CKKSHelper()
        >>> vec1 = [helper.encrypt(1.0), helper.encrypt(2.0), helper.encrypt(3.0)]
        >>> vec2 = [helper.encrypt(4.0), helper.encrypt(5.0), helper.encrypt(6.0)]
        >>> result = dot_product(helper, vec1, vec2)  # 1*4 + 2*5 + 3*6 = 32
    """
    if len(encrypted_vec1) != len(encrypted_vec2):
        raise ValueError("Vectors must have same length")

    if not encrypted_vec1:
        raise ValueError("Vectors cannot be empty")

    # Multiply element-wise
    products = [helper.multiply(e1, e2) for e1, e2 in zip(encrypted_vec1, encrypted_vec2)]

    # Sum all products
    result = products[0]
    for prod in products[1:]:
        result = helper.add(result, prod)

    return result


def measure_performance(func: Callable) -> Callable:
    """
    Decorator to measure performance of a function.

    Example:
        >>> @measure_performance
        ... def my_encryption_task(helper, data):
        ...     return helper.encrypt(data)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f"{func.__name__} took {elapsed:.4f} seconds")
        return result
    return wrapper


# Convenience alias
SEALContext = SEALContextManager
