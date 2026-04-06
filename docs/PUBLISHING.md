# Publishing to PyPI

This guide explains how to publish SEAL-Python to PyPI (Python Package Index).

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - TestPyPI: https://test.pypi.org/account/register/
   - PyPI: https://pypi.org/account/register/

2. **Install Build Tools**:
   ```bash
   pip install build twine
   ```

3. **API Tokens**:
   - Generate API token from PyPI account settings
   - Store securely - you'll need it for authentication

## Building the Package

### 1. Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
./clean.sh  # Clean SEAL build artifacts
```

### 2. Ensure Microsoft SEAL is Available

```bash
# Clone SEAL if not already present
if [ ! -d "third_party/SEAL" ]; then
    git clone https://github.com/microsoft/SEAL.git third_party/SEAL
fi
```

### 3. Build Source Distribution and Wheel

```bash
# Build source distribution
python -m build --sdist

# For wheels, you may need to build on multiple platforms
# or use cibuildwheel (configured in CI/CD)
```

### 4. Check the Built Package

```bash
# Verify the package structure
twine check dist/*

# List contents of the package
tar -tzf dist/seal-python-*.tar.gz
```

## Testing on TestPyPI

Before publishing to the real PyPI, test on TestPyPI:

### 1. Upload to TestPyPI

```bash
twine upload --repository testpypi dist/*
```

When prompted:
- Username: `__token__`
- Password: Your TestPyPI API token (starts with `pypi-`)

### 2. Test Installation from TestPyPI

```bash
# Create a new virtual environment for testing
python -m venv test_env
source test_env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    seal-python

# Test the installation
python -c "import seal; print(seal.__version__)"
```

### 3. Verify Functionality

```bash
# Run the example scripts
cd python
python highlevel_ckks_example.py
python highlevel_bfv_example.py
```

## Publishing to PyPI

Once testing is successful:

### 1. Upload to PyPI

```bash
twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: Your PyPI API token

### 2. Verify on PyPI

Visit: https://pypi.org/project/seal-python/

### 3. Test Installation

```bash
pip install seal-python
```

## Automated Publishing with GitHub Actions

The repository includes a GitHub Actions workflow for automated publishing.

### Setup

1. **Add PyPI API Token to GitHub Secrets**:
   - Go to repository Settings → Secrets → Actions
   - Add new secret: `PYPI_API_TOKEN`
   - Paste your PyPI API token

2. **Create a Release**:
   ```bash
   git tag -a v4.1.5 -m "Release version 4.1.5"
   git push origin v4.1.5
   ```

3. **Publish Release on GitHub**:
   - Go to Releases → Create new release
   - Choose the tag you created
   - Write release notes (use CHANGELOG.md as reference)
   - Publish release

The CI/CD workflow will automatically:
- Build wheels for multiple platforms
- Build source distribution
- Run tests
- Publish to PyPI

## Version Management

### Updating Version

Update version in these files:
- `pyproject.toml`: `version = "x.y.z"`
- `setup.py`: `version='x.y.z'`
- `seal/__init__.py`: `__version__ = "x.y.z"`
- `CHANGELOG.md`: Add new version section

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes, backward compatible

## Troubleshooting

### Build Errors

**Problem**: CMake or C++ compilation errors

**Solution**:
- Ensure Microsoft SEAL is in `third_party/SEAL`
- Check CMake version >= 3.13
- Verify C++17 compiler is available

### Import Errors After Installation

**Problem**: `ImportError: cannot import name 'seal'`

**Solution**:
- The compiled extension (`seal.so`) must be included
- Check that `MANIFEST.in` includes necessary files
- Verify build artifacts are in the wheel

### Platform-Specific Issues

**Problem**: Package only works on the build platform

**Solution**:
- Use `cibuildwheel` for cross-platform wheels
- Build on multiple platforms (Linux, macOS, Windows)
- The GitHub Actions workflow handles this automatically

### PyPI Upload Errors

**Problem**: "File already exists" error

**Solution**:
- You cannot replace a version once uploaded
- Increment version number
- Delete and rebuild distribution files

## Best Practices

1. **Always test on TestPyPI first**
2. **Tag releases in git**: `git tag v4.1.5`
3. **Update CHANGELOG.md** before each release
4. **Test installation** in clean virtual environment
5. **Document breaking changes** in release notes
6. **Keep dependencies minimal** and version constraints loose

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [TestPyPI](https://test.pypi.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [PEP 517 - Build Backend](https://peps.python.org/pep-0517/)

## Security

**Important**: Never commit API tokens to the repository!

- Use environment variables or GitHub Secrets
- Add `.pypirc` to `.gitignore`
- Rotate tokens if accidentally exposed

## Next Steps After Publishing

1. **Announce the release**:
   - Update README with installation instructions
   - Share on relevant communities
   - Update documentation website

2. **Monitor issues**:
   - Watch for installation problems
   - Address platform-specific issues
   - Respond to user questions

3. **Plan next version**:
   - Track feature requests
   - Prioritize bug fixes
   - Update roadmap in README

---

**Questions?** Open an issue or contact the maintainer.
