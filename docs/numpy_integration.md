# NumPy Integration in SEAL-Python

This document explains how to use the NumPy integration features in SEAL-Python to achieve higher performance when working with Microsoft SEAL.

## Overview

SEAL-Python provides several optimized methods for interacting with NumPy arrays:

1. **Direct encoding from NumPy arrays** - Encode NumPy arrays directly into plaintexts
2. **Converting ciphertexts to NumPy arrays** - Convert ciphertext data to NumPy arrays for analysis
3. **Zero-copy views of ciphertext data** - Get direct access to ciphertext memory without copying
4. **Direct ciphertext creation from NumPy arrays** - Create ciphertexts from raw NumPy data (advanced)
5. **Batch operations with ciphertexts** - Save/load multiple ciphertexts efficiently

## 1. Direct Encoding from NumPy Arrays

The `CKKSEncoder` class provides a method specifically for NumPy arrays:

```python
import numpy as np
import seal

# Create a NumPy array
data = np.array([1.0, 2.0, 3.0, 4.0])

# Create encoder
context = seal.SEALContext(params)  # params initialized earlier
encoder = seal.CKKSEncoder(context)

# Encode directly from NumPy array
scale = 2.0**40
plaintext = encoder.encode_new_numpy(data, scale)

# Generate keys
keygen = seal.KeyGenerator(context)
public_key = keygen.create_public_key()  # Note: create_public_key() is used in this binding
secret_key = keygen.secret_key()

# Create an encryptor
encryptor = seal.Encryptor(context, public_key)

# Encryption - returns a ciphertext in this binding
ciphertext = encryptor.encrypt(plaintext)

# Decryption - returns a plaintext in this binding
decryptor = seal.Decryptor(context, secret_key)
decrypted = decryptor.decrypt(ciphertext)
result = encoder.decode(decrypted)
```

Benefits:
- Avoids converting NumPy arrays to Python lists
- Optimized memory handling
- Significantly faster for large arrays

## 2. Converting Ciphertexts to NumPy Arrays

Extract ciphertext data as NumPy arrays for analysis:

```python
# Get a NumPy array representation of the ciphertext
cipher_array = ciphertext.to_array()

print(f"Shape: {cipher_array.shape}")
print(f"Data type: {cipher_array.dtype}")  # uint64
```

This method creates a copy of the ciphertext data as a NumPy array. It's useful for:
- Analyzing ciphertext structure
- Saving ciphertexts in NumPy format
- Custom post-processing

## 3. Zero-Copy Views of Ciphertext Data

For high-performance scenarios, get direct access to the ciphertext memory:

```python
# Get a direct view of the ciphertext memory (no copy)
view = ciphertext.to_array_view()
```

**Warning**: This method creates a view that shares memory with the original ciphertext. Any modifications to the view will directly modify the ciphertext data, which can corrupt the ciphertext if not used carefully.

Benefits:
- No memory copying
- Extremely fast access to ciphertext data
- Useful for advanced users who need maximum performance

## 4. Direct Ciphertext Creation from NumPy Arrays

Advanced users can create ciphertexts directly from NumPy arrays:

```python
# Create a ciphertext directly from a NumPy array
# Note: This is an advanced feature - the array must be properly formatted
custom_cipher = seal.Ciphertext(
    context,               # SEALContext
    data_array,           # NumPy array of uint64 values
    poly_count,           # Number of polynomials
    coeff_mod_count,      # Number of coefficient moduli
    poly_mod_degree,      # Polynomial modulus degree
    scale                 # Scale for CKKS
)
```

This is an advanced feature for users who need to construct ciphertexts from raw data. Typically, you would:
1. First create a normal ciphertext to understand its structure
2. Extract the parameters (poly_count, coeff_mod_count, etc.)
3. Prepare a NumPy array with the correct structure
4. Create a new ciphertext directly from the array

## 5. Batch Operations with Multiple Ciphertexts

Efficient operations with multiple ciphertexts:

```python
# Pre-allocate multiple ciphertexts (more efficient)
count = 10
ciphertexts = seal.Ciphertext.create_preallocated(context, count)

# Save multiple ciphertexts to a single file
seal.Ciphertext.batch_save(ciphertexts, "ciphertexts.bin")

# Load multiple ciphertexts from a file
loaded_ciphertexts = seal.Ciphertext.batch_load(context, "ciphertexts.bin")
```

Benefits:
- Reduced overhead when working with many ciphertexts
- More efficient I/O operations
- Better memory management

## Important Note on SerializableCiphertext vs Ciphertext

In this SEAL-Python binding, `encryptor.encrypt()` returns a `SerializableCiphertext` object, while the `decryptor.decrypt()` method requires a `Ciphertext` object. This is an important distinction to understand when working with the API.

### Converting Between Types

When you need to decrypt data, you must convert from `SerializableCiphertext` to `Ciphertext`. The recommended way to do this is through serialization:

```python
# Encrypt (returns a SerializableCiphertext)
serializable_cipher = encryptor.encrypt(plaintext)

# Convert to Ciphertext via serialization
temp_file = "temp_cipher.bin"
serializable_cipher.save(temp_file)
cipher = seal.Ciphertext()
cipher.load(context, temp_file)

# Now you can decrypt
plaintext_result = seal.Plaintext()
decryptor.decrypt(cipher, plaintext_result)

# Clean up
if os.path.exists(temp_file):
    os.remove(temp_file)
```

This conversion pattern is necessary whenever you need to decrypt data in this binding.

## Performance Considerations

1. **Memory Management**: NumPy integration significantly reduces memory copying between C++ and Python.
2. **Array Dimensions**: Make sure your NumPy arrays have the correct size and type (typically `np.float64` for input, `np.uint64` for raw ciphertext data).
3. **Zero-Copy Views**: Use with caution, as they share memory with the original ciphertext.
4. **Batch Operations**: Pre-allocating ciphertexts can be much faster than creating them individually.

## Example Workflow

A typical high-performance workflow might look like:

```python
import numpy as np
import seal

# Set up encryption parameters and context
# (see other examples)

# Create a large dataset
data_size = 8192
data = np.random.random(data_size)

# Encode using the NumPy-optimized method
plaintext = encoder.encode_new_numpy(data, scale)

# Encrypt the data
ciphertext = encryptor.encrypt(plaintext)

# Perform operations
# ...

# Convert result to NumPy array for analysis
result_array = decrypted_result.to_array()
```

For full examples, see the `numpy_quick_example.py` and `test_numpy_integration.py` files in the `python` directory.
