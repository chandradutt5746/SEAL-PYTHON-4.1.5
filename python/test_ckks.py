from seal import *
import cmath
import time
import os
import tempfile

def convert_to_ciphertext(serializable_ct, context):
    """Convert SerializableCiphertext to Ciphertext for use with Evaluator operations.
    
    The SEAL Python binding has SerializableCiphertext and Ciphertext as separate types.
    Evaluator operations require Ciphertext objects, while encrypt() returns SerializableCiphertext.
    This function handles the conversion efficiently using an     # Encode and encrypt a vector of complex numbers
    complex_data = [cmath.rect(1, i * 0.1) for i in range(10)]
    
    # Extract real parts for encode_new as this binding doesn't support direct complex encoding
    real_data = [complex_num.real for complex_num in complex_data]
    plain = encoder.encode_new(real_data, scale)emory temporary file.
    
    Args:
        serializable_ct: The SerializableCiphertext returned by encryptor.encrypt()
        context: SEALContext object used for loading
        
    Returns:
        Ciphertext: A regular Ciphertext object that can be used with Evaluator
    """
    # Check if already a Ciphertext (no conversion needed)
    if isinstance(serializable_ct, Ciphertext):
        return serializable_ct
    
    # Create a temporary file that gets automatically deleted when closed
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        # Save to temp file
        serializable_ct.save(temp_filename)
        
        # Load as Ciphertext
        ciphertext = Ciphertext()
        ciphertext.load(context, temp_filename)
        return ciphertext
    finally:
        # Clean up temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

"""CKKS Homomorphic Encryption Setup Example (Beginner Friendly)

    This function sets up the CKKS scheme from Microsoft SEAL in Python.
    It explains every step in detail, so even someone new to cryptography can follow along.

    What is the CKKS Scheme?
    ------------------------
    CKKS is a type of homomorphic encryption that lets you do math on encrypted real (decimal) numbers.
    It's great for privacy-preserving computations on things like sensor data, statistics, or machine learning.
    """
def get_seal():
    """1. **Set Encryption Parameters**
       - `EncryptionParameters(SchemeType.CKKS)`: Choose the CKKS scheme.
       - `poly_modulus_degree`: Controls how much data you can encrypt at once and how secure it is.
         - Must be a power of two (e.g., 2048, 4096, 8192, 16384, 32768).
         - Bigger numbers = more security and more slots, but slower.
       - `coeff_modulus`: A list of big prime numbers that control how much noise the ciphertext can handle.
         - Use `CoeffModulus.Create(poly_modulus_degree, [bit_sizes...])` for custom settings.
         - Example: `[60, 40, 40, 60]` gives you 4 levels for computations.
       - `scale`: Controls the precision of your numbers (bigger = more precise, but more noise).
         - Commonly set as `2.0 ** 40` or `2.0 ** 30`.
    """
    parms = EncryptionParameters(SchemeType.CKKS)
    
    # Choose parameters based on security level
    # if security_level == sec_level_type.TC192:  # UPPERCASE
    #     poly_modulus_degree = 16384
    #     coeff_modulus = [60, 50, 50, 50, 50, 60]
    # elif security_level == sec_level_type.TC256:  # UPPERCASE
    #     poly_modulus_degree = 32768
    #     coeff_modulus = [60, 55, 55, 55, 55, 55, 60]
    # else:  # Default to 128-bit
    #     poly_modulus_degree = 8192
    #     coeff_modulus = [60, 40, 40, 60]

    poly_modulus_degree = 8192
    parms.set_poly_modulus_degree(poly_modulus_degree)
    parms.set_coeff_modulus(CoeffModulus.Create(8192, [60, 40, 40, 60]))
    scale = 2.0 ** 40
    """2. **Create a SEAL Context**
       - `SEALContext(parms)`: Checks your parameters and prepares everything for encryption.
       - This is where all the magic happens, and it ensures your parameters are valid
         and compatible with the CKKS scheme.

        3. **Create Helper Objects**
       - `CKKSEncoder`: Packs real numbers into a format that can be encrypted.
       - `slot_count`: How many numbers you can pack at once (half of `poly_modulus_degree`).

    """
    context = SEALContext(parms, expand_mod_chain=True, sec_level=sec_level_type.TC128)
    
    # Validate parameters
    if not context.parameters_set():
        context_data = context.key_context_data()
        if context_data:
            qualifiers = context_data.qualifiers
            error_msg = f"Parameters invalid: {qualifiers.parameter_error_name} - {qualifiers.parameter_error_message}"
            raise ValueError(error_msg)
        raise ValueError("Encryption parameters are invalid")
    

    context_data = context.key_context_data()
    if context_data:
        qualifiers = context_data.qualifiers  
        print(f'[DEBUG] Security level: {qualifiers.sec_level}')
    else:
        print('[WARNING] No context data available')

    ckks_encoder = CKKSEncoder(context)
    slot_count = ckks_encoder.slot_count()
    print('[DEBUG] Slot count:', slot_count)
    """4. **Generate Keys**
       - `KeyGenerator(context)`: Makes all the keys you need.
       - `public_key`: Used to encrypt data (can be shared).
       - `secret_key`: Used to decrypt data (keep this secret!).
       - `relin_keys`: Used for advanced operations like multiplication.
       - `galois_keys`: Used for rotations and conjugations.
    """
    keygen = KeyGenerator(context)
    public_key = keygen.create_public_key()
    secret_key = keygen.secret_key()
    relin_keys = keygen.create_relin_keys()
    galios_keys = keygen.create_galois_keys()
    print('[DEBUG] relin_keys size:', type(relin_keys))
    """5. **Create Encryptor, Evaluator, Decryptor**
       - `Encryptor`: Encrypts plaintext using the public key.
       - `Evaluator`: Lets you do math on ciphertexts (add, multiply, rotate, etc.).
       - `Decryptor`: Decrypts ciphertext using the secret key.
    """
    print('[DEBUG] Creating Encryptor, Evaluator, Decryptor')
    # Create Encryptor, Evaluator, Decryptor
    # Encryptor uses the public key, Decryptor uses the secret key
    # Evaluator is used for performing operations on ciphertexts
    # Note: Encryptor and Decryptor are not used for encoding/decoding,
    # they are used for encrypting and decrypting data.
    encryptor = Encryptor(context, public_key)
    evaluator = Evaluator(context)
    decryptor = Decryptor(context, secret_key)

    """
    6. **Encode and Encrypt Data**
       - You can't encrypt numbers directly; you must encode them first.
       - Example: `[1.23, 4.56, 7.89]` is encoded and then encrypted.
       - `encoder.encode_new(data, scale)`: Packs the numbers into a `Plaintext`.
       - `encryptor.encrypt(plain)`: Encrypts the plaintext into a ciphertext.

    7. **Test Decoding**
       - Immediately decode the plaintext to check that encoding worked as expected.

    Returns:
        A tuple of all the important objects you need for CKKS operations:
        (cipher, context, encoder, decryptor, evaluator, encryptor, scale, relin_keys, galois_keys)

    """
    print('[DEBUG] Encoding and encrypting data')
    data = [1.23, 4.56, 7.89]
    plain = ckks_encoder.encode_new(data, scale)
    test_decoded = ckks_encoder.decode(plain)
    # Print first 5 decoded values for verification. If you want to see more, change the number or remove the slicing.
    print('[DEBUG] Decoded immediately after encoding:', test_decoded[:5]) 
    cipher = encryptor.encrypt(plain)

    return cipher, context, ckks_encoder, decryptor, evaluator, encryptor, scale, relin_keys, galios_keys

def evaluator_example():
    print('evaluator example')
    print('-' * 70)
    cipher, context, encoder, decryptor, evaluator, encryptor, scale, relin_keys, galios_keys = get_seal()

    # Encode and encrypt another vector
    data2 = [2.0, 3.0, 4.0]
    plain2 = encoder.encode_new(data2, scale)
    cipher2 = encryptor.encrypt(plain2)  # returns SerializableCiphertext

    # Convert SerializableCiphertext to Ciphertext for Evaluator
    cipher2 = convert_to_ciphertext(cipher2, context)
    
    # If cipher from get_seal() is not Ciphertext, convert:
    cipher = convert_to_ciphertext(cipher, context)

    print('[DEBUG] Encoded and encrypted data2:', data2)

    # Addition
    evaluator.add_inplace(cipher, cipher2)
    print('[DEBUG] Performed add_inplace')

    # Decrypt and decode
    plain_result = Plaintext()
    decryptor.decrypt(cipher, plain_result)
    decoded_result = encoder.decode(plain_result)
    print('[DEBUG] Decoded after addition:', decoded_result[:10])

    # Multiplication
    evaluator.multiply_inplace(cipher, cipher2)
    evaluator.relinearize_inplace(cipher, relin_keys)
    print('[DEBUG] Performed relinearize_inplace after multiply')
    print('[DEBUG] Performed multiply_inplace')

    # Decrypt and decode
    plain_result2 = Plaintext()
    decryptor.decrypt(cipher, plain_result2)
    decoded_result2 = encoder.decode(plain_result2)
    print('[DEBUG] Decoded after multiplication:', decoded_result2[:10])

    # Rescale (if supported)
    try:
        # Create destination for rescaled result
        rescaled_cipher = Ciphertext()
        evaluator.rescale_to_next(cipher, rescaled_cipher)
        cipher = rescaled_cipher  # Update cipher reference
        print('[DEBUG] Performed rescale_to_next')
        
        # Decrypt and decode using our helper function
        decoded_result3 = decrypt_and_decode(cipher, decryptor, encoder)
        print('[DEBUG] Decoded after rescale:', decoded_result3)
    except Exception as e:
        print('[DEBUG] Rescale failed:', e)
    
    # Square
    evaluator.square_inplace(cipher)
    evaluator.relinearize_inplace(cipher, relin_keys)
    print('[DEBUG] Performed square_inplace')
    plain_sq = Plaintext()
    decryptor.decrypt(cipher, plain_sq)
    decoded_sq = encoder.decode(plain_sq)
    print('[DEBUG] Decoded after square:', decoded_sq[:10])

    print('-' * 70)

    # After multiplication or square performing relinerization
    evaluator.relinearize_inplace(cipher, relin_keys)
    print('[DEBUG] Performed relinearize_inplace')
    plain_relin = Plaintext()
    decryptor.decrypt(cipher, plain_relin)
    decoded_relin = encoder.decode(plain_relin)
    print('[DEBUG] Decoded after relinearization:', decoded_relin[:10])
    print('-' * 70)

def serialization_example():
    """CKKS Ciphertext Serialization Example

    This function demonstrates how to save (serialize) and load (deserialize) encrypted data using the CKKS scheme.
    Serialization lets you store encrypted data on disk or send it over a network, and load it back later.

    Step-by-Step Explanation:
    ------------------------

    1. **Get CKKS Setup**
       - Calls `get_seal()` to get all the objects you need.

    2. **Save Ciphertext to Disk**
       - `cipher.save('cipher2.bin')`: Saves the encrypted data to a file.

    3. **Load Ciphertext from Disk**
       - `cipher3.load(context2, 'cipher2.bin')`: Loads the encrypted data back from the file.

    4. **Decrypt and Decode**
       - Decrypts and decodes the loaded ciphertext to verify correctness.
    """
    print('serialization example')
    print('-' * 70)
    cipher2, context2, ckks_encoder2, decryptor2, *_ = get_seal()
    cipher2.save('cipher2.bin')
    print('save cipher2 data success')

    # Wait for a short time to ensure the file is written before loading
    time.sleep(.5)

    cipher3 = Ciphertext()
    cipher3.load(context2, 'cipher2.bin')
    print('load cipher2 data success')

    plain3 = Plaintext()  
    decryptor2.decrypt(cipher3, plain3)  
    print('plain3 scale:', plain3.scale())
    print('plain3 coeff count:', plain3.coeff_count())
    print('slot_count:', ckks_encoder2.slot_count())
    data3 = ckks_encoder2.decode(plain3)
    print('decoded data3:', data3[:5])
    print('-' * 70)


def pickle_example():
    """
    CKKS Pickle-like Serialization Example

    This function demonstrates saving and loading ciphertexts, similar to Python's pickle,
    but using SEAL's built-in serialization for encrypted data.

    Steps:
    ------
    1. Get CKKS setup and encrypt data.
    2. Save ciphertext to a file.
    3. Load ciphertext from the file.
    4. Decrypt and decode to verify correctness.
    """
    print('pickle example')
    print('-' * 70)
    cipher1, context1, ckks_encoder1, decryptor1, *_ = get_seal()
    cipher1.save('cipher1.bin')
    print('write cipher1 data success')

    time.sleep(.5)

    cipher2 = Ciphertext()
    cipher2.load(context1, 'cipher1.bin')
    plain2 = Plaintext()
    decryptor1.decrypt(cipher2, plain2)
    data = ckks_encoder1.decode(plain2)
    print('read cipher1 data success')
    print(data[:5])

    print('-' * 70)


def key_serialization_example():
    """
    CKKS Key Serialization Example

    This function demonstrates how to save and load public, secret, relinearization, and Galois keys.
    Key serialization is important for securely storing and sharing keys.

    Steps:
    ------
    1. Generate all keys using KeyGenerator.
    2. Save each key to a file.
    3. Load each key back from the file.
    4. Print the type of each loaded key to verify.
    """
    print('key serialization example')
    print('-' * 70)

    _, context, _, _, _, _, _, relin_keys, galios_keys = get_seal()

    # Generate keys
    keygen = KeyGenerator(context)
    public_key = keygen.create_public_key()
    secret_key = keygen.secret_key()
    relin_keys = keygen.create_relin_keys()
    galios_keys = keygen.create_galois_keys()

    # Save keys
    print('[DEBUG] Saving keys to disk')
    public_key.save('public.key')
    secret_key.save('secret.key')
    relin_keys.save('relin.key')
    galios_keys.save('galios.key')
    print('[DEBUG] Keys saved to disk')

    # Load keys using module-level functions

    loaded_public_key = load_public_key(context, 'public.key')
    loaded_secret_key = load_secret_key(context, 'secret.key')
    loaded_relin_keys = load_relin_keys(context, 'relin.key')
    loaded_galios_keys = load_galois_keys(context, 'galios.key')
    print('[DEBUG] Keys loaded from disk')

    # Check types
    print('[DEBUG] Loaded public key type:', type(loaded_public_key))
    print('[DEBUG] Loaded secret key type:', type(loaded_secret_key))
    print('[DEBUG] Loaded relin keys type:', type(loaded_relin_keys))
    print('[DEBUG] Loaded galios keys type:', type(loaded_galios_keys))
    print('-' * 70)

def exception_handling_example():
    """CKKS Exception Handling Example

    This function demonstrates how to handle common errors and exceptions when using SEAL.
    It shows what happens if you try invalid operations, use wrong keys or load corrupted files.
    """
    print('exception handling example')
    print('-' * 70)
    try:
        cipher, context, encoder, decryptor, evaluator, encryptor, scale, relin_keys, galios_keys = get_seal()

        # 1. Invalid operation: add_inplace with Plaintext instead of Ciphertext
        try:
            evaluator.add_inplace(cipher, Plaintext())
        except Exception as e:
            print('[DEBUG][add_inplace] Exception caught as expected:', repr(e))

        # 2. Invalid decryption: using wrong key type
        try:
            wrong_decryptor = Decryptor(context, PublicKey())
            plain = Plaintext()
            wrong_decryptor.decrypt(cipher, plain)
        except Exception as e:
            print('[DEBUG][decrypt] Exception caught as expected:', repr(e))

        # 3. Loading a non-existent key file
        try:
            load_public_key(context, 'nonexistent.key')
        except Exception as e:
            print('[DEBUG][load_public_key] Exception caught as expected:', repr(e))

        # 4. Loading a corrupted ciphertext file
        try:
            with open('corrupt.bin', 'wb') as f:
                f.write(b'not a valid ciphertext')
            ct = Ciphertext()
            ct.load(context, 'corrupt.bin')
        except Exception as e:
            print('[DEBUG][load_ciphertext] Exception caught as expected:', repr(e))

        # 5. Invalid evaluator operation: rotate without Galois keys
        try:
            evaluator.rotate_vector_inplace(cipher, 1, GaloisKeys())
        except Exception as e:
            print('[DEBUG][rotate_vector_inplace] Exception caught as expected:', repr(e))

        # 6. Invalid scale: set scale to zero and try to encode
        try:
            encoder.encode_new([1.0, 2.0, 3.0], 0)
        except Exception as e:
            print('[DEBUG][encode_new] Exception caught as expected:', repr(e))

    except Exception as e:
        print('[DEBUG][outer] Unexpected exception:', repr(e))
    print('-' * 70)

def ckks_rescale_modswitch_example():
    """CKKS Rescale and Modulus Switching Example 

    This function demonstrates how to rescale and modulus switch an encrypted value using the CKKS scheme.
    Rescaling is used after multiplication to manage the scale and noise.
    Modulus switching is used to move to a smaller modulus for further operations.
    """
    print('CKKS rescale and modswitch example')
    print('-' * 70)
    cipher, context, encoder, decryptor, evaluator, encryptor, scale, relin_keys, galois_keys = get_seal()

    # Encode and encrypt
    data = [1.5, 2.5, 3.5]
    plain = encoder.encode_new(data, scale)
    cipher_serializable = encryptor.encrypt(plain)

    # Convert to Ciphertext for Evaluator
    cipher = convert_to_ciphertext(cipher_serializable, context)

    # Multiply and rescale
    evaluator.multiply_inplace(cipher, cipher)
    evaluator.relinearize_inplace(cipher, relin_keys)
    # Create destination ciphertext for rescale_to_next
    rescaled_cipher = Ciphertext()
    evaluator.rescale_to_next(cipher, rescaled_cipher)
    cipher = rescaled_cipher  # Update cipher to use the rescaled version
    print('[DEBUG] Performed multiply, relinearize, and rescale_to_next')

    # Modulus switch to next
    evaluator.mod_switch_to_next_inplace(cipher)
    print('[DEBUG] Performed mod_switch_to_next_inplace')

    # Decrypt and decode
    decoded = decrypt_and_decode(cipher, decryptor, encoder)
    print('[DEBUG] Decoded after rescale and modswitch:', decoded)
    print('-' * 70)

def ckks_conjugation_example():
    """CKKS Complex Conjugation Example 

    This function demonstrates how to apply complex conjugation to an encrypted vector using the CKKS scheme.
    Complex conjugation flips the sign of the imaginary part of each complex number.
    """
    print('CKKS complex conjugation example')
    print('-' * 70)
    cipher, context, encoder, decryptor, evaluator, encryptor, scale, relin_keys, galois_keys = get_seal()

    # Encode and encrypt a vector of complex numbers
    complex_data = [cmath.rect(1, i * 0.1) for i in range(10)]
    
    # Extract real parts for encode_new as this binding doesn't support direct complex encoding
    real_data = [complex_num.real for complex_num in complex_data]
    plain = encoder.encode_new(real_data, scale)
    cipher_serializable = encryptor.encrypt(plain)

    # Convert to Ciphertext for Evaluator
    cipher = convert_to_ciphertext(cipher_serializable, context)

    # Apply complex conjugation
    evaluator.complex_conjugate_inplace(cipher, galois_keys)
    print('[DEBUG] Performed complex_conjugate_inplace')

    # Decrypt and decode
    decoded_conj = decrypt_and_decode(cipher, decryptor, encoder)
    print('[DEBUG] Decoded after conjugation:', decoded_conj)
    print('-' * 70)

def ckks_rotation_example():
    """
    CKKS Rotation Example (Beginner Friendly)

    This function demonstrates how to rotate (shift) an encrypted vector using the CKKS scheme.
    Rotating a vector is like moving all the numbers to the left or right, wrapping around at the ends.

    Step-by-Step Explanation:
    ------------------------

    1. **Get CKKS Setup**
       - Calls `get_seal()` to get all the objects you need.

    2. **Encode and Encrypt a Vector**
       - Example: `[1.0, 2.0, ..., 10.0]` is encoded and encrypted.

    3. **Convert SerializableCiphertext to Ciphertext**
       - Some SEAL operations need a `Ciphertext` object, not a `SerializableCiphertext`.
       - We use our utility function to efficiently convert between types.

    4. **Rotate the Vector**
       - `evaluator.rotate_vector_inplace(cipher, 2, galois_keys)`: Rotates the vector left by 2 positions.

    5. **Decrypt and Decode**
       - Decrypts and decodes the result to show the rotated vector.
    """
    print('CKKS rotation example')
    print('-' * 70)
    cipher, context, encoder, decryptor, evaluator, encryptor, scale, relin_keys, galois_keys = get_seal()

    # Encode and encrypt a vector
    # Example: [1.0, 2.0, ..., 10.0]
    print('[DEBUG] Encoding and encrypting data for rotation')
    data = [i + 1.0 for i in range(10)]
    plain = encoder.encode_new(data, scale)
    cipher_serializable = encryptor.encrypt(plain)

    # Convert to Ciphertext for Evaluator
    print('[DEBUG] Converting SerializableCiphertext to Ciphertext for rotation')
    # This is necessary because some SEAL operations require a Ciphertext object not a SerializableCiphertext
    cipher = convert_to_ciphertext(cipher_serializable, context)

    # Rotate left by 2
    print('[DEBUG] Performing rotate_vector_inplace by 2')
    # Rotate the vector left by 2 positions
    # This means the first two elements will move to the end of the vector
    # For example, [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    # becomes [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 1.0, 2.0]
    # The third argument is the Galois keys, which are needed for rotation operations
    # Galois keys are generated during key generation
    # and are used for operations like rotation and conjugation
    # If you don't have Galois keys, you can't perform rotations
    if not isinstance(galois_keys, GaloisKeys):
        raise ValueError("Galois keys are required for rotation operations.")
    if not isinstance(cipher, Ciphertext):
        raise ValueError("Cipher must be a Ciphertext object for rotation operations.")
    if not isinstance(evaluator, Evaluator):
        raise ValueError("Evaluator must be an Evaluator object for rotation operations.")
    evaluator.rotate_vector_inplace(cipher, 2, galois_keys)
    print('[DEBUG] Performed rotate_vector_inplace by 2')

    # Decrypt and decode
    print('[DEBUG] Decrypting and decoding the rotated vector')
    decoded_rot = decrypt_and_decode(cipher, decryptor, encoder)
    print('[DEBUG] Decoded after rotation:', decoded_rot)
    print('-' * 70)

def numpy_integration_example():
    """Example showing how to use the NumPy integration features.
    
    This example demonstrates the high-performance NumPy integration features
    added to the SEAL-Python bindings.
    """
    try:
        import numpy as np
    except ImportError:
        print("NumPy not installed. Install with: pip install numpy")
        return
        
    print('=' * 70)
    print('[EXAMPLE] NumPy Integration Example')
    print('=' * 70)
    
    # Create the encryption parameters and context
    print('[DEBUG] Setting up encryption parameters')
    params = EncryptionParameters(SchemeType.CKKS)
    poly_modulus_degree = 8192
    params.set_poly_modulus_degree(poly_modulus_degree)
    params.set_coeff_modulus(CoeffModulus.Create(poly_modulus_degree, [40, 40, 40, 40]))
    context = SEALContext(params)
    
    # Generate keys
    print('[DEBUG] Generating keys')
    keygen = KeyGenerator(context)
    public_key = keygen.create_public_key()  # Note: using the specific API for this binding
    secret_key = keygen.secret_key()
    
    # Create encrytor, evaluator, and decryptor
    encryptor = Encryptor(context, public_key)
    evaluator = Evaluator(context)
    decryptor = Decryptor(context, secret_key)
    
    # Create encoder
    encoder = CKKSEncoder(context)
    slot_count = encoder.slot_count()
    print(f'[DEBUG] Number of slots: {slot_count}')
    
    # Create a NumPy array with test data
    print('[DEBUG] Creating NumPy array with test data')
    scale = 2.0**40
    
    # Create some test data
    input_data = np.array([3.1415, 2.7182, 1.4142, 1.7320, 2.2360, 2.6457])
    print(f'[DEBUG] Input data: {input_data}')
    
    # Create a full array padded with zeros
    padded_data = np.zeros(slot_count)
    padded_data[:len(input_data)] = input_data
    
    # Method 1: Encode directly from NumPy array
    print('[DEBUG] Encoding using encode_new_numpy method')
    plaintext = encoder.encode_new_numpy(padded_data, scale)
    
    # Encrypt
    print('[DEBUG] Encrypting')
    serializable_ct = encryptor.encrypt(plaintext)
    
    # Convert to Ciphertext for Evaluator operations
    print('[DEBUG] Converting SerializableCiphertext to Ciphertext')
    ciphertext = convert_to_ciphertext(serializable_ct, context)
    
    # Perform a simple operation (square the values)
    print('[DEBUG] Squaring the encrypted values')
    evaluator.square_inplace(ciphertext)
    evaluator.relinearize_inplace(ciphertext, keygen.create_relin_keys())
    
    # Use destination parameter for rescale_to_next
    rescaled_cipher = Ciphertext()
    evaluator.rescale_to_next(ciphertext, rescaled_cipher)
    ciphertext = rescaled_cipher  # Update ciphertext to use the rescaled version
    
    # Decrypt
    print('[DEBUG] Decrypting')
    # decrypted = decryptor.decrypt(ciphertext)
    
    # Decode
    print('[DEBUG] Decoding')
    result = decrypt_and_decode(ciphertext, decryptor, encoder)

    # Check results
    print('[DEBUG] Original values:', input_data)
    print('[DEBUG] Squared values (decrypted):', result[:len(input_data)])
    print('[DEBUG] Expected squared values:', input_data ** 2)
    print('[DEBUG] Absolute error:', np.abs(result[:len(input_data)] - input_data ** 2))
    
    # Method 2: Convert ciphertext to NumPy array
    print('\n[DEBUG] Converting ciphertext to NumPy array')
    cipher_array = ciphertext.to_array()
    print(f'[DEBUG] Ciphertext array shape: {cipher_array.shape}')
    
    # Method 3: Get zero-copy view of ciphertext
    print('\n[DEBUG] Getting zero-copy view of ciphertext')
    view = ciphertext.to_array_view()
    print(f'[DEBUG] View shape: {view.shape}')
    
    # Method 4: Batch operations
    print('\n[DEBUG] Testing batch operations')
    serializable_ciphertexts = [encryptor.encrypt(encoder.encode_new_numpy(np.ones(slot_count) * i, scale)) 
                               for i in range(3)]
    
    # Convert for batch operations
    ciphertexts = [convert_to_ciphertext(ct, context) for ct in serializable_ciphertexts]
    
    # Save to file
    print('[DEBUG] Saving ciphertexts in batch')
    Ciphertext.batch_save(ciphertexts, 'numpy_test_batch.bin')
    
    # Load from file
    print('[DEBUG] Loading ciphertexts in batch')
    loaded = Ciphertext.batch_load(context, 'numpy_test_batch.bin')
    print(f'[DEBUG] Loaded {len(loaded)} ciphertexts')
    
    # Verify the loaded data
    for i, ct in enumerate(loaded):
        result = decrypt_and_decode(ct, decryptor, encoder)
        print(f'[DEBUG] Ciphertext {i} contains: {result[0]}')
    
    print('[DEBUG] NumPy integration example completed successfully')
    print('=' * 70)

def decrypt_and_decode(cipher, decryptor, encoder, num_results=10, use_complex=False):
    """Helper function to decrypt and decode a ciphertext, reducing code duplication.
    
    Args:
        cipher: The ciphertext to decrypt
        decryptor: Decryptor object
        encoder: CKKSEncoder object
        num_results: Number of results to return (default: 10)
        use_complex: Whether to use decode_complex instead of decode (default: False)
        
    Returns:
        list: Decoded values
    """
    # Create plaintext for results
    plain_result = Plaintext()
    
    # Decrypt the ciphertext
    decryptor.decrypt(cipher, plain_result)
    
    # Decode the plaintext - use the correct available method
    if use_complex and hasattr(encoder, "decode_complex"):
        decoded_values = encoder.decode_complex(plain_result)
    else:
        decoded_values = encoder.decode(plain_result)
    
    # Return the specified number of results
    return decoded_values[:num_results]

if __name__ == "__main__":
    serialization_example()
    pickle_example()
    evaluator_example()
    key_serialization_example()
    exception_handling_example()
    ckks_rotation_example()
    ckks_rescale_modswitch_example()
    ckks_conjugation_example()
    numpy_integration_example()
    print('All examples completed successfully.')