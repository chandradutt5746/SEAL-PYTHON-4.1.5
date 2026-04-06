# Changelog

All notable changes to SEAL-Python will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.1.5] - 2026-04-06

### Added
- Modern PyPI-ready package structure with `pyproject.toml`
- High-level Python wrapper API with `CKKSHelper` and `BFVHelper` classes
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

### Changed
- Updated package metadata for PyPI publication
- Improved seal/__init__.py with better error handling and imports
- Enhanced README.md with PyPI installation instructions
- Version bumped to 4.1.5 for new feature release

### Fixed
- Better error messages when SEAL extension is not built
- Improved import handling in the seal package

### Documentation
- Added comprehensive inline documentation for all utilities
- Updated README with PyPI installation instructions
- Added examples for using high-level helper classes

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
