"""
High-level utilities and helper classes for SEAL-Python.

This module provides convenient wrapper classes and utilities to make
working with Microsoft SEAL easier for Python developers.
"""
from typing import List, Optional, Union, Tuple
import numpy as np


try:
    from . import seal
    SEAL_AVAILABLE = True
except (ImportError, AttributeError):
    try:
        import seal
        SEAL_AVAILABLE = True
    except ImportError:
        SEAL_AVAILABLE = False


__all__ = [
    'CKKSHelper',
    'BFVHelper',
    'serialize_to_bytes',
    'deserialize_from_bytes',
    'create_ckks_params',
    'create_bfv_params',
]


def create_ckks_params(poly_modulus_degree: int = 8192,
                       coeff_modulus_bits: Optional[List[int]] = None):
    """
    Create CKKS encryption parameters with sensible defaults.

    Args:
        poly_modulus_degree: Degree of polynomial modulus (power of 2, typically 4096-32768)
        coeff_modulus_bits: List of bit-lengths for coefficient modulus chain

    Returns:
        EncryptionParameters object configured for CKKS

    Example:
        >>> params = create_ckks_params(8192, [60, 40, 40, 60])
        >>> context = seal.SEALContext(params)
    """
    if not SEAL_AVAILABLE:
        raise ImportError("SEAL extension not available. Please build the extension first.")

    if coeff_modulus_bits is None:
        # Default coefficient modulus based on poly_modulus_degree
        if poly_modulus_degree == 4096:
            coeff_modulus_bits = [40, 40, 40]
        elif poly_modulus_degree == 8192:
            coeff_modulus_bits = [60, 40, 40, 60]
        elif poly_modulus_degree == 16384:
            coeff_modulus_bits = [60, 60, 60, 60, 60]
        else:
            raise ValueError(f"No default coeff modulus for poly_modulus_degree={poly_modulus_degree}")

    parms = seal.EncryptionParameters(seal.scheme_type.ckks)
    parms.set_poly_modulus_degree(poly_modulus_degree)
    parms.set_coeff_modulus(seal.CoeffModulus.Create(poly_modulus_degree, coeff_modulus_bits))
    return parms


def create_bfv_params(poly_modulus_degree: int = 4096,
                      plain_modulus_bits: int = 20):
    """
    Create BFV encryption parameters with sensible defaults.

    Args:
        poly_modulus_degree: Degree of polynomial modulus (power of 2, typically 4096-32768)
        plain_modulus_bits: Bit-length for plaintext modulus

    Returns:
        EncryptionParameters object configured for BFV

    Example:
        >>> params = create_bfv_params(4096, 20)
        >>> context = seal.SEALContext(params)
    """
    if not SEAL_AVAILABLE:
        raise ImportError("SEAL extension not available. Please build the extension first.")

    parms = seal.EncryptionParameters(seal.scheme_type.bfv)
    parms.set_poly_modulus_degree(poly_modulus_degree)
    parms.set_coeff_modulus(seal.CoeffModulus.BFVDefault(poly_modulus_degree))
    parms.set_plain_modulus(seal.PlainModulus.Batching(poly_modulus_degree, plain_modulus_bits))
    return parms


def serialize_to_bytes(obj) -> bytes:
    """
    Serialize a SEAL object to bytes.

    Args:
        obj: SEAL object (Ciphertext, PublicKey, SecretKey, etc.)

    Returns:
        Bytes representation of the object

    Example:
        >>> encrypted = encryptor.encrypt(plain)
        >>> data = serialize_to_bytes(encrypted)
    """
    if not SEAL_AVAILABLE:
        raise ImportError("SEAL extension not available")

    # Most SEAL objects have a save method
    import io
    buffer = io.BytesIO()
    obj.save(buffer)
    return buffer.getvalue()


def deserialize_from_bytes(data: bytes, obj_type):
    """
    Deserialize SEAL object from bytes.

    Args:
        data: Bytes representation
        obj_type: Type of object to create (seal.Ciphertext, seal.PublicKey, etc.)

    Returns:
        Deserialized SEAL object

    Example:
        >>> data = serialize_to_bytes(encrypted)
        >>> encrypted_copy = deserialize_from_bytes(data, seal.Ciphertext)
    """
    if not SEAL_AVAILABLE:
        raise ImportError("SEAL extension not available")

    import io
    obj = obj_type()
    buffer = io.BytesIO(data)
    obj.load(buffer)
    return obj


class CKKSHelper:
    """
    High-level helper class for CKKS operations.

    This class simplifies common CKKS operations by managing the context,
    keys, and providing convenient methods for encryption and computation.

    Example:
        >>> helper = CKKSHelper(poly_modulus_degree=8192)
        >>> encrypted_x = helper.encrypt(3.14)
        >>> encrypted_y = helper.encrypt(2.0)
        >>> encrypted_sum = helper.add(encrypted_x, encrypted_y)
        >>> result = helper.decrypt(encrypted_sum)
    """

    def __init__(self,
                 poly_modulus_degree: int = 8192,
                 coeff_modulus_bits: Optional[List[int]] = None,
                 scale_bits: int = 40):
        """
        Initialize CKKS helper with encryption parameters.

        Args:
            poly_modulus_degree: Degree of polynomial modulus
            coeff_modulus_bits: Coefficient modulus bit lengths
            scale_bits: Default scale for encoding (typically 30-60)
        """
        if not SEAL_AVAILABLE:
            raise ImportError("SEAL extension not available. Please build the extension first.")

        self.params = create_ckks_params(poly_modulus_degree, coeff_modulus_bits)
        self.context = seal.SEALContext(self.params)
        self.scale = 2.0 ** scale_bits

        # Generate keys
        self.keygen = seal.KeyGenerator(self.context)
        self.secret_key = self.keygen.secret_key()
        self.public_key = self.keygen.create_public_key()
        self.relin_keys = self.keygen.create_relin_keys()

        # Create encoder, encryptor, decryptor, evaluator
        self.encoder = seal.CKKSEncoder(self.context)
        self.encryptor = seal.Encryptor(self.context, self.public_key)
        self.decryptor = seal.Decryptor(self.context, self.secret_key)
        self.evaluator = seal.Evaluator(self.context)

    def encrypt(self, value: Union[float, List[float], np.ndarray]) -> 'seal.Ciphertext':
        """
        Encrypt a value or array of values.

        Args:
            value: Float, list of floats, or NumPy array

        Returns:
            Encrypted ciphertext
        """
        plain = seal.Plaintext()

        if isinstance(value, (int, float)):
            self.encoder.encode(float(value), self.scale, plain)
        elif isinstance(value, (list, np.ndarray)):
            if isinstance(value, np.ndarray):
                value = value.tolist()
            self.encoder.encode(value, self.scale, plain)
        else:
            raise TypeError(f"Cannot encrypt type {type(value)}")

        return self.encryptor.encrypt(plain)

    def decrypt(self, encrypted: 'seal.Ciphertext') -> Union[float, List[float]]:
        """
        Decrypt a ciphertext.

        Args:
            encrypted: Ciphertext to decrypt

        Returns:
            Decrypted value(s)
        """
        plain = seal.Plaintext()
        self.decryptor.decrypt(encrypted, plain)
        result = self.encoder.decode(plain)

        # Return single value if it's a scalar
        if len(result) == 1:
            return result[0]
        return result

    def add(self, encrypted1: 'seal.Ciphertext', encrypted2: 'seal.Ciphertext') -> 'seal.Ciphertext':
        """Add two encrypted values."""
        result = seal.Ciphertext()
        self.evaluator.add(encrypted1, encrypted2, result)
        return result

    def multiply(self, encrypted1: 'seal.Ciphertext', encrypted2: 'seal.Ciphertext') -> 'seal.Ciphertext':
        """Multiply two encrypted values."""
        result = seal.Ciphertext()
        self.evaluator.multiply(encrypted1, encrypted2, result)
        self.evaluator.relinearize_inplace(result, self.relin_keys)
        self.evaluator.rescale_to_next_inplace(result)
        return result

    def negate(self, encrypted: 'seal.Ciphertext') -> 'seal.Ciphertext':
        """Negate an encrypted value."""
        result = seal.Ciphertext()
        self.evaluator.negate(encrypted, result)
        return result

    def square(self, encrypted: 'seal.Ciphertext') -> 'seal.Ciphertext':
        """Square an encrypted value."""
        result = seal.Ciphertext()
        self.evaluator.square(encrypted, result)
        self.evaluator.relinearize_inplace(result, self.relin_keys)
        self.evaluator.rescale_to_next_inplace(result)
        return result


class BFVHelper:
    """
    High-level helper class for BFV operations.

    This class simplifies common BFV operations for integer arithmetic.

    Example:
        >>> helper = BFVHelper(poly_modulus_degree=4096)
        >>> encrypted_x = helper.encrypt([1, 2, 3, 4, 5])
        >>> encrypted_y = helper.encrypt([5, 4, 3, 2, 1])
        >>> encrypted_sum = helper.add(encrypted_x, encrypted_y)
        >>> result = helper.decrypt(encrypted_sum)
    """

    def __init__(self,
                 poly_modulus_degree: int = 4096,
                 plain_modulus_bits: int = 20):
        """
        Initialize BFV helper with encryption parameters.

        Args:
            poly_modulus_degree: Degree of polynomial modulus
            plain_modulus_bits: Bit-length for plaintext modulus
        """
        if not SEAL_AVAILABLE:
            raise ImportError("SEAL extension not available. Please build the extension first.")

        self.params = create_bfv_params(poly_modulus_degree, plain_modulus_bits)
        self.context = seal.SEALContext(self.params)

        # Generate keys
        self.keygen = seal.KeyGenerator(self.context)
        self.secret_key = self.keygen.secret_key()
        self.public_key = self.keygen.create_public_key()
        self.relin_keys = self.keygen.create_relin_keys()

        # Create encoder, encryptor, decryptor, evaluator
        self.encoder = seal.BatchEncoder(self.context)
        self.encryptor = seal.Encryptor(self.context, self.public_key)
        self.decryptor = seal.Decryptor(self.context, self.secret_key)
        self.evaluator = seal.Evaluator(self.context)

        self.slot_count = self.encoder.slot_count()

    def encrypt(self, values: Union[int, List[int]]) -> 'seal.Ciphertext':
        """
        Encrypt integer value(s).

        Args:
            values: Integer or list of integers

        Returns:
            Encrypted ciphertext
        """
        if isinstance(values, int):
            values = [values]

        # Pad with zeros to slot_count
        if len(values) < self.slot_count:
            values = values + [0] * (self.slot_count - len(values))
        elif len(values) > self.slot_count:
            raise ValueError(f"Too many values ({len(values)}), max is {self.slot_count}")

        plain = seal.Plaintext()
        self.encoder.encode(values, plain)
        return self.encryptor.encrypt(plain)

    def decrypt(self, encrypted: 'seal.Ciphertext') -> List[int]:
        """
        Decrypt a ciphertext.

        Args:
            encrypted: Ciphertext to decrypt

        Returns:
            List of decrypted integers
        """
        plain = seal.Plaintext()
        self.decryptor.decrypt(encrypted, plain)
        result = []
        self.encoder.decode(plain, result)
        return result

    def add(self, encrypted1: 'seal.Ciphertext', encrypted2: 'seal.Ciphertext') -> 'seal.Ciphertext':
        """Add two encrypted values."""
        result = seal.Ciphertext()
        self.evaluator.add(encrypted1, encrypted2, result)
        return result

    def multiply(self, encrypted1: 'seal.Ciphertext', encrypted2: 'seal.Ciphertext') -> 'seal.Ciphertext':
        """Multiply two encrypted values."""
        result = seal.Ciphertext()
        self.evaluator.multiply(encrypted1, encrypted2, result)
        self.evaluator.relinearize_inplace(result, self.relin_keys)
        return result

    def negate(self, encrypted: 'seal.Ciphertext') -> 'seal.Ciphertext':
        """Negate an encrypted value."""
        result = seal.Ciphertext()
        self.evaluator.negate(encrypted, result)
        return result
