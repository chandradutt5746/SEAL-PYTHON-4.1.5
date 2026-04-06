"""
Example demonstrating the high-level BFVHelper API.

This example shows how to use the new BFVHelper class for
simplified homomorphic encryption with BFV scheme (integer arithmetic).
"""

import seal


def main():
    print("=" * 70)
    print("SEAL-Python High-Level API Demo - BFV Scheme")
    print("=" * 70)

    # Create a BFV helper with default parameters
    print("\n[1] Initializing BFV helper...")
    helper = seal.BFVHelper(poly_modulus_degree=4096, plain_modulus_bits=20)
    print(f"    ✓ Context created and keys generated")
    print(f"    ✓ Available slots: {helper.slot_count}")

    # Example 1: Single value encryption
    print("\n[2] Single Value Encryption:")
    value = 42
    encrypted = helper.encrypt(value)
    decrypted = helper.decrypt(encrypted)
    print(f"    Original: {value}")
    print(f"    Decrypted: {decrypted[0]}")

    # Example 2: Vector encryption
    print("\n[3] Vector Encryption:")
    vector = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    encrypted_vec = helper.encrypt(vector)
    decrypted_vec = helper.decrypt(encrypted_vec)
    print(f"    Original: {vector}")
    print(f"    Decrypted: {decrypted_vec[:10]}")

    # Example 3: Addition
    print("\n[4] Homomorphic Addition:")
    vec1 = [10, 20, 30, 40, 50]
    vec2 = [5, 15, 25, 35, 45]

    encrypted_1 = helper.encrypt(vec1)
    encrypted_2 = helper.encrypt(vec2)
    encrypted_sum = helper.add(encrypted_1, encrypted_2)

    result = helper.decrypt(encrypted_sum)
    expected = [a + b for a, b in zip(vec1, vec2)]

    print(f"    Vector 1: {vec1}")
    print(f"    Vector 2: {vec2}")
    print(f"    Sum:      {result[:5]}")
    print(f"    Expected: {expected}")

    # Example 4: Multiplication
    print("\n[5] Homomorphic Multiplication:")
    vec_a = [2, 3, 4, 5, 6]
    vec_b = [3, 4, 5, 6, 7]

    encrypted_a = helper.encrypt(vec_a)
    encrypted_b = helper.encrypt(vec_b)
    encrypted_product = helper.multiply(encrypted_a, encrypted_b)

    result = helper.decrypt(encrypted_product)
    expected = [a * b for a, b in zip(vec_a, vec_b)]

    print(f"    Vector A:  {vec_a}")
    print(f"    Vector B:  {vec_b}")
    print(f"    Product:   {result[:5]}")
    print(f"    Expected:  {expected}")

    # Example 5: Complex computation
    print("\n[6] Complex Computation: (a + b) × (x + y)")
    x = [1, 2, 3]
    y = [4, 5, 6]
    a = [2, 2, 2]
    b = [3, 3, 3]

    enc_x = helper.encrypt(x)
    enc_y = helper.encrypt(y)
    enc_a = helper.encrypt(a)
    enc_b = helper.encrypt(b)

    # (x + y)
    enc_sum1 = helper.add(enc_x, enc_y)
    # (a + b)
    enc_sum2 = helper.add(enc_a, enc_b)
    # (x + y) × (a + b)
    enc_final = helper.multiply(enc_sum1, enc_sum2)

    result = helper.decrypt(enc_final)
    expected = [(xi + yi) * (ai + bi) for xi, yi, ai, bi in zip(x, y, a, b)]

    print(f"    x:        {x}")
    print(f"    y:        {y}")
    print(f"    a:        {a}")
    print(f"    b:        {b}")
    print(f"    Result:   {result[:3]}")
    print(f"    Expected: {expected}")

    # Example 6: Negation
    print("\n[7] Negation:")
    vec = [10, 20, 30]
    encrypted_vec = helper.encrypt(vec)
    encrypted_neg = helper.negate(encrypted_vec)
    result = helper.decrypt(encrypted_neg)
    print(f"    Original:  {vec}")
    print(f"    Negated:   {result[:3]}")
    print(f"    Expected:  {[-v for v in vec]}")

    # Example 7: Batch processing demonstration
    print("\n[8] Batch Processing (SIMD):")
    # BFV supports SIMD operations - we can encrypt many values at once
    batch_size = 100
    batch_data = list(range(1, batch_size + 1))

    # Single encryption for all values
    encrypted_batch = helper.encrypt(batch_data)

    # Perform operation on entire batch at once
    encrypted_doubled = helper.add(encrypted_batch, encrypted_batch)

    result = helper.decrypt(encrypted_doubled)
    print(f"    Batch size: {batch_size} values")
    print(f"    Operation: doubling each value")
    print(f"    First 10 results: {result[:10]}")
    print(f"    Expected: {[2 * i for i in batch_data[:10]]}")
    print(f"    Last 10 results: {result[batch_size-10:batch_size]}")

    print("\n" + "=" * 70)
    print("Demo completed successfully!")
    print("All operations performed on encrypted data!")
    print("=" * 70)


if __name__ == "__main__":
    main()
