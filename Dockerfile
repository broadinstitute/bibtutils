FROM python:3.8

WORKDIR /usr/src
COPY bibtutils bibtutils
COPY setup.cfg .
COPY setup.py .
COPY pyproject.toml .
COPY MANIFEST.in .

RUN [ "python3", "setup.py", "install" ]
RUN [ "pip", "install", "pytest" ]
RUN [ "pip", "install", "protobuf"]
COPY pytest.ini .
COPY tests tests

ARG CREDS_FILE=./creds/service_account.json
COPY $CREDS_FILE /usr/creds/creds.json

CMD [ "pytest", "tests/" ]
