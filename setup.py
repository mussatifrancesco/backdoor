from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name='backdoor',
    version='0.1.0',
    description='Multi-Platform C2 & Reverse Shell Framework',
    author='mussatifrancesco',
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'backdoor-server=bin.server:main',
        ],
    },
)