from setuptools import setup, find_packages

setup(
    name="myspikesorter",
    version="0.1.0",
    description="A basic spike sorter for testing SpikeInterface integration",
    packages=find_packages(where="."),  # Look in current directory
    package_dir={"": "."},              # Packages are in current directory
    install_requires=[
        "numpy",
    ],
    python_requires=">=3.7",
)
