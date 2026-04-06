"""
Example demonstrating the high-level CKKSHelper API.

This example shows how to use the new CKKSHelper class for
simplified homomorphic encryption with CKKS scheme.
"""

import seal


def main():
    print("=" * 70)
    print("SEAL-Python High-Level API Demo - CKKS Scheme")
    print("=" * 70)

    # Create a CKKS helper with default parameters
    print("\n[1] Initializing CKKS helper...")
    helper = seal.CKKSHelper(poly_modulus_degree=8192, scale_bits=40)
    print("    ✓ Context created and keys generated")

    # Example 1: Basic encryption and decryption
    print("\n[2] Basic Encryption/Decryption:")
    value = 3.14159
    encrypted = helper.encrypt(value)
    decrypted = helper.decrypt(encrypted)
    print(f"    Original: {value}")
    print(f"    Decrypted: {decrypted}")
    print(f"    Error: {abs(value - decrypted):.10f}")

    # Example 2: Addition
    print("\n[3] Homomorphic Addition:")
    x = 10.5
    y = 20.3
    encrypted_x = helper.encrypt(x)
    encrypted_y = helper.encrypt(y)
    encrypted_sum = helper.add(encrypted_x, encrypted_y)
    result = helper.decrypt(encrypted_sum)
    print(f"    {x} + {y} = {result}")
    print(f"    Expected: {x + y}")
    print(f"    Error: {abs(result - (x + y)):.10f}")

    # Example 3: Multiplication
    print("\n[4] Homomorphic Multiplication:")
    a = 5.0
    b = 7.0
    encrypted_a = helper.encrypt(a)
    encrypted_b = helper.encrypt(b)
    encrypted_product = helper.multiply(encrypted_a, encrypted_b)
    result = helper.decrypt(encrypted_product)
    print(f"    {a} × {b} = {result}")
    print(f"    Expected: {a * b}")
    print(f"    Error: {abs(result - (a * b)):.10f}")

    # Example 4: Complex computation
    print("\n[5] Complex Computation: (x + y) × (a + b)")
    encrypted_sum1 = helper.add(encrypted_x, encrypted_y)
    encrypted_sum2 = helper.add(encrypted_a, encrypted_b)

    # Note: Need to match scales for multiplication
    # The helper handles relinearization and rescaling
    encrypted_final = helper.multiply(encrypted_sum1, encrypted_sum2)
    result = helper.decrypt(encrypted_final)

    expected = (x + y) * (a + b)
    print(f"    Result: {result}")
    print(f"    Expected: {expected}")
    print(f"    Error: {abs(result - expected):.6f}")

    # Example 5: Negation and Square
    print("\n[6] Other Operations:")
    val = 4.0
    encrypted_val = helper.encrypt(val)

    # Negate
    encrypted_neg = helper.negate(encrypted_val)
    neg_result = helper.decrypt(encrypted_neg)
    print(f"    Negate({val}) = {neg_result}")

    # Square
    encrypted_sq = helper.square(encrypted_val)
    sq_result = helper.decrypt(encrypted_sq)
    print(f"    Square({val}) = {sq_result}")
    print(f"    Expected: {val ** 2}")

    # Example 6: Vector operations
    print("\n[7] Vector Operations:")
    vector = [1.0, 2.0, 3.0, 4.0, 5.0]
    encrypted_vec = helper.encrypt(vector)
    decrypted_vec = helper.decrypt(encrypted_vec)
    print(f"    Original: {vector}")
    print(f"    Decrypted: {decrypted_vec[:5]}")

    print("\n" + "=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
