# Contributing to SEAL-Python

Thank you for your interest in contributing to SEAL-Python! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project aims to foster an inclusive and respectful community. By participating, you are expected to:

- Be respectful and considerate in your communication
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect different viewpoints and experiences

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/SEAL-PYTHON-4.1.5.git
   cd SEAL-PYTHON-4.1.5
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/chandradutt5746/SEAL-PYTHON-4.1.5.git
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- C++17 compatible compiler (GCC >= 7, Clang >= 5)
- CMake >= 3.13
- Git

### Setting Up Your Environment

1. **Create a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"  # Install in editable mode with dev dependencies
   ```

3. **Clone Microsoft SEAL**:
   ```bash
   git clone https://github.com/microsoft/SEAL.git third_party/SEAL
   ```

4. **Build the extension**:
   ```bash
   chmod +x build.sh
   ./build.sh
   ```

5. **Run tests** to verify everything works:
   ```bash
   pytest tests/ -v
   ```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Fix issues in the existing code
- **New features**: Add new functionality or improvements
- **Documentation**: Improve docs, examples, or tutorials
- **Tests**: Add or improve test coverage
- **Performance**: Optimize existing code
- **Examples**: Create new example scripts or notebooks

### Development Workflow

1. **Create a new branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes** following the coding standards below

3. **Test your changes**:
   ```bash
   pytest tests/ -v
   ```

4. **Commit your changes** with clear commit messages:
   ```bash
   git add .
   git commit -m "Add feature: description of what you did"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## Coding Standards

### Python Code

- Follow [PEP 8](https://pep8.org/) style guide
- Use **Black** for code formatting (line length: 100)
- Use **isort** for import sorting
- Use type hints where appropriate
- Write docstrings for all public functions and classes

### C++ Code

- Follow existing code style in the project
- Use C++17 features appropriately
- Comment complex logic
- Keep functions focused and reasonably sized

### Formatting Your Code

Before submitting, format your code:

```bash
# Format Python code
black seal/ tests/
isort seal/ tests/

# Check types
mypy seal/
```

### Documentation

- Update README.md if adding new features
- Add docstrings to new functions and classes
- Update relevant documentation in docs/
- Add examples for new features

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=seal --cov-report=html

# Run specific test file
pytest tests/test_ckks.py -v
```

### Writing Tests

- Add tests for all new features
- Follow existing test patterns in `tests/`
- Use pytest fixtures for common setup
- Name test functions clearly: `test_<functionality>`

Example test structure:

```python
def test_new_feature():
    """Test description of what is being tested."""
    # Setup
    helper = CKKSHelper()

    # Action
    result = helper.new_feature(input_data)

    # Assert
    assert result == expected_value
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass** locally
4. **Update CHANGELOG.md** under the "Unreleased" section
5. **Create PR** with a clear description of changes

### PR Description Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
Describe the tests you ran and their results

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Review Process

- Maintainers will review your PR
- Address any requested changes
- Once approved, your PR will be merged

## Reporting Bugs

When reporting bugs, please include:

1. **Clear title** describing the issue
2. **Steps to reproduce** the bug
3. **Expected behavior** vs actual behavior
4. **Environment details**:
   - OS and version
   - Python version
   - SEAL-Python version
   - Relevant dependencies
5. **Code sample** or minimal reproducible example
6. **Error messages** or stack traces

Use the GitHub issue tracker: https://github.com/chandradutt5746/SEAL-PYTHON-4.1.5/issues

## Suggesting Enhancements

We welcome enhancement suggestions! Please include:

1. **Clear description** of the proposed feature
2. **Use case**: Why is this enhancement useful?
3. **Possible implementation** (if you have ideas)
4. **Examples** of how it would be used
5. **Alternatives considered**

## Questions?

- Open an issue on GitHub
- Contact the maintainer: [Chandradutt Patel](https://www.linkedin.com/in/cnpatel5746/)

## License

By contributing to SEAL-Python, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to SEAL-Python!** Your efforts help make homomorphic encryption more accessible to the Python community.
