#
# Bentobox
# SDK
# Setuptools
#

import os
from setuptools import setup
from distutils.cmd import Command
from setuptools.command.build_py import build_py
from pathlib import Path
from grpc_tools import protoc


class GenProtos(Command):
    __doc__ = """
    Custom command to generate Python Protobuf bindings
    """
    description = __doc__
    command_name = "build_protos"
    user_options = []

    def initialize_options(self):
        self.protos_dir = str(Path("..") / "protos")
        self.binds_dir = str(Path(".") / "bento" / "protos")

    def finalize_options(self):
        self.protos_dir = Path(self.protos_dir)
        self.binds_dir = Path(self.binds_dir)

    def run(self):
        proto_paths = [ str(p) for p in self.protos_dir.glob("*.proto") ]
        os.makedirs(self.binds_dir, exist_ok=True)
        if self.verbose:
            print(f"compling python protobuf bindings to {self.binds_dir}")
        # generate python proto bindings with protoc
        protoc.main([
            __file__,
            f"-I{self.protos_dir}",
            f"--python_out={self.binds_dir}",
            f"--grpc_python_out={self.binds_dir}"
        ] + proto_paths)
        # create a __init__.py to to tell python to treat it as a package
        (self.binds_dir / "__init__.py").touch()

class ProtoBuildPy(build_py):
    """
    Custom Build step to generate protobuf bindings before build
    """
    command_name = "build_py"

    def run(self):
        # run protoc to compile bindings form proto defintions
        self.run_command("build_protos")
        super().run()

setup(
    python_requires=">=3.6",
    setup_requires=["pbr>=5"],
    pbr=True,
)
