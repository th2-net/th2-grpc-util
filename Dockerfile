FROM gradle:6.6-jdk11 as builder
WORKDIR /home/grpc-generator-template
COPY . .
RUN gradle publish

FROM nexus.exactpro.com:9000/th2-python-service-generator:1.0.8.5 as generator
WORKDIR /home/grpc-generator-template
COPY --from=builder /home/grpc-generator-template .
RUN /home/th2-python-service-generator/bin/th2-python-service-generator -p src/main/proto -w PythonServiceWriter -o src/gen/main/python

FROM python:3.8-slim as python
ARG PYPI_REPOSITORY_URL
ARG PYPI_USER
ARG PYPI_PASSWORD
WORKDIR /home/grpc-generator-template
COPY --from=generator /home/grpc-generator-template .
RUN pip install -r requirements.txt
RUN python setup.py generate
RUN touch src/gen/main/python/__init__.py
RUN 2to3 src/gen/main/python -w -n
RUN python setup.py sdist
RUN twine upload --repository-url ${PYPI_REPOSITORY_URL} --username ${PYPI_USER} --password ${PYPI_PASSWORD} dist/*