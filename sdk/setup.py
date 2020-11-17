#
# Bentobox
# SDK
# Setuptools
#

import os
import setuptools
from pathlib import Path


parent_dir = Path(os.getcwd()).parent
with open(os.path.join(parent_dir, "README.md"), "r") as f:
    long_description = f.read()

setuptools.setup(
    name="bento-box",  # Replace with your own username
    version="0.0.1-dev",
    author="The Bentobox Authors",
    author_email="mrzzy.dev@gmail.com",
    description="SDK for Bentobox",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joeltio/bento-box",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
