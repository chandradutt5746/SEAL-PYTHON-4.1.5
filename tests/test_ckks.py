"""
Basic pytest tests for SEAL-Python CKKS scheme.
"""
import pytest

# These tests will be skipped if seal.so is not built
try:
    import seal
    SEAL_AVAILABLE = True
except ImportError:
    SEAL_AVAILABLE = False

pytestmark = pytest.mark.skipif(not SEAL_AVAILABLE, reason="SEAL extension not built")


@pytest.fixture
def ckks_params():
    """Create basic CKKS parameters for testing."""
    if not SEAL_AVAILABLE:
        return None

    parms = seal.EncryptionParameters(seal.scheme_type.ckks)
    poly_modulus_degree = 8192
    parms.set_poly_modulus_degree(poly_modulus_degree)
    parms.set_coeff_modulus(seal.CoeffModulus.Create(
        poly_modulus_degree, [60, 40, 40, 60]
    ))
    return parms


@pytest.fixture
def ckks_context(ckks_params):
    """Create SEAL context for testing."""
    if not SEAL_AVAILABLE:
        return None
    return seal.SEALContext(ckks_params)


@pytest.fixture
def ckks_keys(ckks_context):
    """Generate keys for testing."""
    if not SEAL_AVAILABLE:
        return None

    keygen = seal.KeyGenerator(ckks_context)
    secret_key = keygen.secret_key()
    public_key = keygen.create_public_key()
    relin_keys = keygen.create_relin_keys()

    return {
        'secret_key': secret_key,
        'public_key': public_key,
        'relin_keys': relin_keys
    }


def test_seal_import():
    """Test that SEAL can be imported."""
    import seal
    assert seal is not None


def test_context_creation(ckks_context):
    """Test SEAL context creation."""
    assert ckks_context is not None


def test_encryption_parameters(ckks_params):
    """Test encryption parameters."""
    assert ckks_params is not None
    assert ckks_params.scheme() == seal.scheme_type.ckks


def test_key_generation(ckks_keys):
    """Test key generation."""
    assert ckks_keys is not None
    assert ckks_keys['secret_key'] is not None
    assert ckks_keys['public_key'] is not None
    assert ckks_keys['relin_keys'] is not None


def test_basic_encryption_decryption(ckks_context, ckks_keys):
    """Test basic encryption and decryption."""
    scale = 2.0 ** 40

    # Create encoder, encryptor, and decryptor
    encoder = seal.CKKSEncoder(ckks_context)
    encryptor = seal.Encryptor(ckks_context, ckks_keys['public_key'])
    decryptor = seal.Decryptor(ckks_context, ckks_keys['secret_key'])

    # Encode a value
    plain = seal.Plaintext()
    value = 3.14159
    encoder.encode(value, scale, plain)

    # Encrypt
    encrypted = encryptor.encrypt(plain)

    # Decrypt
    decrypted_plain = seal.Plaintext()
    decryptor.decrypt(encrypted, decrypted_plain)

    # Decode
    result = encoder.decode(decrypted_plain)

    # Check result (allow for small floating point error)
    assert abs(result[0] - value) < 0.001


def test_addition(ckks_context, ckks_keys):
    """Test homomorphic addition."""
    scale = 2.0 ** 40

    encoder = seal.CKKSEncoder(ckks_context)
    encryptor = seal.Encryptor(ckks_context, ckks_keys['public_key'])
    decryptor = seal.Decryptor(ckks_context, ckks_keys['secret_key'])
    evaluator = seal.Evaluator(ckks_context)

    # Encode and encrypt two values
    plain1 = seal.Plaintext()
    plain2 = seal.Plaintext()
    value1 = 1.5
    value2 = 2.5

    encoder.encode(value1, scale, plain1)
    encoder.encode(value2, scale, plain2)

    encrypted1 = encryptor.encrypt(plain1)
    encrypted2 = encryptor.encrypt(plain2)

    # Add encrypted values
    encrypted_result = seal.Ciphertext()
    evaluator.add(encrypted1, encrypted2, encrypted_result)

    # Decrypt and decode
    decrypted = seal.Plaintext()
    decryptor.decrypt(encrypted_result, decrypted)
    result = encoder.decode(decrypted)

    expected = value1 + value2
    assert abs(result[0] - expected) < 0.001


def test_multiplication(ckks_context, ckks_keys):
    """Test homomorphic multiplication."""
    scale = 2.0 ** 40

    encoder = seal.CKKSEncoder(ckks_context)
    encryptor = seal.Encryptor(ckks_context, ckks_keys['public_key'])
    decryptor = seal.Decryptor(ckks_context, ckks_keys['secret_key'])
    evaluator = seal.Evaluator(ckks_context)

    # Encode and encrypt two values
    plain1 = seal.Plaintext()
    plain2 = seal.Plaintext()
    value1 = 2.0
    value2 = 3.0

    encoder.encode(value1, scale, plain1)
    encoder.encode(value2, scale, plain2)

    encrypted1 = encryptor.encrypt(plain1)
    encrypted2 = encryptor.encrypt(plain2)

    # Multiply encrypted values
    encrypted_result = seal.Ciphertext()
    evaluator.multiply(encrypted1, encrypted2, encrypted_result)
    evaluator.relinearize_inplace(encrypted_result, ckks_keys['relin_keys'])
    evaluator.rescale_to_next_inplace(encrypted_result)

    # Decrypt and decode
    decrypted = seal.Plaintext()
    decryptor.decrypt(encrypted_result, decrypted)
    result = encoder.decode(decrypted)

    expected = value1 * value2
    assert abs(result[0] - expected) < 0.01
