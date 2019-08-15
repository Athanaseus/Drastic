import os
from setuptools import setup, find_packages

pkg = 'Drastic'
build_root = os.path.dirname(__file__)


def readme():
    """Get readme content for package long description"""
    with open(os.path.join(build_root, 'README.rst')) as f:
        return f.read()


def requirements():
    """Get package requirements"""
    with open(os.path.join(build_root, 'requirements.txt')) as f:
        return [pname.strip() for pname in f.readlines()]


setup(name=pkg,
      version="0.1.0",
      description="Diverse Radio Astronomy Software Tools for Imaging and Calibration",
      long_description=readme(),
      author="Athanaseus Ramaila",
      author_email="aramaila@ska.ac.za",
      packages=find_packages(),
      url="https://github.com/Athanaseus/Drastic",
      license="GNU GPL 3",
      classifiers=["Intended Audience :: Developers",
                   "Programming Language :: Python :: 3",
                   "Topic :: Scientific/Engineering :: Astronomy",
                   "Topic :: Software Development :: Libraries :: Python Modules"],
      platforms=["OS Independent"],
      install_requires=requirements())
