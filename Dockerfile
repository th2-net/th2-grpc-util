FROM gradle:6.6-jdk11 as builder
WORKDIR /home/grpc-generator
COPY . .
RUN gradle clean publish

FROM nexus.exactpro.com:9000/th2-python-service-generator:1.0.8.5 as generator
WORKDIR /home/grpc-generator
COPY --from=builder /home/grpc-generator .
RUN /home/th2-python-service-generator/bin/th2-python-service-generator -p ./src/main/proto -w PythonServiceWriter -o ./src/gen/main/python

FROM python:3.8-slim as python
ARG PYPI_REPOSITORY_URL
ARG PYPI_USER
ARG PYPI_PASSWORD
ARG app_name
ARG app_version
WORKDIR /home/grpc-generator
COPY --from=generator /home/grpc-generator .
RUN pip install -U twine
RUN python setup.py generate
RUN python setup.py sdist
RUN twine upload --repository-url ${PYPI_REPOSITORY_URL} --username ${PYPI_USER} --password ${PYPI_PASSWORD} dist/*