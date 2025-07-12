from seal import *

def get_seal(
    security_level=sec_level_type.TC192,
    poly_modulus_degree=32768
):
    """Create SEAL context with production-validated parameters"""
    parms = EncryptionParameters(SchemeType.CKKS)
    parms.set_poly_modulus_degree(poly_modulus_degree)
    
    # Get SEAL's maximum allowed coefficient modulus bits
    max_bits = CoeffModulus.MaxBitCount(poly_modulus_degree, sec_level=security_level)
    
    # Security-optimized configurations (all primes <= 60 bits)
    SECURITY_CONFIGS = {
        # 128-bit security (high performance)
        sec_level_type.TC128: {
            4096: (109, [54, 55]),                   # 2 primes, depth 1
            8192: (218, [55, 55, 54, 54]),           # 4 primes, depth 3
            16384: (438, [55, 55, 55, 55, 55, 55, 55, 53]),  # 8 primes, depth 7
            32768: (881, [60]*14 + [41])             # 15 primes, depth 14
        },
        # 192-bit security (balanced)
        sec_level_type.TC192: {
            4096: (77, [50, 27]),                   # 2 primes, depth 1
            8192: (154, [51, 51, 52]),              # 3 primes, depth 2
            16384: (300, [60, 60, 60, 60, 60]),    # 5 primes, depth 4
            32768: (600, [60]*10)                   # 10 primes, depth 9
        },
        # 256-bit security (high security)
        sec_level_type.TC256: {
            4096: (60, [60]),                       # 1 prime, depth 0
            8192: (120, [60, 60]),                  # 2 primes, depth 1
            16384: (239, [60, 60, 59]),             # 3 primes, depth 2
            32768: (476, [60, 60, 60, 60, 60, 60, 56])  # 7 primes, depth 6
        }
    }
    
    # Get parameters
    try:
        total_logq, coeff_modulus_bits = SECURITY_CONFIGS[security_level][poly_modulus_degree]
    except KeyError:
        # Fallback to SEAL defaults
        coeff_modulus_bits = [min(60, max_bits)]
        total_logq = sum(coeff_modulus_bits)
    
    # Auto-adjust if needed
    if sum(coeff_modulus_bits) > max_bits:
        diff = sum(coeff_modulus_bits) - max_bits
        coeff_modulus_bits[-1] = max(40, coeff_modulus_bits[-1] - diff)
        total_logq = sum(coeff_modulus_bits)
    
    print(f"[CONFIG] Security: {security_level}, Poly deg: {poly_modulus_degree}")
    print(f"         Total modulus: {total_logq}/{max_bits} bits, Chain: {coeff_modulus_bits}")
    
    # Create coefficient modulus
    coeff_modulus = CoeffModulus.Create(poly_modulus_degree, coeff_modulus_bits)
    parms.set_coeff_modulus(coeff_modulus)
    
    # Create context
    context = SEALContext(parms, expand_mod_chain=True, sec_level=security_level)
    if not context.parameters_set():
        qualifiers = context.first_context_data().qualifiers()
        raise ValueError(f"Invalid parameters: {qualifiers.parameter_error_message}")
    
    return context

# Tested production configurations
if __name__ == "__main__":
    # Ultra-fast 128-bit
    print("\n1. 128-bit (4K):")
    ctx = get_seal(sec_level_type.TC128, 4096)
    
    # Balanced 192-bit
    print("\n2. 192-bit (16K):")
    ctx = get_seal(sec_level_type.TC192, 16384)
    
    # High-security 256-bit
    print("\n3. 256-bit (32K):")
    ctx = get_seal(sec_level_type.TC256, 32768)
    
    # High-throughput 192-bit
    print("\n4. 192-bit (32K):")
    ctx = get_seal(sec_level_type.TC192, 32768)

    
'''from seal import *

def get_seal(security_level=sec_level_type.TC192):
    """Create SEAL context with HE-standard parameters for 192/256-bit security"""
    parms = EncryptionParameters(SchemeType.CKKS)
    
    # Security parameter tables (fixed to SEAL constraints)
    security_params = {
        # 192-bit security
        sec_level_type.TC192: {
            16384: (307, [60, 60, 60, 60, 60]),  # 300 bits (5 primes)
            32768: (612, [60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 12])  # Fixed last prime
        },
        # 256-bit security
        sec_level_type.TC256: {
            16384: (239, [60, 60, 59]),  # 179 bits (3 primes)
            32768: (478, [60, 60, 60, 60, 60, 60, 58])  # 418 bits (7 primes)
        }
    }
    
    # Select polynomial degree
    if security_level == sec_level_type.TC192:
        poly_modulus_degree = 16384
    else:  # TC256
        poly_modulus_degree = 32768
    
    # Get parameters from table
    total_logq, coeff_modulus_bits = security_params[security_level][poly_modulus_degree]
    
    # Adjust to valid bit sizes (2-60 bits)
    coeff_modulus_bits = [min(max(b, 2), 60) for b in coeff_modulus_bits]
    
    # Set parameters
    parms.set_poly_modulus_degree(poly_modulus_degree)
    parms.set_coeff_modulus(CoeffModulus.Create(poly_modulus_degree, coeff_modulus_bits))
    
    scale = 2.0 ** 100
    print(f'[CONFIG] Security: {security_level}, '
          f'Poly deg: {poly_modulus_degree}, '
          f'Total q: {sum(coeff_modulus_bits)} bits, '
          f'Mod chain: {coeff_modulus_bits}')
    
    # Create context
    context = SEALContext(parms, expand_mod_chain=True, sec_level=security_level)
    
    # Validate parameters
    if not context.parameters_set():
        context_data = context.key_context_data()
        if context_data:
            qualifiers = context_data.qualifiers
            error_msg = (f"Parameters invalid: {qualifiers.parameter_error_name} - "
                         f"{qualifiers.parameter_error_message}")
            raise ValueError(error_msg)
        raise ValueError("Encryption parameters are invalid")
    
    # Create encoder and print slot count
    ckks_encoder = CKKSEncoder(context)
    slot_count = ckks_encoder.slot_count()
    print(f'[DEBUG] Slot count: {slot_count}')
    
    # Generate keys
    keygen = KeyGenerator(context)
    public_key = keygen.create_public_key()
    secret_key = keygen.secret_key()
    relin_keys = keygen.create_relin_keys()
    galois_keys = keygen.create_galois_keys()
    
    # Create operators
    encryptor = Encryptor(context, public_key)
    evaluator = Evaluator(context)
    decryptor = Decryptor(context, secret_key)

    # Encode and encrypt sample data
    data = [1.23, 4.56, 7.89, 10, 150256, 123123123, 123123123123123, 123123123123123123999889]
    plain = ckks_encoder.encode_new(data, scale)
    test_decoded = ckks_encoder.decode(plain)
    print(f'Decoded: {test_decoded[:8]}')
    cipher = encryptor.encrypt(plain)
    
    return cipher, context, ckks_encoder, decryptor, evaluator, encryptor, scale, relin_keys, galois_keys

# Example usage
if __name__ == "__main__":
    # Run with 192-bit security
    print("Running with 192-bit security:")
    cipher192, ctx192, *_ = get_seal(security_level=sec_level_type.TC192)
    
    # Run with 256-bit security
    print("\nRunning with 256-bit security:")
    cipher256, ctx256, *_ = get_seal(security_level=sec_level_type.TC256)'''