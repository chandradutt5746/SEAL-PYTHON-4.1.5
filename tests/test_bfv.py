"""
Pytest tests for SEAL-Python BFV scheme.
"""
import pytest

try:
    import seal
    SEAL_AVAILABLE = True
except ImportError:
    SEAL_AVAILABLE = False

pytestmark = pytest.mark.skipif(not SEAL_AVAILABLE, reason="SEAL extension not built")


@pytest.fixture
def bfv_params():
    """Create basic BFV parameters for testing."""
    if not SEAL_AVAILABLE:
        return None

    parms = seal.EncryptionParameters(seal.scheme_type.bfv)
    poly_modulus_degree = 4096
    parms.set_poly_modulus_degree(poly_modulus_degree)
    parms.set_coeff_modulus(seal.CoeffModulus.BFVDefault(poly_modulus_degree))
    parms.set_plain_modulus(seal.PlainModulus.Batching(poly_modulus_degree, 20))
    return parms


@pytest.fixture
def bfv_context(bfv_params):
    """Create SEAL context for BFV testing."""
    if not SEAL_AVAILABLE:
        return None
    return seal.SEALContext(bfv_params)


@pytest.fixture
def bfv_keys(bfv_context):
    """Generate keys for BFV testing."""
    if not SEAL_AVAILABLE:
        return None

    keygen = seal.KeyGenerator(bfv_context)
    secret_key = keygen.secret_key()
    public_key = keygen.create_public_key()
    relin_keys = keygen.create_relin_keys()

    return {
        'secret_key': secret_key,
        'public_key': public_key,
        'relin_keys': relin_keys
    }


def test_bfv_encryption_decryption(bfv_context, bfv_keys):
    """Test basic BFV encryption and decryption."""
    encoder = seal.BatchEncoder(bfv_context)
    encryptor = seal.Encryptor(bfv_context, bfv_keys['public_key'])
    decryptor = seal.Decryptor(bfv_context, bfv_keys['secret_key'])

    # Create a vector of integers
    slot_count = encoder.slot_count()
    pod_vector = [1, 2, 3, 4, 5] + [0] * (slot_count - 5)

    # Encode
    plain = seal.Plaintext()
    encoder.encode(pod_vector, plain)

    # Encrypt
    encrypted = encryptor.encrypt(plain)

    # Decrypt
    decrypted_plain = seal.Plaintext()
    decryptor.decrypt(encrypted, decrypted_plain)

    # Decode
    result = []
    encoder.decode(decrypted_plain, result)

    # Check first 5 values
    assert result[:5] == [1, 2, 3, 4, 5]


def test_bfv_addition(bfv_context, bfv_keys):
    """Test BFV homomorphic addition."""
    encoder = seal.BatchEncoder(bfv_context)
    encryptor = seal.Encryptor(bfv_context, bfv_keys['public_key'])
    decryptor = seal.Decryptor(bfv_context, bfv_keys['secret_key'])
    evaluator = seal.Evaluator(bfv_context)

    slot_count = encoder.slot_count()
    pod_vector1 = [1, 2, 3] + [0] * (slot_count - 3)
    pod_vector2 = [4, 5, 6] + [0] * (slot_count - 3)

    # Encode and encrypt
    plain1 = seal.Plaintext()
    plain2 = seal.Plaintext()
    encoder.encode(pod_vector1, plain1)
    encoder.encode(pod_vector2, plain2)

    encrypted1 = encryptor.encrypt(plain1)
    encrypted2 = encryptor.encrypt(plain2)

    # Add
    encrypted_result = seal.Ciphertext()
    evaluator.add(encrypted1, encrypted2, encrypted_result)

    # Decrypt and decode
    decrypted = seal.Plaintext()
    decryptor.decrypt(encrypted_result, decrypted)
    result = []
    encoder.decode(decrypted, result)

    # Check results
    assert result[:3] == [5, 7, 9]


def test_bfv_multiplication(bfv_context, bfv_keys):
    """Test BFV homomorphic multiplication."""
    encoder = seal.BatchEncoder(bfv_context)
    encryptor = seal.Encryptor(bfv_context, bfv_keys['public_key'])
    decryptor = seal.Decryptor(bfv_context, bfv_keys['secret_key'])
    evaluator = seal.Evaluator(bfv_context)

    slot_count = encoder.slot_count()
    pod_vector1 = [2, 3, 4] + [0] * (slot_count - 3)
    pod_vector2 = [3, 4, 5] + [0] * (slot_count - 3)

    # Encode and encrypt
    plain1 = seal.Plaintext()
    plain2 = seal.Plaintext()
    encoder.encode(pod_vector1, plain1)
    encoder.encode(pod_vector2, plain2)

    encrypted1 = encryptor.encrypt(plain1)
    encrypted2 = encryptor.encrypt(plain2)

    # Multiply
    encrypted_result = seal.Ciphertext()
    evaluator.multiply(encrypted1, encrypted2, encrypted_result)
    evaluator.relinearize_inplace(encrypted_result, bfv_keys['relin_keys'])

    # Decrypt and decode
    decrypted = seal.Plaintext()
    decryptor.decrypt(encrypted_result, decrypted)
    result = []
    encoder.decode(decrypted, result)

    # Check results (2*3=6, 3*4=12, 4*5=20)
    assert result[:3] == [6, 12, 20]
