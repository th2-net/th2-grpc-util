ARG release_version
ARG artifactory_user
ARG artifactory_password
ARG artifactory_deploy_repo_key
ARG artifactory_url

ARG pypi_repository_url
ARG pypi_user
ARG pypi_password
ARG app_name
ARG app_version

FROM gradle:6.6-jdk11 as builder
WORKDIR /home/project
ARG release_version
ARG artifactory_user
ARG artifactory_password
ARG artifactory_deploy_repo_key
ARG artifactory_url

COPY ./ .
RUN gradle --no-daemon clean build artifactoryPublish \
    -Prelease_version=${release_version} \
	-Partifactory_user=${artifactory_user} \
	-Partifactory_password=${artifactory_password} \
	-Partifactory_deploy_repo_key=${artifactory_deploy_repo_key} \
	-Partifactory_url=${artifactory_url}

FROM nexus.exactpro.com:9000/th2-python-service-generator:1.0.8.5 as generator
WORKDIR /home/project
COPY ./ .
RUN /home/th2-python-service-generator/bin/th2-python-service-generator -p src/main/proto -w PythonServiceWriter -o src/gen/main/python

FROM python:3.8-slim as python
ARG pypi_repository_url
ARG pypi_user
ARG pypi_password
ARG app_name
ARG app_version

WORKDIR /home/project
COPY --from=generator /home/project .
RUN export APP_NAME=${app_name} \
    export APP_VERSION=${app_version} \
    pip install -r requirements.txt \
    python setup.py generate \
    touch src/gen/main/python/__init__.py \
    2to3 src/gen/main/python -w -n \
    python setup.py sdist \
    twine upload --repository-url ${pypi_repository_url} --username ${pypi_user} --password ${pypi_password} dist/*