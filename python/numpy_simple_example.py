"""
SEAL-Python NumPy Integration - Simple Example

This file demonstrates the basic NumPy integration features
of the SEAL-Python bindings.
"""

import os
import sys
import numpy as np

# Add the seal module to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
import seal

def main():
    print("SEAL-Python NumPy Integration - Simple Example")
    
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
    
    # Example 1: Encode and encrypt a NumPy array
    print("\nExample 1: Encode and encrypt a NumPy array")
    
    # Create a NumPy array with test data
    scale = 2.0**40
    input_array = np.array([3.14159, 2.71828, 1.41421, 1.73205])
    print(f"Original data: {input_array}")
    
    # Pad with zeros to fill all slots
    padded_array = np.zeros(slot_count)
    padded_array[:len(input_array)] = input_array
    
    try:
        # Try to encode directly from NumPy array
        print("Encoding NumPy array...")
        plaintext = encoder.encode_new_numpy(padded_array, scale)
        print("Encoding successful!")
        
        # Encrypt
        print("Encrypting...")
        encrypted = encryptor.encrypt(plaintext)
        print("Encryption successful!")
        print(f"Type of encrypted object: {type(encrypted)}")
        
        # Let's inspect what methods are available
        print("\nMethods available on the encrypted object:")
        methods = [method for method in dir(encrypted) if not method.startswith('__')]
        for method in methods:
            print(f" - {method}")
            
        # Create a Ciphertext object and see what methods it has
        try:
            print("\nCreating a Ciphertext object to inspect:")
            ct = seal.Ciphertext()
            print(f"Type of Ciphertext: {type(ct)}")
            ct_methods = [method for method in dir(ct) if not method.startswith('__')]
            for method in ct_methods:
                print(f" - {method}")
        except Exception as e:
            print(f"Error creating Ciphertext: {e}")
            
        # Attempt to convert SerializableCiphertext to Ciphertext if possible
        print("\nAttempting to decrypt:")
        
        # Create plaintext destination
        result_plaintext = seal.Plaintext()
        
        # Try to find a way to get a Ciphertext from SerializableCiphertext
        # In some bindings, Ciphertext and SerializableCiphertext might be compatible
        # or there might be a conversion method
        
        # Let's try to use serialization as a bridge if direct conversion isn't available
        try:
            print("Trying to use serialization as a bridge...")
            
            # Save the SerializableCiphertext to a file
            temp_file = "temp_ciphertext.bin"
            print(f"Saving SerializableCiphertext to {temp_file}")
            encrypted.save(temp_file)
            
            # Load it back as a Ciphertext
            print("Loading back as a Ciphertext")
            ciphertext = seal.Ciphertext()
            ciphertext.load(context, temp_file)
            
            # Now try to decrypt
            print("Decrypting loaded Ciphertext")
            decryptor.decrypt(ciphertext, result_plaintext)
            print("Decryption successful!")
            
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except Exception as e:
            print(f"Error during conversion via serialization: {e}")
            result_plaintext = None
        
        # Decode
        print("Decoding...")
        result = encoder.decode(result_plaintext)
        print("Decoding successful!")
        
        # Check results
        print(f"Original: {input_array}")
        print(f"Result:   {result[:len(input_array)]}")
        print(f"Error:    {np.abs(input_array - result[:len(input_array)])}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nExample complete!")

if __name__ == "__main__":
    main()
