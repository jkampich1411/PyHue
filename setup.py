from setuptools import setup
import pathlib

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()
LICENSE = (HERE / "LICENSE").read_text()

setup(
    name="pyhue",
    version="0.0.1",
    author="Jakob K",
    description="Python library for Philips Hue",
    long_description=README,
    packages=[
        "pyhue",
    ],
    url="https://github.com/jkampich1411/pyhue",
    requires=["zeroconf", "requests", "urllib3"],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    license="MIT",
    author_email="me@jkdev.run",
)
