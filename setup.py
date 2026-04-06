"""
Setup script for SEAL-Python.

This script handles building the C++ extension module using CMake.
Modern packaging metadata is in pyproject.toml.
"""
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import subprocess
import os
import sys


class CMakeExtension(Extension):
    """Extension class for CMake-based builds."""

    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    """Custom build_ext command for building with CMake."""

    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            '-DSEAL_USE_INTEL_HEXL=ON',
            '-DSEAL_BUILD_TESTS=ON',
            '-DSEAL_BUILD_EXAMPLES=ON',
            '-DSEAL_BUILD_SEAL_C=ON'
        ]

        build_args = []

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)


# Main setup - metadata comes from pyproject.toml
setup(
    name='seal-python',
    version='4.1.5',
    author='Chandradutt Patel',
    author_email='cnpatel5746@gmail.com',
    description='Python bindings for Microsoft SEAL - Homomorphic Encryption Library',
    long_description=open('README.md', encoding='utf-8').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/chandradutt5746/SEAL-PYTHON-4.1.5',
    project_urls={
        'Bug Tracker': 'https://github.com/chandradutt5746/SEAL-PYTHON-4.1.5/issues',
        'Documentation': 'https://github.com/chandradutt5746/SEAL-PYTHON-4.1.5/blob/main/README.md',
        'Source Code': 'https://github.com/chandradutt5746/SEAL-PYTHON-4.1.5',
    },
    ext_modules=[CMakeExtension('seal.seal')],
    cmdclass=dict(build_ext=CMakeBuild),
    packages=['seal'],
    package_dir={'seal': 'seal'},
    zip_safe=False,
    python_requires='>=3.8',
    install_requires=[
        'numpy>=1.19.0',
        'pybind11>=2.6.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'isort>=5.12.0',
            'mypy>=1.0.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.2.0',
            'myst-parser>=1.0.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: C++',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Security :: Cryptography',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='homomorphic-encryption cryptography privacy seal microsoft-seal ckks bfv bgv fhe',
    license='MIT',
)
