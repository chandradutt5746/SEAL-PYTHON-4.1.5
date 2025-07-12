# SEAL-Python Quick Reference Guide

This guide provides quick reference examples for common operations with the SEAL-Python binding. It covers the key API features and highlights important details for correctly using the binding.

## Core API Features

### Encryption and Decryption Workflow

```python
import seal
import numpy as np
import os

# Setup encryption parameters
params = seal.EncryptionParameters(seal.SchemeType.CKKS)
poly_modulus_degree = 8192
params.set_poly_modulus_degree(poly_modulus_degree)
params.set_coeff_modulus(seal.CoeffModulus.Create(poly_modulus_degree, [40, 40, 40, 40]))
context = seal.SEALContext(params)

# Generate keys
keygen = seal.KeyGenerator(context)
public_key = keygen.create_public_key()  # Note: This binding uses create_public_key()
secret_key = keygen.secret_key()

# Create cryptography objects
encryptor = seal.Encryptor(context, public_key)
decryptor = seal.Decryptor(context, secret_key)
evaluator = seal.Evaluator(context)
encoder = seal.CKKSEncoder(context)

# Encode data
scale = 2.0**40
data = np.array([1.0, 2.0, 3.0, 4.0])
plaintext = encoder.encode_new_numpy(data, scale)

# Encrypt (produces a SerializableCiphertext)
serializable_cipher = encryptor.encrypt(plaintext)

# ⚠️ Important: Converting SerializableCiphertext to Ciphertext for operations/decryption
temp_file = "temp_cipher.bin"
serializable_cipher.save(temp_file)
cipher = seal.Ciphertext()
cipher.load(context, temp_file)
os.remove(temp_file)  # Clean up

# Perform operations (requires Ciphertext)
result_cipher = seal.Ciphertext()
evaluator.add(cipher, cipher, result_cipher)  # Double the values

# Decrypt (requires Ciphertext)
result_plaintext = seal.Plaintext()
decryptor.decrypt(result_cipher, result_plaintext)

# Decode
result = encoder.decode(result_plaintext)
print(result[:4])  # Should be approximately [2.0, 4.0, 6.0, 8.0]
```

## NumPy Integration

### Direct Encoding from NumPy Arrays

```python
# Create and pad a NumPy array
data = np.array([1.0, 2.0, 3.0, 4.0])
slot_count = encoder.slot_count()
padded_data = np.zeros(slot_count)
padded_data[:len(data)] = data

# Encode the NumPy array directly
plaintext = encoder.encode_new_numpy(padded_data, scale)
```

### Converting Ciphertext to NumPy Arrays

```python
# Get a NumPy array representation of a ciphertext
cipher_array = cipher.to_array()
print(f"Ciphertext shape: {cipher_array.shape}")
```

### Zero-Copy Views (if supported)

```python
try:
    # Get a view that shares memory with the ciphertext (no copying)
    view = cipher.to_array_view()
    print(f"View shape: {view.shape}")
    # Warning: Modifying this view directly modifies the ciphertext data!
except AttributeError:
    print("to_array_view() is not supported in this binding")
```

## Batch Operations

### Saving and Loading Multiple Ciphertexts

```python
# Save multiple ciphertexts to individual files
for i, cipher in enumerate(ciphertexts):
    cipher_file = f"ciphertext_{i}.bin"
    cipher.save(cipher_file)

# Load multiple ciphertexts from files
loaded_ciphertexts = []
for i in range(len(ciphertexts)):
    cipher_file = f"ciphertext_{i}.bin"
    loaded_cipher = seal.Ciphertext()
    loaded_cipher.load(context, cipher_file)
    loaded_ciphertexts.append(loaded_cipher)
    os.remove(cipher_file)  # Clean up
```

## Common Pitfalls and Solutions

1. **TypeError with decrypt**: If you get `TypeError: decrypt(): incompatible function arguments`, it means you're trying to decrypt a `SerializableCiphertext` instead of a `Ciphertext`. Use the conversion method shown above.

2. **TypeError with evaluator methods**: Operations like `evaluator.add()` require `Ciphertext` objects, not `SerializableCiphertext`. Always convert encrypted results to `Ciphertext` before performing operations.

3. **Shape mismatch**: When encoding NumPy arrays, make sure the array size matches the slot count or is properly padded.

4. **Parameter mismatch**: Use consistent encryption parameters throughout your code. Mixing parameters can lead to cryptographic errors.

## Performance Tips

1. **Pre-allocate ciphertexts** when performing many operations to reduce memory allocation overhead.

2. **Batch operations** when working with multiple ciphertexts for better performance.

3. **Use direct NumPy encoding** rather than converting lists to NumPy arrays and then encoding.

4. **Zero-copy views** can provide performance benefits for advanced users, but use with caution.

## Further Resources

- Full API documentation in the README.md file
- Example scripts in the `/python` directory
- NumPy integration details in the `docs/numpy_integration.md` file
