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
import json
from distutils.cmd import Command
import os
from pkg_resources import resource_filename
from distutils.sysconfig import get_python_lib
from setuptools.command.sdist import sdist
from distutils.dir_util import copy_tree
from shutil import rmtree
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
        copy_tree(f'src/main/proto/{package_name}', package_name)

        copy_tree(f'src/gen/main/python/{package_name}', package_name)
        Path(f'{package_name}/__init__.py').touch()
        convert2to3('lib2to3.fixes', [package_name, '-w', '-n'])

        sdist.run(self)

        rmtree(package_name, ignore_errors=True)


with open('package_info.json', 'r') as file:
    package_info = json.load(file)

package_name = package_info['package_name'].replace('-', '_')
package_version = package_info['package_version']

with open('README.md', 'r') as file:
    long_description = file.read()


setup(
    name=package_name,
    version=package_version,
    description=package_name,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='TH2-devs',
    author_email='th2-devs@exactprosystems.com',
    url='https://github.com/th2-net/th2-grpc-util',
    license='Apache License 2.0',
    python_requires='>=3.7',
    install_requires=[
        'th2-grpc-common==2.3.0'
    ],
    packages=['', package_name],
    package_data={'': ['package_info.json'], package_name: ['*.proto']},
    cmdclass={
        'generate': ProtoGenerator,
        'sdist': CustomDist
    }
)
