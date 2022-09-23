from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
setup(
    name="py3-PyHue",
    version="0.1a6",
    author="Jakob K",
    description="Python3 Module for controlling Philips Hue lights",
    long_description=(HERE / "README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=[".cached*"]),
    url="https://github.com/jkampich1411/PyHue",
    requires=["zeroconf", "requests"],
    install_requires=["zeroconf", "requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    license="MIT",
    author_email="me@jkdev.run",
)
