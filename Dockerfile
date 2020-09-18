FROM gradle:6.6-jdk11 as builder
WORKDIR /home/grpc-generator
COPY . .
RUN gradle clean publish

FROM nexus.exactpro.com:9000/th2-python-service-generator:1.0.7.4 as generator
WORKDIR /home/grpc-generator
COPY --from=builder /home/grpc-generator .
RUN /home/th2-python-service-generator/bin/th2-python-service-generator -p ./src/main/proto -w PythonServiceWriter -o ./src/gen/main/python

FROM python:3.8-slim as python
WORKDIR /home/grpc-generator
COPY --from=generator /home/grpc-generator .
RUN pip install .
RUN python setup.py build_proto_modules
RUN twine upload ...