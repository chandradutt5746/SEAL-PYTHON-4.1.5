# Advanced Features Guide

This guide covers the advanced features in SEAL-Python 4.1.5 that make real-world homomorphic encryption applications easier to build.

## Table of Contents

- [Context Managers](#context-managers)
- [Batch Processing](#batch-processing)
- [Performance Monitoring](#performance-monitoring)
- [Key Management](#key-management)
- [Computation Patterns](#computation-patterns)
  - [Polynomial Evaluation](#polynomial-evaluation)
  - [Matrix-Vector Multiplication](#matrix-vector-multiplication)
  - [Dot Product](#dot-product)

## Context Managers

Use `SEALContext` (alias for `SEALContextManager`) for automatic resource cleanup:

```python
import seal

# Automatic resource management
with seal.SEALContext(scheme='ckks', poly_modulus_degree=8192) as helper:
    encrypted = helper.encrypt(42.0)
    result = helper.decrypt(encrypted)
# Resources automatically cleaned up here
```

**Benefits:**
- Automatic cleanup of internal metadata
- Cleaner code structure
- Exception-safe resource management

## Batch Processing

Process multiple values efficiently with `BatchProcessor`:

```python
import seal

helper = seal.CKKSHelper()
processor = seal.BatchProcessor(helper)

# Encrypt multiple values at once
values = [1.0, 2.0, 3.0, 4.0, 5.0]
encrypted_batch = processor.encrypt_batch(values)

# Batch operations
encrypted_batch2 = processor.encrypt_batch([10, 20, 30, 40, 50])
encrypted_sums = processor.add_batch(encrypted_batch, encrypted_batch2)

# Decrypt batch
results = processor.decrypt_batch(encrypted_sums)
```

**Methods:**
- `encrypt_batch(values)` - Encrypt multiple values
- `decrypt_batch(ciphertexts)` - Decrypt multiple ciphertexts
- `add_batch(batch1, batch2)` - Element-wise addition
- `multiply_batch(batch1, batch2)` - Element-wise multiplication

## Performance Monitoring

Track performance of homomorphic operations with `PerformanceMonitor`:

```python
import seal

helper = seal.CKKSHelper()
monitor = seal.PerformanceMonitor()

# Measure specific operations
with monitor.measure("encryption"):
    encrypted = helper.encrypt(42.0)

with monitor.measure("multiplication"):
    enc1 = helper.encrypt(2.0)
    enc2 = helper.encrypt(3.0)
    result = helper.multiply(enc1, enc2)

# Get statistics
stats = monitor.get_stats()
for operation, metrics in stats.items():
    print(f"{operation}: avg={metrics['avg']*1000:.2f}ms")

# Or use the decorator
@seal.measure_performance
def my_encryption_function(data):
    return helper.encrypt(data)
```

**Metrics Tracked:**
- Count of operations
- Total time
- Average time
- Min/max times

## Key Management

Save and load encryption keys with `KeyManager`:

```python
import seal

helper = seal.CKKSHelper()
manager = seal.KeyManager(helper)

# Save all keys to a directory
manager.save_keys("./keys")

# Later, load keys into a new helper
new_helper = seal.CKKSHelper()
new_manager = seal.KeyManager(new_helper)
new_manager.load_keys("./keys")
```

**Saved Keys:**
- Public key (`public_key.bin`)
- Secret key (`secret_key.bin`)
- Relinearization keys (`relin_keys.bin`)

**Use Cases:**
- Distributed systems (share public key)
- Key rotation
- Backup and recovery

## Computation Patterns

### Polynomial Evaluation

Evaluate polynomials on encrypted data using Horner's method:

```python
import seal

helper = seal.CKKSHelper()

# Evaluate f(x) = 3x² + 2x + 1 at x = 5
encrypted_x = helper.encrypt(5.0)
coefficients = [1, 2, 3]  # [a_0, a_1, a_2]

encrypted_result = seal.polynomial_evaluation(helper, coefficients, encrypted_x)
result = helper.decrypt(encrypted_result)  # ≈ 86
```

**Efficient:** Uses Horner's method to minimize multiplications

**Applications:**
- Activation functions in neural networks
- Statistical computations
- Approximating transcendental functions

### Matrix-Vector Multiplication

Multiply a plaintext matrix by an encrypted vector:

```python
import seal

helper = seal.CKKSHelper()

# Define plaintext matrix
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

# Encrypt vector
vector = [1.0, 2.0, 3.0]
encrypted_vector = [helper.encrypt(v) for v in vector]

# Multiply
encrypted_result = seal.matrix_vector_multiply(helper, matrix, encrypted_vector)

# Decrypt result
result = [helper.decrypt(enc) for enc in encrypted_result]
# result ≈ [14, 32, 50]
```

**Applications:**
- Linear regression predictions
- Image transformations
- Feature extraction

### Dot Product

Compute dot product of two encrypted vectors:

```python
import seal

helper = seal.CKKSHelper()

# Encrypt two vectors
vec1 = [helper.encrypt(1.0), helper.encrypt(2.0), helper.encrypt(3.0)]
vec2 = [helper.encrypt(4.0), helper.encrypt(5.0), helper.encrypt(6.0)]

# Compute dot product on encrypted data
encrypted_result = seal.dot_product(helper, vec1, vec2)
result = helper.decrypt(encrypted_result)  # ≈ 32
```

**Applications:**
- Cosine similarity
- Distance metrics
- Neural network layers

## Real-World Application Examples

### Private Machine Learning Inference

```python
import seal
import numpy as np

# Server has the model weights (plaintext)
model_weights = [[0.5, -0.3, 0.8], [0.2, 0.6, -0.4]]

# Client encrypts their data
helper = seal.CKKSHelper(poly_modulus_degree=8192)
user_data = [1.0, 2.0, 3.0]
encrypted_data = [helper.encrypt(v) for v in user_data]

# Server computes prediction on encrypted data
encrypted_predictions = seal.matrix_vector_multiply(
    helper, model_weights, encrypted_data
)

# Client decrypts the result
predictions = [helper.decrypt(enc) for enc in encrypted_predictions]
print(f"Private predictions: {predictions}")
```

### Secure Data Aggregation

```python
import seal

helper = seal.CKKSHelper()
processor = seal.BatchProcessor(helper)
monitor = seal.PerformanceMonitor()

# Multiple users encrypt their data
user_data = [
    [10, 20, 30],  # User 1
    [15, 25, 35],  # User 2
    [12, 22, 32],  # User 3
]

# Encrypt all user data
with monitor.measure("batch_encryption"):
    encrypted_batches = [processor.encrypt_batch(data) for data in user_data]

# Aggregate (sum) all encrypted data
encrypted_aggregate = encrypted_batches[0]
for batch in encrypted_batches[1:]:
    encrypted_aggregate = processor.add_batch(encrypted_aggregate, batch)

# Decrypt aggregated result
with monitor.measure("batch_decryption"):
    aggregate_result = processor.decrypt_batch(encrypted_aggregate)

print(f"Aggregate statistics: {aggregate_result}")
print(f"Performance: {monitor.get_stats()}")
```

### Encrypted Database Queries

```python
import seal

helper = seal.CKKSHelper()

# Encrypted database records (ages)
encrypted_db = [helper.encrypt(age) for age in [25, 30, 35, 40, 45]]

# Query: Add 5 years to all ages
encrypted_5 = helper.encrypt(5.0)
updated_ages = [helper.add(age, encrypted_5) for age in encrypted_db]

# Decrypt to verify
results = [helper.decrypt(enc) for enc in updated_ages]
print(f"Updated ages: {results}")
```

## Performance Tips

1. **Use Batch Processing**: Process multiple values together when possible
2. **Monitor Performance**: Identify bottlenecks with `PerformanceMonitor`
3. **Choose Appropriate Parameters**: Larger `poly_modulus_degree` = more security but slower
4. **Minimize Multiplications**: Each multiplication consumes noise budget
5. **Reuse Helpers**: Create helper objects once and reuse them

## Error Handling

```python
import seal

try:
    with seal.SEALContext(scheme='ckks') as helper:
        encrypted = helper.encrypt(42.0)
        result = helper.decrypt(encrypted)
except ImportError as e:
    print(f"SEAL extension not available: {e}")
except ValueError as e:
    print(f"Invalid parameters: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## See Also

- [Basic API Documentation](advanced_api.md)
- [NumPy Integration Guide](numpy_integration.md)
- [Quick Reference](quick_reference.md)
- [Example Scripts](../python/)

---

For questions or issues, visit the [GitHub repository](https://github.com/chandradutt5746/SEAL-PYTHON-4.1.5).
