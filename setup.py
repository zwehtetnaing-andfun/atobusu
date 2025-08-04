"""
Setup script for Atobusu application.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="atobusu",
    version="1.0.0",
    author="Atobusu Development Team",
    description="Auto HTML Generator for structured data processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "pyqt5": ["PyQt5>=5.15.0"],
        "dev": ["pytest>=7.0.0", "pytest-cov>=4.0.0", "black>=22.0.0", "flake8>=5.0.0"],
    },
    entry_points={
        "console_scripts": [
            "atobusu=atobusu.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "atobusu": ["templates/*", "config/*"],
    },
)