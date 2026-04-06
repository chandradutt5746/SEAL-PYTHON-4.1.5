"""
Example demonstrating advanced features of SEAL-Python.

This script showcases:
- Context managers for automatic resource cleanup
- Batch processing for multiple values
- Performance monitoring
- Key management
- Common computation patterns (polynomial evaluation, matrix operations)
"""

import seal
import numpy as np


def demo_context_manager():
    """Demonstrate context manager usage."""
    print("=" * 70)
    print("1. Context Manager Demo")
    print("=" * 70)

    # Use context manager for automatic cleanup
    with seal.SEALContext(scheme='ckks', poly_modulus_degree=8192) as helper:
        # Operations within context
        encrypted_x = helper.encrypt(10.5)
        encrypted_y = helper.encrypt(5.2)
        encrypted_sum = helper.add(encrypted_x, encrypted_y)
        result = helper.decrypt(encrypted_sum)

        print(f"Result using context manager: {result}")
        print("Resources cleaned up automatically!\n")


def demo_batch_processing():
    """Demonstrate batch processing."""
    print("=" * 70)
    print("2. Batch Processing Demo")
    print("=" * 70)

    helper = seal.CKKSHelper(poly_modulus_degree=8192)
    processor = seal.BatchProcessor(helper)

    # Encrypt a batch of values
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    print(f"Original values: {values}")

    encrypted_batch = processor.encrypt_batch(values)
    print(f"Encrypted {len(encrypted_batch)} values")

    # Decrypt batch
    decrypted = processor.decrypt_batch(encrypted_batch)
    print(f"Decrypted values: {[f'{v:.2f}' for v in decrypted]}")

    # Batch operations
    encrypted_batch2 = processor.encrypt_batch([10, 20, 30, 40, 50])
    encrypted_sum_batch = processor.add_batch(encrypted_batch, encrypted_batch2)
    sum_results = processor.decrypt_batch(encrypted_sum_batch)
    print(f"Sum of batches: {[f'{v:.2f}' for v in sum_results]}\n")


def demo_performance_monitoring():
    """Demonstrate performance monitoring."""
    print("=" * 70)
    print("3. Performance Monitoring Demo")
    print("=" * 70)

    helper = seal.CKKSHelper(poly_modulus_degree=8192)
    monitor = seal.PerformanceMonitor()

    # Measure encryption
    with monitor.measure("encryption"):
        encrypted = helper.encrypt(42.0)

    # Measure decryption
    with monitor.measure("decryption"):
        result = helper.decrypt(encrypted)

    # Measure multiplication (multiple times)
    for i in range(5):
        with monitor.measure("multiplication"):
            enc1 = helper.encrypt(2.0)
            enc2 = helper.encrypt(3.0)
            _ = helper.multiply(enc1, enc2)

    # Get statistics
    stats = monitor.get_stats()
    print("\nPerformance Statistics:")
    for operation, metrics in stats.items():
        print(f"\n{operation}:")
        print(f"  Count: {metrics['count']}")
        print(f"  Average: {metrics['avg']*1000:.2f} ms")
        print(f"  Min: {metrics['min']*1000:.2f} ms")
        print(f"  Max: {metrics['max']*1000:.2f} ms")
    print()


def demo_key_management():
    """Demonstrate key management."""
    print("=" * 70)
    print("4. Key Management Demo")
    print("=" * 70)

    import os
    import tempfile

    helper = seal.CKKSHelper(poly_modulus_degree=4096)
    manager = seal.KeyManager(helper)

    # Create temporary directory for keys
    with tempfile.TemporaryDirectory() as tmpdir:
        key_dir = os.path.join(tmpdir, "keys")

        # Save keys
        manager.save_keys(key_dir)
        print(f"Keys saved to {key_dir}")
        print(f"Files: {os.listdir(key_dir)}")

        # Create new helper and load keys
        new_helper = seal.CKKSHelper(poly_modulus_degree=4096)
        new_manager = seal.KeyManager(new_helper)
        new_manager.load_keys(key_dir)
        print("Keys loaded successfully!\n")


def demo_polynomial_evaluation():
    """Demonstrate polynomial evaluation."""
    print("=" * 70)
    print("5. Polynomial Evaluation Demo")
    print("=" * 70)

    helper = seal.CKKSHelper(poly_modulus_degree=8192)

    # Evaluate f(x) = 2x^2 + 3x + 1 at x = 5
    x = 5.0
    coefficients = [1, 3, 2]  # [a_0, a_1, a_2]

    print(f"Polynomial: f(x) = 2x² + 3x + 1")
    print(f"Evaluating at x = {x}")

    # Encrypt x
    encrypted_x = helper.encrypt(x)

    # Evaluate polynomial on encrypted data
    encrypted_result = seal.polynomial_evaluation(helper, coefficients, encrypted_x)

    # Decrypt result
    result = helper.decrypt(encrypted_result)
    expected = 2 * x**2 + 3 * x + 1

    print(f"Encrypted result: {result:.2f}")
    print(f"Expected result: {expected:.2f}")
    print(f"Error: {abs(result - expected):.6f}\n")


def demo_matrix_vector_multiply():
    """Demonstrate matrix-vector multiplication."""
    print("=" * 70)
    print("6. Matrix-Vector Multiplication Demo")
    print("=" * 70)

    helper = seal.CKKSHelper(poly_modulus_degree=8192)

    # Define matrix and vector
    matrix = [
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0]
    ]
    vector = [1.0, 2.0, 3.0]

    print("Matrix:")
    for row in matrix:
        print(f"  {row}")
    print(f"Vector: {vector}")

    # Encrypt vector
    encrypted_vector = [helper.encrypt(v) for v in vector]

    # Multiply
    encrypted_result = seal.matrix_vector_multiply(helper, matrix, encrypted_vector)

    # Decrypt result
    result = [helper.decrypt(enc) for enc in encrypted_result]

    # Calculate expected result
    expected = [sum(m * v for m, v in zip(row, vector)) for row in matrix]

    print(f"\nEncrypted result: {[f'{r:.2f}' for r in result]}")
    print(f"Expected result: {expected}")
    print()


def demo_dot_product():
    """Demonstrate dot product of encrypted vectors."""
    print("=" * 70)
    print("7. Dot Product Demo")
    print("=" * 70)

    helper = seal.CKKSHelper(poly_modulus_degree=8192)

    vec1 = [1.0, 2.0, 3.0, 4.0]
    vec2 = [5.0, 6.0, 7.0, 8.0]

    print(f"Vector 1: {vec1}")
    print(f"Vector 2: {vec2}")

    # Encrypt both vectors
    encrypted_vec1 = [helper.encrypt(v) for v in vec1]
    encrypted_vec2 = [helper.encrypt(v) for v in vec2]

    # Compute dot product on encrypted data
    encrypted_result = seal.dot_product(helper, encrypted_vec1, encrypted_vec2)

    # Decrypt
    result = helper.decrypt(encrypted_result)
    expected = sum(a * b for a, b in zip(vec1, vec2))

    print(f"\nEncrypted dot product: {result:.2f}")
    print(f"Expected: {expected:.2f}")
    print(f"Error: {abs(result - expected):.6f}\n")


def demo_performance_decorator():
    """Demonstrate performance measurement decorator."""
    print("=" * 70)
    print("8. Performance Decorator Demo")
    print("=" * 70)

    helper = seal.CKKSHelper(poly_modulus_degree=8192)

    @seal.measure_performance
    def encrypt_and_process(helper, values):
        """Sample function to measure."""
        encrypted = [helper.encrypt(v) for v in values]
        result = encrypted[0]
        for enc in encrypted[1:]:
            result = helper.add(result, enc)
        return helper.decrypt(result)

    values = list(range(1, 11))
    result = encrypt_and_process(helper, values)
    print(f"Sum of {values} = {result:.2f}\n")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("SEAL-Python Advanced Features Demo")
    print("=" * 70 + "\n")

    try:
        demo_context_manager()
        demo_batch_processing()
        demo_performance_monitoring()
        demo_key_management()
        demo_polynomial_evaluation()
        demo_matrix_vector_multiply()
        demo_dot_product()
        demo_performance_decorator()

        print("=" * 70)
        print("All demos completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
