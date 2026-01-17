from setuptools import setup, find_packages

setup(
    name="proton-cli",
    version="2.1.3",
    description="Command line tool for managing Proton versions and Wine prefixes",
    author="hhadi34",
    url="https://github.com/hhadi34/proton-cli",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "proton-cli=proton_cli.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
)