# SEAL-Python 4.1.5

**Author:** Chandradutt Patel
**LinkedIn:** https://www.linkedin.com/in/cnpatel5746/

[![PyPI version](https://badge.fury.io/py/seal-python.svg)](https://badge.fury.io/py/seal-python)
[![Python Versions](https://img.shields.io/pypi/pyversions/seal-python.svg)](https://pypi.org/project/seal-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python binding for [Microsoft SEAL](https://github.com/microsoft/SEAL), enabling easy-to-use homomorphic encryption in Python. This project allows you to perform encrypted computation on real numbers and integers using CKKS, BFV, and BGV schemes, with advanced features including high-level wrapper APIs, NumPy integration, and comprehensive testing infrastructure.

**Developed and maintained by Chandradutt Patel**

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
  - [From GitHub](#from-github)
  - [Build Instructions](#build-instructions)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)
- [References](#references)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Contact](#contact)

---

## Features

### Core Functionality
- Python bindings for Microsoft SEAL 4.1.2+
- **CKKS** scheme for encrypted floating-point computation
- **BFV** and **BGV** schemes for encrypted integer computation
- Full homomorphic operations: addition, multiplication, negation, square, rotation, and more
- Serialization and deserialization of ciphertexts and keys
- Security levels: TC128, TC192, TC256

### Advanced Features (New in 4.1.5!)
- **High-level Python wrapper API** with `CKKSHelper` and `BFVHelper` classes for easier usage
- **Simplified parameter setup** with `create_ckks_params()` and `create_bfv_params()`
- **Utility functions** for serialization, key management, and more
- **Context managers** with `SEALContext` for automatic resource cleanup
- **Batch processing** with `BatchProcessor` for efficient multi-value operations
- **Performance monitoring** with `PerformanceMonitor` for optimization
- **Key management** with `KeyManager` for save/load operations
- **Computation patterns**: polynomial evaluation, matrix operations, dot product
- **High-performance NumPy integration** for efficient data transfer and manipulation
- **Zero-copy memory views** for advanced performance
- **Batch operations** for efficient processing of multiple ciphertexts
- **Pytest-based testing infrastructure** for reliability
- **CI/CD pipeline** with GitHub Actions for automated testing and deployment

### Developer-Friendly
- PyPI package for easy installation via pip
- Comprehensive documentation and examples
- Type hints and docstrings for better IDE support
- Beginner-friendly example scripts with detailed comments
- Contributing guide for community collaboration

---

## Project Structure

```
.
├── build.sh                # Build script
├── clean.sh                # Clean build artifacts
├── CMakeLists.txt          # CMake build configuration
├── README.md               # This file
├── setup.py                # Python package setup
├── docs/
│   ├── numpy_integration.md
│   └── quick_reference.md
├── python/                 # Python bindings and test scripts
│   ├── seal.so             # Compiled Python extension
│   ├── test_ckks.py
│   └── test_bfv_and_bgv.py
├── seal/                   # Python package directory
│   ├── __init__.py
│   └── seal.so
├── src/                    # C++ binding sources
│   └── core/
├── third_party/SEAL/       # Official Microsoft SEAL source
└── ...
```

---

## Requirements

**Install requirements.txt file for the important packages**
```sh
    pip install -r requirements.txt
```
- Python 3.8+
- C++17 compatible compiler (GCC >= 7, Clang >= 5)
- [CMake](https://cmake.org/) >= 3.13
- [pybind11](https://github.com/pybind/pybind11) (installed automatically if using the provided scripts)
- (Linux) `build-essential`, `python3-dev`, `ninja-build` recommended

---

## Installation

### From PyPI (Recommended)

The easiest way to install SEAL-Python is via pip:

```sh
pip install seal-python
```

**Note:** Pre-built wheels may not be available for all platforms yet. If pip installation fails, use the "From Source" method below.

### From Source

For the latest development version or if pre-built wheels are not available:

#### 1. Clone the repository

```sh
git clone https://github.com/chandradutt5746/SEAL-PYTHON-4.1.5.git
cd SEAL-PYTHON-4.1.5
```

#### 2. Get Microsoft SEAL (Do not skip this step!)

This binding requires the official [Microsoft SEAL](https://github.com/microsoft/SEAL) library.

**Clone SEAL into the `third_party/` directory:**

```sh
git clone https://github.com/microsoft/SEAL.git third_party/SEAL
```

#### 3. Create a Python virtual environment (recommended)

```sh
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 4. Install Python dependencies

```sh
pip install -r requirements.txt
```

#### 5. Build the C++ extension and SEAL library

```sh
./build.sh
```

This will compile Microsoft SEAL and the Python bindings. The resulting `seal.so` will be placed in the `python/` and `seal/` directories.

**Manual build** (if `build.sh` doesn't work):

```sh
mkdir -p build
cd build
cmake ..
make -j$(nproc)
cd ..
```

#### 6. Install as a Python package (optional)

If you want to use SEAL globally in your system:

```sh
pip install .
```

Or install in development/editable mode:

```sh
pip install -e .
```
---

## Quick Start

### Using the High-Level API (Easiest)

The new high-level API makes homomorphic encryption much easier to use:

```python
import seal

# CKKS Example (for floating-point numbers)
helper = seal.CKKSHelper(poly_modulus_degree=8192)

# Encrypt values
encrypted_x = helper.encrypt(3.14)
encrypted_y = helper.encrypt(2.0)

# Perform homomorphic operations
encrypted_sum = helper.add(encrypted_x, encrypted_y)
encrypted_product = helper.multiply(encrypted_x, encrypted_y)

# Decrypt results
sum_result = helper.decrypt(encrypted_sum)       # ≈ 5.14
product_result = helper.decrypt(encrypted_product)  # ≈ 6.28

print(f"Sum: {sum_result}, Product: {product_result}")
```

```python
# BFV Example (for integers)
helper = seal.BFVHelper(poly_modulus_degree=4096)

# Encrypt integer vectors
encrypted_x = helper.encrypt([1, 2, 3, 4, 5])
encrypted_y = helper.encrypt([5, 4, 3, 2, 1])

# Homomorphic addition
encrypted_sum = helper.add(encrypted_x, encrypted_y)

# Decrypt
result = helper.decrypt(encrypted_sum)
print(f"Result: {result[:5]}")  # [6, 6, 6, 6, 6]
```

### Using the Low-Level API

After building, you can run the example scripts:
### In this 'python' folder you will find seal.so file after building the Python Binding.
### Do not Remove this file otherwise you have to build the seal again.

#### For basic understanding, try to open these example files in order:

```sh
cd python
python test_bfv_and_bgv.py        # Basic BFV and BGV examples
python test_numpy_integration.py   # NumPy integration examples
python test_bootstrapping.py       # Advanced bootstrapping operations
```

- The `seal.so` file must be present in the `python/` directory for imports to work.
- **Do not remove `seal.so`** unless you plan to rebuild.

---

## Usage Examples

### Basic Usage

See `python/test_bfv_and_bgv.py` for basic examples of using BFV and BGV schemes.

### NumPy Integration

SEAL-Python provides powerful NumPy integration features for high-performance data handling:

- **Direct encoding from NumPy arrays** with `encode_new_numpy()`
- **Converting ciphertexts to NumPy arrays** with `to_array()`
- **Zero-copy views** of ciphertext data with `to_array_view()`
- **Batch operations** for multiple ciphertexts

For detailed examples and usage, see the [NumPy Integration Guide](docs/numpy_integration.md) and the example scripts in the `python/` directory.

For a complete example, see `python/test_numpy_integration.py`.

### Advanced Usage

See `python/test_bootstrapping.py` for examples of advanced operations.

## Important API Notes

1. **Key Generation**: This binding uses `keygen.create_public_key()` rather than `keygen.public_key()` which might be found in other bindings.

2. **SerializableCiphertext vs Ciphertext**: The `encrypt()` method returns a `SerializableCiphertext` object, while the `decrypt()` method requires a `Ciphertext` object. You need to convert between these types using serialization when decrypting data.

3. **Batch Operations**: When working with multiple ciphertexts, you'll need to convert between serializable and regular ciphertext types.

4. **NumPy Integration**: The `encode_new_numpy()` method provides efficient encoding of NumPy arrays.

For complete examples of these operations, see the [Quick Reference Guide](docs/quick_reference.md) and the example files in the `python/` directory.

## Testing

You can run the provided test scripts:

```sh
cd python
python test_bfv_and_bgv.py
python test_numpy_integration.py
python test_bootstrapping.py
```

---

## Troubleshooting

- **Build errors:** Ensure you have a C++17 compiler and all dependencies installed.
- **Import errors:** Make sure `seal.so` is in your `PYTHONPATH` or in the same directory as your script.
- **Empty decode results:** Ensure you are using the latest binding code and returning vectors from C++ to Python.
- **Debugging:** The example scripts include `[DEBUG]` print statements to help trace computation steps.
- **Virtual environment:** If you have issues, try running everything inside a fresh Python virtual environment.
---

## Security Notes

- **No secrets or credentials** are included in this repository.
- **Do not share your secret keys** or decrypted data.
- **Review all dependencies** and keep them up to date.
- **For research and educational use only.** Not for production or handling sensitive data without a full security review.

---

## Documentation

- [NumPy Integration Guide](docs/numpy_integration.md) - Detailed guide on using NumPy with SEAL-Python
- [Quick Reference Guide](docs/quick_reference.md) - Concise examples and tips for common SEAL-Python operations
- Additional documentation can be found in the `docs/` directory.

## References

- [Microsoft SEAL Documentation](https://github.com/microsoft/SEAL)
- [Homomorphic Encryption Standardization](https://homomorphicencryption.org/)
- [pybind11 Documentation](https://pybind11.readthedocs.io/en/stable/)
- [NumPy Documentation](https://numpy.org/doc/)

---

## License

Copyright (c) 2025 Chandradutt Patel

This project is licensed under the MIT License. See [third_party/SEAL/LICENSE](third_party/SEAL/LICENSE) for Microsoft SEAL's license.

---

## Acknowledgments

- Microsoft SEAL team for the core library
- pybind11 for Python bindings
- Chandradutt Patel for the Python binding and packaging

---

## Contact

For collaboration, questions, or contributions, please:
- Open an issue or pull request on GitHub
- Connect on [LinkedIn](https://www.linkedin.com/in/cnpatel5746/)

---

## Example Files

The `python/` directory contains several example files to help you get started:

- **basic_example.py** - Simple example demonstrating core API usage including proper handling of SerializableCiphertext vs Ciphertext
- **test_bfv_and_bgv.py** - Examples of using BFV and BGV encryption schemes
- **test_ckks.py** - Examples of using the CKKS encryption scheme for floating-point operations
- **test_numpy_integration.py** - Comprehensive examples of NumPy integration features
- **numpy_simple_example.py** - Simple examples focused on NumPy integration
- **numpy_quick_example.py** - Quick demonstration of NumPy features

These examples are designed to be run in order of increasing complexity and provide detailed comments to help you understand how to use the library effectively.

---

*Happy encrypting!*