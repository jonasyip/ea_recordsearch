from setuptools import setup, find_packages

setup(
    name="earecordsearch",
    version="0.1",
    description="Environment Agency (EA) record search",
    url="https://github.com/jonasyip/earecordsearch",
    packages=find_packages(),
    install_requires=["datetime", "pandas", "requests"],
)