import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="slave-irc",
    version="1.0.2",
    description="IRC based customizable botnet framework",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/bufgix/slave",
    author="bufgix",
    author_email="ooruc471@yandex.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["slave", "slave.lib"],
    include_package_data=True,
    install_requires=["pyinstaller", "mss"],
)