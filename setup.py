from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
setup(
    name="py3-PyHue",
    version="0.1a1",
    author="Jakob K",
    description="Python3 library for Philips Hue",
    long_description=(HERE / "README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=[".cached*"]),
    url="https://github.com/jkampich1411/PyHue",
    requires=["zeroconf", "requests"],
    install_requires=["zeroconf", "requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    license="https://jkdev.mit-license.org/",
    author_email="me@jkdev.run",
)
