# Advanced API Documentation

This document provides detailed information about the advanced features and high-level API introduced in SEAL-Python 4.1.5.

## Table of Contents

- [High-Level Helper Classes](#high-level-helper-classes)
- [Utility Functions](#utility-functions)
- [Advanced Usage Patterns](#advanced-usage-patterns)
- [Performance Considerations](#performance-considerations)
- [Error Handling](#error-handling)

## High-Level Helper Classes

### CKKSHelper

The `CKKSHelper` class provides a simplified interface for CKKS (Cheon-Kim-Kim-Song) scheme operations on floating-point numbers.

#### Initialization

```python
import seal

helper = seal.CKKSHelper(
    poly_modulus_degree=8192,      # Polynomial modulus degree (power of 2)
    coeff_modulus_bits=None,        # Coefficient modulus bit lengths (auto if None)
    scale_bits=40                   # Scale for encoding (typically 30-60)
)
```

**Parameters:**
- `poly_modulus_degree`: Controls security and performance. Common values: 4096, 8192, 16384
- `coeff_modulus_bits`: List of bit lengths for coefficient modulus chain. If None, uses sensible defaults
- `scale_bits`: Precision for encoding. Higher = more precision but slower

#### Methods

##### encrypt(value)

Encrypt a floating-point value or array.

```python
# Single value
encrypted = helper.encrypt(3.14)

# Array/vector
encrypted_vec = helper.encrypt([1.0, 2.0, 3.0, 4.0])

# NumPy array
import numpy as np
encrypted_np = helper.encrypt(np.array([1.5, 2.5, 3.5]))
```

**Parameters:**
- `value`: float, list of floats, or NumPy array

**Returns:**
- `seal.Ciphertext`: Encrypted ciphertext

##### decrypt(encrypted)

Decrypt a ciphertext back to plaintext.

```python
result = helper.decrypt(encrypted)
```

**Parameters:**
- `encrypted`: `seal.Ciphertext` to decrypt

**Returns:**
- `float` or `list[float]`: Decrypted value(s)

##### add(encrypted1, encrypted2)

Homomorphically add two encrypted values.

```python
encrypted_sum = helper.add(encrypted_x, encrypted_y)
```

**Parameters:**
- `encrypted1`, `encrypted2`: `seal.Ciphertext` objects

**Returns:**
- `seal.Ciphertext`: Result of addition

##### multiply(encrypted1, encrypted2)

Homomorphically multiply two encrypted values.

```python
encrypted_product = helper.multiply(encrypted_a, encrypted_b)
```

**Parameters:**
- `encrypted1`, `encrypted2`: `seal.Ciphertext` objects

**Returns:**
- `seal.Ciphertext`: Result of multiplication

**Note:** Automatically handles relinearization and rescaling.

##### negate(encrypted)

Negate an encrypted value.

```python
encrypted_neg = helper.negate(encrypted_value)
```

##### square(encrypted)

Square an encrypted value.

```python
encrypted_sq = helper.square(encrypted_value)
```

#### Example: Computing a Polynomial

```python
import seal

helper = seal.CKKSHelper()

# Compute f(x) = 2x^2 + 3x + 1 for x = 5.0
x = 5.0
encrypted_x = helper.encrypt(x)

# 2x^2
encrypted_x_sq = helper.square(encrypted_x)
encrypted_2 = helper.encrypt(2.0)
encrypted_2x_sq = helper.multiply(encrypted_2, encrypted_x_sq)

# 3x
encrypted_3 = helper.encrypt(3.0)
encrypted_3x = helper.multiply(encrypted_3, encrypted_x)

# 2x^2 + 3x
encrypted_sum1 = helper.add(encrypted_2x_sq, encrypted_3x)

# 2x^2 + 3x + 1
encrypted_1 = helper.encrypt(1.0)
encrypted_result = helper.add(encrypted_sum1, encrypted_1)

result = helper.decrypt(encrypted_result)
expected = 2 * x**2 + 3 * x + 1
print(f"Result: {result}, Expected: {expected}")
```

### BFVHelper

The `BFVHelper` class provides a simplified interface for BFV (Brakerski/Fan-Vercauteren) scheme operations on integers.

#### Initialization

```python
import seal

helper = seal.BFVHelper(
    poly_modulus_degree=4096,    # Polynomial modulus degree
    plain_modulus_bits=20         # Plaintext modulus bit length
)
```

**Parameters:**
- `poly_modulus_degree`: Determines batch size (slots) and security
- `plain_modulus_bits`: Size of plaintext space (affects maximum values)

#### Properties

- `slot_count`: Number of available SIMD slots (read-only)

```python
print(f"Available slots: {helper.slot_count}")
```

#### Methods

Methods are similar to `CKKSHelper` but work with integers:

##### encrypt(values)

```python
# Single integer (auto-padded to slot_count)
encrypted = helper.encrypt(42)

# Integer vector
encrypted_vec = helper.encrypt([1, 2, 3, 4, 5])
```

##### decrypt(encrypted)

```python
result = helper.decrypt(encrypted)  # Returns list of integers
```

##### add, multiply, negate

Same interface as CKKSHelper but for integer arithmetic.

#### Example: SIMD Batch Processing

```python
import seal

helper = seal.BFVHelper(poly_modulus_degree=4096)

# Encrypt two batches
batch1 = list(range(1, 101))      # [1, 2, 3, ..., 100]
batch2 = list(range(100, 0, -1))   # [100, 99, 98, ..., 1]

encrypted1 = helper.encrypt(batch1)
encrypted2 = helper.encrypt(batch2)

# Single operation computes 100 additions simultaneously!
encrypted_sum = helper.add(encrypted1, encrypted2)

result = helper.decrypt(encrypted_sum)
print(f"All results are 101: {all(r == 101 for r in result[:100])}")
```

## Utility Functions

### create_ckks_params(poly_modulus_degree, coeff_modulus_bits)

Create CKKS encryption parameters with defaults.

```python
import seal

params = seal.create_ckks_params(
    poly_modulus_degree=8192,
    coeff_modulus_bits=[60, 40, 40, 60]  # Optional
)
context = seal.SEALContext(params)
```

### create_bfv_params(poly_modulus_degree, plain_modulus_bits)

Create BFV encryption parameters with defaults.

```python
params = seal.create_bfv_params(
    poly_modulus_degree=4096,
    plain_modulus_bits=20
)
context = seal.SEALContext(params)
```

### serialize_to_bytes(obj)

Serialize SEAL objects to bytes.

```python
data = seal.serialize_to_bytes(ciphertext)
# Save to file
with open('encrypted.bin', 'wb') as f:
    f.write(data)
```

### deserialize_from_bytes(data, obj_type)

Deserialize SEAL objects from bytes.

```python
with open('encrypted.bin', 'rb') as f:
    data = f.read()
ciphertext = seal.deserialize_from_bytes(data, seal.Ciphertext)
```

## Advanced Usage Patterns

### Pattern 1: Secure Multi-Party Computation

```python
import seal

# Party A creates encryption context
helper = seal.CKKSHelper()

# Party A encrypts their data
encrypted_a = helper.encrypt(10.5)

# Share encrypted_a with Party B (safe to transmit)
# Party B can perform operations without decrypting
encrypted_b = helper.encrypt(5.2)
encrypted_sum = helper.add(encrypted_a, encrypted_b)

# Only Party A (with secret key) can decrypt
result = helper.decrypt(encrypted_sum)
```

### Pattern 2: Privacy-Preserving Machine Learning

```python
import seal
import numpy as np

helper = seal.CKKSHelper(poly_modulus_degree=8192)

# Encrypt model weights
weights = np.array([0.5, -0.3, 0.8, 0.1])
encrypted_weights = [helper.encrypt(w) for w in weights]

# Encrypt user data
features = np.array([1.0, 2.0, 3.0, 4.0])
encrypted_features = [helper.encrypt(f) for f in features]

# Compute dot product on encrypted data
products = [helper.multiply(encrypted_weights[i], encrypted_features[i])
            for i in range(len(weights))]

# Sum all products
result = products[0]
for p in products[1:]:
    result = helper.add(result, p)

# Decrypt final prediction
prediction = helper.decrypt(result)
expected = np.dot(weights, features)
print(f"Encrypted prediction: {prediction:.4f}, Expected: {expected:.4f}")
```

### Pattern 3: Database Queries on Encrypted Data

```python
import seal

helper = seal.BFVHelper()

# Encrypted database of ages
ages = [25, 30, 35, 40, 45, 50, 55, 60]
encrypted_ages = [helper.encrypt(age) for age in ages]

# Query: add 5 years to all ages (birthday updates)
encrypted_5 = helper.encrypt(5)
updated_ages = [helper.add(enc_age, encrypted_5) for enc_age in encrypted_ages]

# Decrypt results
results = [helper.decrypt(enc)[0] for enc in updated_ages]
print(f"Updated ages: {results}")
```

## Performance Considerations

### Parameter Selection

**poly_modulus_degree** impacts:
- **Security**: Higher = more secure
- **Performance**: Higher = slower operations
- **Batch size**: Determines number of SIMD slots
- **Noise budget**: Higher = more operations before noise overflow

**Recommended values:**
- `4096`: Fast, suitable for testing or low-security scenarios
- `8192`: Good balance for most applications
- `16384`: High security, slower but supports many operations

### Noise Budget Management

Each homomorphic operation consumes "noise budget". When exhausted, decryption fails.

```python
# Check noise budget (low-level API)
import seal

helper = seal.CKKSHelper()
encrypted = helper.encrypt(5.0)

# After operations, noise budget decreases
# Multiplication consumes more noise than addition

# Rescaling helps manage noise in CKKS
# (automatically done by CKKSHelper.multiply)
```

### Optimization Tips

1. **Batch operations**: Use vectors instead of single values
2. **Minimize multiplications**: They're expensive and consume noise
3. **Use addition when possible**: Much faster than multiplication
4. **Relinearization**: Keep ciphertext size small (auto in helpers)
5. **Rescaling (CKKS)**: Manage scale and noise (auto in helpers)

## Error Handling

### Common Errors

**ImportError: SEAL extension not available**
```python
import seal

if not hasattr(seal, 'SEALContext'):
    print("SEAL extension not built. Run ./build.sh")
```

**Noise budget exhausted**
```python
# Use higher poly_modulus_degree or fewer operations
helper = seal.CKKSHelper(poly_modulus_degree=16384)
```

**Type mismatch**
```python
# CKKS is for floats, BFV is for integers
ckks_helper = seal.CKKSHelper()
# ckks_helper.encrypt(42)  # Works but converts to float

bfv_helper = seal.BFVHelper()
# bfv_helper.encrypt(3.14)  # Error: expects integers
```

### Best Practices

1. **Always use try-except** for encryption operations
2. **Validate inputs** before encryption
3. **Check parameter compatibility** when loading serialized data
4. **Monitor noise budget** for long computation chains
5. **Test with small parameters** first, then scale up

## Examples Repository

Complete working examples are in the `python/` directory:

- `highlevel_ckks_example.py`: CKKS demonstrations
- `highlevel_bfv_example.py`: BFV demonstrations
- `test_numpy_integration.py`: NumPy integration
- `basic_example.py`: Low-level API usage

## See Also

- [NumPy Integration Guide](numpy_integration.md)
- [Quick Reference Guide](quick_reference.md)
- [Microsoft SEAL Documentation](https://github.com/microsoft/SEAL)

---

For questions or issues, please visit the [GitHub repository](https://github.com/chandradutt5746/SEAL-PYTHON-4.1.5).
