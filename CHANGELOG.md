# Changelog

All notable changes to SEAL-Python will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.1.5] - 2026-04-06

### Added
- Modern PyPI-ready package structure with `pyproject.toml`
- High-level Python wrapper API with `CKKSHelper` and `BFVHelper` classes
- **Advanced features module** (`seal/advanced.py`):
  - `SEALContext`: Context manager for automatic resource cleanup
  - `BatchProcessor`: Efficient batch encryption/decryption operations
  - `PerformanceMonitor`: Track and analyze operation performance
  - `KeyManager`: Save/load encryption keys to/from disk
  - `polynomial_evaluation()`: Evaluate polynomials on encrypted data
  - `matrix_vector_multiply()`: Linear algebra on encrypted vectors
  - `dot_product()`: Compute dot product of encrypted vectors
  - `measure_performance()`: Decorator for performance tracking
- Utility functions for easier encryption parameter setup
- Comprehensive pytest-based testing infrastructure
- GitHub Actions CI/CD workflow for automated testing and wheel building
- MANIFEST.in for proper source distribution packaging
- CONTRIBUTING.md guide for new contributors
- This CHANGELOG.md file to track version changes
- Support for Python 3.8 through 3.12
- Type hints and better documentation in utility modules
- Serialization helper functions: `serialize_to_bytes()` and `deserialize_from_bytes()`
- Convenience functions: `create_ckks_params()` and `create_bfv_params()`
- `show_security_warning()` function for on-demand security notice
- Metadata tracking in `CKKSHelper` for proper scalar vs vector decryption
- `decrypt_scalar()` and `decrypt_vector()` methods in `CKKSHelper`

### Changed
- Updated package metadata for PyPI publication
- Improved seal/__init__.py with better error handling and imports
- Enhanced README.md with PyPI installation instructions and advanced features
- Version bumped to 4.1.5 for new feature release
- Refactored `seal/__init__.py`: replaced warnings with ImportError, removed auto-print
- Improved `seal/utils.py`: added SEAL API validation with `_has_required_seal_api()`
- Minimized `setup.py`: removed duplicate metadata, kept only build logic
- Updated `build.sh`: stops overwriting `seal/__init__.py`
- Updated `pyproject.toml`: CMake requirement to 3.15, added ImportWarning filter
- Fixed CI/CD workflow: removed `continue-on-error` to enforce quality
- Improved test skip conditions: check `SEAL_LOADED` attribute properly

### Fixed
- Better error messages when SEAL extension is not built
- Improved import handling in the seal package
- Proper validation of SEAL extension module availability
- Scalar vs vector detection in `CKKSHelper.decrypt()`
- Test skip logic to properly detect missing SEAL extension
- Build process to preserve custom `seal/__init__.py`
- CMake version requirement alignment with `CMakeLists.txt`

### Documentation
- Added comprehensive inline documentation for all utilities
- Updated README with PyPI installation instructions
- Added examples for using high-level helper classes
- Created `docs/advanced_features.md`: Complete guide to advanced features
- Created `python/advanced_features_demo.py`: Working demonstrations
- Added real-world application examples (ML inference, data aggregation, database queries)

## [4.1.2] - 2025-01-XX

### Added
- Initial Python bindings for Microsoft SEAL 4.1.2
- Support for CKKS, BFV, and BGV encryption schemes
- NumPy integration with zero-copy memory views
- Batch operations for ciphertexts
- Example scripts for all encryption schemes
- Documentation for NumPy integration
- Quick reference guide

### Features
- Full support for homomorphic operations (add, multiply, negate, square, etc.)
- Serialization and deserialization of ciphertexts and keys
- Rotation and Galois operations
- Relinearization and rescaling for CKKS
- Security levels: TC128, TC192, TC256
- Intel HEXL acceleration support

## Future Plans

### [Planned]
- Windows build support and pre-built wheels
- ARM architecture support
- Sphinx-based API documentation
- Jupyter notebook tutorials
- Performance benchmarking suite
- Additional high-level APIs for common patterns
- Async/await support for large computations
- Cloud deployment examples

---

For more information, see the [README](README.md) and [documentation](docs/).
