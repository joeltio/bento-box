#
# Bentobox
# SDK
# Setuptools
#

import os
from setuptools import setup
from distutils.cmd import Command
from distutils.command.clean import clean
from setuptools.command.build_py import build_py
from pathlib import Path
from grpc_tools import protoc
from shutil import rmtree


class GenProtos(Command):
    __doc__ = """
    Custom command to generate Python Protobuf bindings
    """
    description = __doc__
    command_name = "build_protos"
    user_options = []

    protos_dir = Path("..") / "protos"
    binds_dir = Path(".") / "bento" / "protos"

    # Empty implementation to statisfy abstract Command class requirements
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        proto_glob = (GenProtos.protos_dir / "bento" / "protos").glob("*.proto")
        proto_paths = [str(p) for p in proto_glob]
        os.makedirs(GenProtos.binds_dir, exist_ok=True)
        if self.verbose:
            print(f"compling python protobuf bindings to {GenProtos.binds_dir}")
        # generate python proto bindings with protoc
        protoc.main(
            [
                __file__,
                f"-I{GenProtos.protos_dir}",
                f"--python_out=.",
                f"--grpc_python_out=.",
            ]
            + proto_paths
        )
        # create a __init__.py to to tell python to treat it as a package
        (GenProtos.binds_dir / "__init__.py").touch()


class ProtoBuildPy(build_py):
    """
    Custom Build step to generate protobuf bindings before build
    """

    command_name = "build_py"

    def run(self):
        # run protoc to compile bindings form proto defintions
        self.run_command("build_protos")
        super().run()


class ProtoClean(clean):
    """
    Custom Clean step to remove generated protobuf bindings during clean.
    """

    command_name = "clean"

    def run(self):
        if os.path.exists(GenProtos.binds_dir):
            if self.verbose:
                print(f"removing python protobuf bindings at {GenProtos.binds_dir}")
            rmtree(GenProtos.binds_dir)
        super().run()


if __name__ == "__main__":
    # if main required to prevent setup.py from running twice
    setup(
        python_requires=">=3.6",
        setup_requires=["pbr>=5"],
        pbr=True,
    )
