#!/usr/bin/env python3
"""
SEAL-Python Basic Usage Example

This file demonstrates the core functionality of the SEAL-Python binding,
including proper handling of SerializableCiphertext vs Ciphertext objects.

Author: Chandradutt Patel
"""

import os
import sys
import numpy as np

# Add the seal module to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
import seal

def main():
    print("SEAL-Python Basic Usage Example")
    print("===============================")
    
    # Step 1: Set up encryption parameters
    print("\n[STEP 1] Setting up encryption parameters")
    params = seal.EncryptionParameters(seal.SchemeType.CKKS)
    poly_modulus_degree = 8192
    params.set_poly_modulus_degree(poly_modulus_degree)
    params.set_coeff_modulus(
        seal.CoeffModulus.Create(poly_modulus_degree, [40, 40, 40, 40])
    )
    context = seal.SEALContext(params)
    
    # Step 2: Generate keys
    print("\n[STEP 2] Generating keys")
    keygen = seal.KeyGenerator(context)
    public_key = keygen.create_public_key()  # Note: create_public_key() is the correct API
    secret_key = keygen.secret_key()
    
    # Step 3: Set up encoder, encryptor, evaluator, and decryptor
    print("\n[STEP 3] Creating encoder, encryptor, evaluator, and decryptor")
    encoder = seal.CKKSEncoder(context)
    encryptor = seal.Encryptor(context, public_key)
    evaluator = seal.Evaluator(context)
    decryptor = seal.Decryptor(context, secret_key)
    
    slot_count = encoder.slot_count()
    print(f"Number of slots: {slot_count}")
    
    # Step 4: Encode and encrypt data
    print("\n[STEP 4] Encoding and encrypting data")
    # Create a simple vector of values
    values = np.array([3.1, 4.1, 5.9, 2.6])
    print(f"Original values: {values}")
    
    # Set the scale
    scale = 2.0**40
    
    # Encode the values
    plaintext = encoder.encode_new_numpy(values, scale)
    print("Encoding successful")
    
    # Encrypt the plaintext (returns a SerializableCiphertext)
    encrypted = encryptor.encrypt(plaintext)
    print(f"Encryption successful, result type: {type(encrypted)}")
    
    # Step 5: Convert SerializableCiphertext to Ciphertext
    print("\n[STEP 5] Converting SerializableCiphertext to Ciphertext")
    print("* This is a critical step for operations and decryption *")
    
    # Save the SerializableCiphertext to a file
    temp_file = "temp_cipher.bin"
    encrypted.save(temp_file)
    print(f"Saved SerializableCiphertext to {temp_file}")
    
    # Create a Ciphertext object and load from the file
    ciphertext = seal.Ciphertext()
    ciphertext.load(context, temp_file)
    print(f"Loaded as Ciphertext, type: {type(ciphertext)}")
    
    # Clean up the temporary file
    os.remove(temp_file)
    print(f"Removed temporary file: {temp_file}")
    
    # Step 6: Perform operations (requires Ciphertext)
    print("\n[STEP 6] Performing homomorphic operations")
    # Square the encrypted values (x² operation)
    result = seal.Ciphertext()
    evaluator.square(ciphertext, result)
    print("Computed square of encrypted values")
    
    # Step 7: Decrypt and decode
    print("\n[STEP 7] Decrypting and decoding")
    # Create a plaintext for the result
    decrypted = seal.Plaintext()
    
    # Decrypt (requires a Ciphertext input)
    decryptor.decrypt(result, decrypted)
    print("Decryption successful")
    
    # Decode
    decoded = encoder.decode(decrypted)
    print("Decoding successful")
    
    # Step 8: Verify results
    print("\n[STEP 8] Verifying results")
    expected = values ** 2
    result_values = decoded[:len(values)]
    
    print(f"Original values:   {values}")
    print(f"Expected (x²):     {expected}")
    print(f"Decrypted result:  {result_values}")
    print(f"Absolute error:    {np.abs(expected - result_values)}")
    
    print("\nBasic example completed successfully!")

if __name__ == "__main__":
    main()
