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

from distutils.cmd import Command
import os
import pkg_resources
from setuptools import setup, find_packages


class BuildPackageProtos(Command):

    description = 'build proto protobuf modules'
    user_options = [('strict-mode', 's',
                     'exit with non-zero value if the proto compiling fails.')]

    def initialize_options(self):
        self.strict_mode = False

    def finalize_options(self):
        pass

    def run(self):
        proto_path = os.path.abspath('src/main/proto')
        gen_path = os.path.abspath('src/gen/main/python')

        proto_files = []
        for root, _, files in os.walk(proto_path):
            for filename in files:
                if filename.endswith('.proto'):
                    proto_files.append(os.path.abspath(os.path.join(root, filename)))

        well_known_protos_include = pkg_resources.resource_filename('grpc_tools', '_proto')

        from grpc_tools import protoc
        for proto_file in proto_files:
            command = [
                          'grpc_tools.protoc',
                          '--proto_path={}'.format(proto_path),
                          '--proto_path={}'.format(well_known_protos_include),
                          '--python_out={}'.format(gen_path),
                          '--grpc_python_out={}'.format(gen_path),
                      ] + [proto_file]
            if protoc.main(command) != 0:
                if self.strict_mode:
                    raise Exception('error: {} failed'.format(command))


gen_path = os.path.abspath('src/gen/main/python')
if not os.path.exists(gen_path):
    os.mkdir(gen_path)

setup(
    name='grpc-generator-template',
    version=f"1.1.1",
    install_requires=[
        'grpcio-tools',
        'google-api-core',
        'twine'
    ],
    url='https://gitlab.exactpro.com/vivarium/th2/th2-core-open-source/grpc-generator-template',
    license='Apache License 2.0',
    author='TH2-devs',
    python_requires='>=3.7',
    author_email='th2-devs@exactprosystems.com',
    description='TH2-common-python',
    # long_description=open('README.md').read(),
    packages=['proto', 'gen'],
    package_dir={'proto': 'src/main/proto', 'gen': 'src/gen/main/python'},
    package_data={'proto': ['*.proto']},
    cmdclass={
        'build_proto_modules': BuildPackageProtos,
    }
)
