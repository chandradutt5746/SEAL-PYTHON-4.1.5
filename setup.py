"""
Setup script for SEAL-Python.

This script handles building the C++ extension module using CMake.
All package metadata is defined in pyproject.toml.
"""
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import subprocess
import os


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


# Main setup - all metadata comes from pyproject.toml
setup(
    ext_modules=[CMakeExtension('seal.seal')],
    cmdclass=dict(build_ext=CMakeBuild),
)
