"""
Setup script for Advanced DeFi Portfolio Manager

Handles installation and configuration of the portfolio management system.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="advanced-defi-portfolio-manager",
    version="1.0.0",
    author="JuliaOS Community",
    author_email="community@juliaos.org",
    description="Advanced DeFi Portfolio Manager powered by JuliaOS AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JuliaOScode/JuliaOS",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "dashboard": [
            "streamlit>=1.28.0",
            "plotly>=5.17.0",
            "dash>=2.14.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "defi-portfolio=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
