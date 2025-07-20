from setuptools import setup, find_packages

setup(
    name="my-utils",
    version="1.0.0",
    author="Portia210",
    description="A collection of reusable utility functions",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pytz>=2021.1",
    ],
) 