# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 4.1.5   | :white_check_mark: |
| 4.1.x   | :white_check_mark: |
| < 4.1   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in SEAL-Python, please follow these steps:

### 1. Email the Maintainer

Send an email to **cnpatel5746@gmail.com** with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

Please include "SECURITY" in the subject line.

### 2. Wait for Response

You should receive a response within 48 hours acknowledging your report.

### 3. Coordinated Disclosure

We follow coordinated disclosure:

- We'll work with you to understand and validate the issue
- We'll develop and test a fix
- We'll prepare a security advisory
- We'll release the fix and advisory together

**Please give us reasonable time to address the issue before public disclosure.**

## What We Consider Security Vulnerabilities

Examples of security issues:

- **Cryptographic weaknesses**: Flaws in encryption implementation
- **Key exposure**: Unintentional exposure of secret keys
- **Memory safety**: Buffer overflows, use-after-free
- **Injection vulnerabilities**: Code injection, command injection
- **Denial of Service**: Resource exhaustion attacks
- **Authentication bypass**: Unauthorized access to encrypted data

## What We Don't Consider Security Vulnerabilities

- **Theoretical cryptographic attacks**: Unless practically exploitable
- **Issues in dependencies**: Report to the upstream project
- **Social engineering**: Not applicable to a library
- **Physical attacks**: Out of scope

## Security Best Practices for Users

When using SEAL-Python:

1. **Protect Secret Keys**
   - Never log secret keys
   - Never transmit secret keys in plain text
   - Use secure key storage mechanisms
   - Rotate keys periodically

2. **Parameter Selection**
   - Use appropriate security levels (TC128, TC192, TC256)
   - Consult Microsoft SEAL documentation for parameter guidelines
   - Don't use weak parameters for production

3. **Dependency Management**
   - Keep SEAL-Python updated
   - Monitor security advisories
   - Update Microsoft SEAL to latest version

4. **Code Review**
   - Review cryptographic code carefully
   - Validate all inputs
   - Use constant-time operations where applicable

5. **Testing**
   - Test thoroughly before production use
   - Verify decryption results
   - Check noise budget management

## Known Limitations

SEAL-Python is a binding for Microsoft SEAL. Security considerations:

1. **Side-channel attacks**: Timing attacks may be possible
2. **Implementation correctness**: Depends on correct parameter usage
3. **Not intended for production use without security review**

## Updates and Advisories

Security updates will be:
- Published in GitHub Security Advisories
- Announced in release notes
- Posted on the repository README

## Bug Bounty

We currently do not offer a bug bounty program. However, we deeply appreciate security researchers who report vulnerabilities responsibly.

## Acknowledgments

We thank security researchers who have helped improve SEAL-Python's security.

## Contact

For security concerns: **cnpatel5746@gmail.com**

For general questions: Open a GitHub issue

---

**Thank you for helping keep SEAL-Python secure!**
