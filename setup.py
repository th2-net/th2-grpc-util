#   Copyright 2020-2020 Exactpro (Exactpro Systems Limited)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from setuptools import setup
from distutils.cmd import Command
import os
from pkg_resources import resource_filename
from distutils.sysconfig import get_python_lib
from setuptools.command.sdist import sdist
from distutils.dir_util import copy_tree
import shutil
from pathlib import Path
from lib2to3.main import main as convert2to3


class ProtoGenerator(Command):

    description = 'build protobuf modules'
    user_options = [('strict-mode', 's',
                     'exit with non-zero value if the proto compiling fails.')]

    def initialize_options(self):
        self.strict_mode = False

    def finalize_options(self):
        pass

    def run(self):
        proto_path = os.path.abspath('src/main/proto')
        gen_path = os.path.abspath('src/gen/main/python')

        if not os.path.exists(gen_path):
            os.makedirs(gen_path)

        proto_files = []
        for root, _, files in os.walk(proto_path):
            for filename in files:
                if filename.endswith('.proto'):
                    proto_files.append(os.path.abspath(os.path.join(root, filename)))

        protos = [('grpc_tools', '_proto')]
        protos_include = [f'--proto_path={proto_path}'] + \
                         [f'--proto_path={resource_filename(x[0], x[1])}' for x in protos] + \
                         [f'--proto_path={get_python_lib()}']

        from grpc_tools import protoc
        for proto_file in proto_files:
            command = ['grpc_tools.protoc'] + \
                      protos_include + \
                      ['--python_out={}'.format(gen_path), '--grpc_python_out={}'.format(gen_path)] + \
                      [proto_file]

            if protoc.main(command) != 0:
                if self.strict_mode:
                    raise Exception('error: {} failed'.format(command))


class CustomDist(sdist):

    def run(self):
        copy_tree(f'src/main/proto/{package_name}', f'{package_name}')

        copy_tree(f'src/gen/main/python/{package_name}', f'{package_name}')
        Path(f'{package_name}/__init__.py').touch()
        convert2to3('lib2to3.fixes', [f'{package_name}', '-w', '-n'])

        sdist.run(self)

        shutil.rmtree(package_name, ignore_errors=True)


package_name = 'grpc_util'

with open('version.info', 'r') as file:
    package_version = file.read()

with open('README.md', 'r') as file:
    long_description = file.read()


setup(
    name=package_name,
    version=package_version,
    url='https://gitlab.exactpro.com/vivarium/th2/th2-core-open-source/th2-grpc-util',
    license='Apache License 2.0',
    author='TH2-devs',
    python_requires='>=3.7',
    author_email='th2-devs@exactprosystems.com',
    description='grpc-util',
    long_description=long_description,
    packages=['', package_name],
    package_data={'': ['version.info'], package_name: ['*.proto']},
    cmdclass={
        'generate': ProtoGenerator,
        'sdist': CustomDist
    }
)
