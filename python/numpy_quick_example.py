"""
SEAL-Python NumPy Integration - Quick Example

This file demonstrates the core NumPy integration features
of the SEAL-Python bindings in a concise format.
"""

import os
import sys
import numpy as np

# Add the seal module to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
import seal

def main():
    print("SEAL-Python NumPy Integration - Quick Example")
    
    # Set up encryption parameters for CKKS scheme
    params = seal.EncryptionParameters(seal.SchemeType.CKKS)
    poly_modulus_degree = 8192
    params.set_poly_modulus_degree(poly_modulus_degree)
    params.set_coeff_modulus(
        seal.CoeffModulus.Create(poly_modulus_degree, [40, 40, 40, 40])
    )
    
    context = seal.SEALContext(params)
    
    # Generate keys
    keygen = seal.KeyGenerator(context)
    public_key = keygen.create_public_key()
    secret_key = keygen.secret_key()
    
    # Create encryptor, evaluator, and decryptor
    encryptor = seal.Encryptor(context, public_key)
    evaluator = seal.Evaluator(context)
    decryptor = seal.Decryptor(context, secret_key)
    
    # Create encoder
    encoder = seal.CKKSEncoder(context)
    slot_count = encoder.slot_count()
    print(f"Number of slots: {slot_count}")
    
    # =========================================================================
    # Feature 1: Direct encoding from NumPy arrays
    # =========================================================================
    print("\n1. Direct encoding from NumPy arrays")
    
    # Create a NumPy array
    scale = 2.0**40
    input_array = np.array([3.14159, 2.71828, 1.41421, 1.73205])
    
    # Pad the array to slot_count with zeros
    padded_array = np.zeros(slot_count)
    padded_array[:len(input_array)] = input_array
    
    # Encode the NumPy array directly
    plaintext = encoder.encode_new_numpy(padded_array, scale)
    
    # Encrypt - in this binding, encrypt() returns a SerializableCiphertext
    serializable_ciphertext = encryptor.encrypt(plaintext)
    
    # We need to convert SerializableCiphertext to Ciphertext for decryption
    # Using serialization as a bridge
    temp_file = "temp_cipher.bin"
    serializable_ciphertext.save(temp_file)
    
    # Load it back as a Ciphertext
    ciphertext = seal.Ciphertext()
    ciphertext.load(context, temp_file)
    
    # Create a destination plaintext for decryption
    plaintext_result = seal.Plaintext()
    
    # Now we can decrypt with the Ciphertext object
    decryptor.decrypt(ciphertext, plaintext_result)
    
    # Clean up the temporary file
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    # Decode the result
    result = encoder.decode(plaintext_result)
    
    # Verify
    print(f"Original: {input_array}")
    print(f"Decoded:  {result[:len(input_array)]}")
    print(f"Error:    {np.abs(input_array - result[:len(input_array)])}")
    
    # =========================================================================
    # Feature 2: Continuing with batch operations (skipping array conversion features)
    # =========================================================================
    print("\n2. Note: to_array() and to_array_view() methods are not used in this example")
    print("   as they may not be available in your binding.")
    print("   Continuing with batch operations instead.")
    
    # =========================================================================
    # Feature 4: Batch operations with ciphertexts
    # =========================================================================
    print("\n4. Batch operations with ciphertexts")
    
    # Create 5 ciphertexts
    count = 5
    # In this binding, we'll just create ciphertexts directly rather than pre-allocating
    print(f"Creating {count} ciphertexts")
    
    # Encrypt data into separate ciphertexts
    serializable_ciphertexts = []
    ciphertexts = []
    for i in range(count):
        # Pad with zeros to match slot_count
        data = np.zeros(slot_count)
        # Fill the first few values
        data[:4] = float(i+1)
        # Encode and encrypt
        plain = encoder.encode_new_numpy(data, scale)
        # In this binding, encrypt returns a SerializableCiphertext
        serializable_cipher = encryptor.encrypt(plain)
        serializable_ciphertexts.append(serializable_cipher)
        
        # Convert to Ciphertext for later use
        temp_file = f"temp_cipher_{i}.bin"
        serializable_cipher.save(temp_file)
        cipher = seal.Ciphertext()
        cipher.load(context, temp_file)
        ciphertexts.append(cipher)
        
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    # Save each ciphertext to its own file
    print("Saving ciphertexts individually")
    for i, cipher in enumerate(ciphertexts):
        file_path = f"ciphertext_{i}.bin"
        cipher.save(file_path)
        print(f"Saved ciphertext {i} to {file_path}")
    
    # Load ciphertexts from files
    print("Loading ciphertexts individually")
    loaded_ciphertexts = []
    for i in range(count):
        file_path = f"ciphertext_{i}.bin"
        # In your binding, you may need to create an empty ciphertext first
        loaded_cipher = seal.Ciphertext()
        loaded_cipher.load(context, file_path)
        loaded_ciphertexts.append(loaded_cipher)
        print(f"Loaded ciphertext from {file_path}")
    
    # Verify the loaded data
    for i, cipher in enumerate(loaded_ciphertexts):
        try:
            # Create a destination plaintext
            plaintext_result = seal.Plaintext()
            # Decrypt into the destination plaintext
            decryptor.decrypt(cipher, plaintext_result)
            result = encoder.decode(plaintext_result)
            print(f"Ciphertext {i} decrypts to: {result[:4]}")
        except Exception as e:
            print(f"Error decrypting ciphertext {i}: {e}")
        
    # Clean up files
    for i in range(count):
        file_path = f"ciphertext_{i}.bin"
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Clean up was done earlier for individual files
    
    print("\nNumPy integration example completed successfully!")

if __name__ == "__main__":
    main()
