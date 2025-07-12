#!/usr/bin/env python3
"""
SEAL Python Bindings: NumPy Integration Example

This example demonstrates how to use NumPy arrays with Microsoft SEAL Python bindings,
showcasing the high-performance data exchange between NumPy arrays and SEAL ciphertexts.

Author: Chandradutt Patel
"""

import os
import sys
import time
import numpy as np

# Add the seal module to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
import seal

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")

def print_step(step):
    """Print a step in the example"""
    print(f"\n[STEP] {step}")

def main():
    print_header("SEAL-Python NumPy Integration Example")
    
    print_step("Setting up encryption parameters")
    # Set up encryption parameters
    params = seal.EncryptionParameters(seal.SchemeType.CKKS)
    
    # Use a smaller polynomial modulus degree for this example
    poly_modulus_degree = 8192
    params.set_poly_modulus_degree(poly_modulus_degree)
    
    # Create the coefficient modulus
    params.set_coeff_modulus(seal.CoeffModulus.Create(poly_modulus_degree, [40, 40, 40, 40]))
    
    # Create the context
    context = seal.SEALContext(params)
    
    # Generate keys
    print_step("Generating keys")
    keygen = seal.KeyGenerator(context)
    public_key = keygen.create_public_key()
    secret_key = keygen.secret_key()
    
    # Create encryptor, evaluator, and decryptor
    encryptor = seal.Encryptor(context, public_key)
    evaluator = seal.Evaluator(context)
    decryptor = seal.Decryptor(context, secret_key)
    
    # Create a CKKSEncoder
    print_step("Creating encoder")
    ckks_encoder = seal.CKKSEncoder(context)
    slot_count = ckks_encoder.slot_count()
    print(f"Number of slots: {slot_count}")
    
    # Create input data as NumPy arrays
    print_step("Creating input data using NumPy arrays")
    scale = 2.0**40
    
    # Create random input vectors
    vector1 = np.random.random(slot_count)
    vector2 = np.random.random(slot_count)
    
    print(f"Input vector1[0:4]: {vector1[0:4]}")
    print(f"Input vector2[0:4]: {vector2[0:4]}")
    
    # METHOD 1: Encode and encrypt NumPy arrays
    print_step("METHOD 1: Standard encoding and encryption with NumPy")
    
    # Encode using the new NumPy integration method
    start_time = time.time()
    plain1 = ckks_encoder.encode_new_numpy(vector1, scale)
    plain2 = ckks_encoder.encode_new_numpy(vector2, scale)
    encoding_time = time.time() - start_time
    print(f"NumPy encoding time: {encoding_time:.5f} seconds")
    
    # Encrypt - returns SerializableCiphertext
    start_time = time.time()
    serz_cipher1 = encryptor.encrypt(plain1)
    serz_cipher2 = encryptor.encrypt(plain2)
    encryption_time = time.time() - start_time
    print(f"Encryption time: {encryption_time:.5f} seconds")
    
    # Convert SerializableCiphertext to Ciphertext for evaluation
    temp1_file = "temp_cipher1.bin"
    temp2_file = "temp_cipher2.bin"
    serz_cipher1.save(temp1_file)
    serz_cipher2.save(temp2_file)
    
    # Load as Ciphertext
    cipher1 = seal.Ciphertext()
    cipher2 = seal.Ciphertext()
    cipher1.load(context, temp1_file)
    cipher2.load(context, temp2_file)
    
    # Clean up temp files
    if os.path.exists(temp1_file):
        os.remove(temp1_file)
    if os.path.exists(temp2_file):
        os.remove(temp2_file)
    
    # Perform computation (addition)
    start_time = time.time()
    result_cipher = seal.Ciphertext()  # Create destination ciphertext
    evaluator.add(cipher1, cipher2, result_cipher)
    computation_time = time.time() - start_time
    print(f"Addition time: {computation_time:.5f} seconds")
    
    # Decrypt and decode
    start_time = time.time()
    result_plain = seal.Plaintext()
    decryptor.decrypt(result_cipher, result_plain)
    result_decoded = ckks_encoder.decode(result_plain)
    decoding_time = time.time() - start_time
    print(f"Decryption and decoding time: {decoding_time:.5f} seconds")
    
    # Verify results
    expected = vector1 + vector2
    print(f"Expected result[0:4]: {expected[0:4]}")
    print(f"Decoded result[0:4]: {result_decoded[0:4]}")
    print(f"Absolute error[0:4]: {np.abs(expected[0:4] - result_decoded[0:4])}")
    
    # METHOD 2: Direct ciphertext creation from NumPy arrays
    print_step("METHOD 2: Direct ciphertext creation from NumPy arrays")
    
    # First encrypt a ciphertext to get its parameters
    template_plain = ckks_encoder.encode_new_numpy(vector1, scale)
    serz_template_cipher = encryptor.encrypt(template_plain)
    
    # Convert SerializableCiphertext to Ciphertext
    temp_template_file = "temp_template.bin"
    serz_template_cipher.save(temp_template_file)
    template_cipher = seal.Ciphertext()
    template_cipher.load(context, temp_template_file)
    os.remove(temp_template_file)
    
    # Convert template ciphertext to array to understand its structure
    cipher_array = template_cipher.to_array()
    print(f"Ciphertext shape: {cipher_array.shape}")
    
    # Get parameters needed for direct ciphertext creation
    poly_count = template_cipher.size()
    coeff_mod_count = template_cipher.coeff_modulus_size()
    poly_mod_degree = template_cipher.poly_modulus_degree()
    
    # Create a new ciphertext directly from a NumPy array (for demonstration)
    # Note: In a real application, you would create meaningful data here
    print("Creating a ciphertext directly from NumPy array")
    start_time = time.time()
    
    try:
        # Create a random array with the correct dimensions
        # WARNING: This is just for demonstration - this won't be a valid ciphertext!
        random_data = np.random.randint(
            0, 2**64-1, 
            size=poly_count * coeff_mod_count * poly_mod_degree, 
            dtype=np.uint64
        )
        
        # Create a ciphertext directly from the NumPy array
        # Note: This is just a demonstration of the API - the resulting ciphertext won't be valid
        custom_cipher = seal.Ciphertext(context, random_data, poly_count, coeff_mod_count, 
                                        poly_mod_degree, scale)
        direct_creation_time = time.time() - start_time
        print(f"Direct ciphertext creation time: {direct_creation_time:.5f} seconds")
    except (AttributeError, TypeError) as e:
        direct_creation_time = time.time() - start_time
        print(f"Direct ciphertext creation from NumPy array is not supported in this binding: {e}")
        print("This is an advanced feature that may not be implemented in all versions")
    
    # METHOD 3: Zero-copy view of ciphertext data
    print_step("METHOD 3: Zero-copy access to ciphertext data")
    
    # Get a zero-copy view of the ciphertext data
    start_time = time.time()
    try:
        view = template_cipher.to_array_view()
        view_time = time.time() - start_time
        print(f"Getting zero-copy view time: {view_time:.5f} seconds")
        print(f"View shape: {view.shape}")
        
        # Note: Modifying this view will directly modify the ciphertext data!
        # This is unsafe to use unless you know what you're doing
        print("Warning: Modifying the view will directly modify the ciphertext!")
    except AttributeError:
        view_time = time.time() - start_time
        print("to_array_view() is not available in this binding version")
        print("This is an advanced feature that may not be implemented in all versions")
    
    # METHOD 4: Batch operations with ciphertexts
    print_step("METHOD 4: Batch operations with multiple ciphertexts")
    
    # Create multiple ciphertexts
    num_ciphertexts = 5
    print(f"Creating {num_ciphertexts} ciphertexts")
    
    # Create multiple serializable ciphertexts and convert them to regular ciphertexts
    start_time = time.time()
    serializable_ciphertexts = []
    ciphertexts = []
    
    # Encrypt data into separate ciphertexts
    for i in range(num_ciphertexts):
        # Create random data for this example
        data = np.random.random(slot_count)
        plain = ckks_encoder.encode_new_numpy(data, scale)
        
        # Encrypt to get a SerializableCiphertext
        serializable_cipher = encryptor.encrypt(plain)
        serializable_ciphertexts.append(serializable_cipher)
        
        # Convert to a regular Ciphertext
        temp_file = f"temp_cipher_{i}.bin"
        serializable_cipher.save(temp_file)
        cipher = seal.Ciphertext()
        cipher.load(context, temp_file)
        ciphertexts.append(cipher)
        os.remove(temp_file)
    
    preallocation_time = time.time() - start_time
    print(f"Cipher creation time: {preallocation_time:.5f} seconds")
    
    # Save multiple ciphertexts to individual files (simulating batch save)
    batch_dir = os.path.join(current_dir, "batch_ciphertexts")
    os.makedirs(batch_dir, exist_ok=True)
    
    start_time = time.time()
    for i, cipher in enumerate(ciphertexts):
        cipher_file = os.path.join(batch_dir, f"cipher_{i}.bin")
        cipher.save(cipher_file)
    save_time = time.time() - start_time
    print(f"Saved {len(ciphertexts)} ciphertexts in {save_time:.5f} seconds")
    
    # Load multiple ciphertexts from files
    start_time = time.time()
    loaded_ciphertexts = []
    for i in range(num_ciphertexts):
        cipher_file = os.path.join(batch_dir, f"cipher_{i}.bin")
        loaded_cipher = seal.Ciphertext()
        loaded_cipher.load(context, cipher_file)
        loaded_ciphertexts.append(loaded_cipher)
        os.remove(cipher_file)  # Clean up
    load_time = time.time() - start_time
    print(f"Loaded {len(loaded_ciphertexts)} ciphertexts in {load_time:.5f} seconds")
    
    # Clean up the batch directory
    os.rmdir(batch_dir)
    
    print_step("Conclusion")
    print("NumPy integration provides significant performance benefits:")
    print("1. Direct encoding of NumPy arrays using encode_new_numpy()")
    print("2. Converting ciphertexts to NumPy arrays with to_array()")
    print("3. Zero-copy views of ciphertext data with to_array_view()")
    print("4. Direct ciphertext creation from NumPy arrays")
    print("5. Batch operations with multiple ciphertexts")

if __name__ == "__main__":
    main()
