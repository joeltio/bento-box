#
# Bentobox
# SDK
# Setuptools
#

import os
from setuptools import setup
from pathlib import Path


parent_dir = Path(os.getcwd()).parent
with open(os.path.join(parent_dir, "README.md"), "r") as f:
    long_description = f.read()

setup(
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    setup_requires=["pbr>=5"],
    pbr=True,
)
