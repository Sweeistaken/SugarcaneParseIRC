from setuptools import setup, find_packages

VERSION = '1.0.0' 
DESCRIPTION = 'IRC parser for the Sugarcane IM family.'
LONG_DESCRIPTION = open('README.md').read()

setup(
        name="scparseirc", 
        version=VERSION,
        author="SweeZero",
        author_email="swee@mailfence.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ]
)
