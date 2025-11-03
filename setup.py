from setuptools import setup, find_packages

setup(
    name="polymarket-anomaly-detector",
    version="0.1.0",
    description="PolyMarket Anomaly Detection System",
    author="PolyMarket Surveillance Architect",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "polymarket-detector=src.main:main",
        ],
    },
)
