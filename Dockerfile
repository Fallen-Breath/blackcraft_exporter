ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim AS builder
ARG POETRY_VERSION=2.1.1

RUN pip3 install --no-cache-dir poetry==${POETRY_VERSION} poetry-plugin-export
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry export --output=requirements.txt && cat ./requirements.txt


FROM python:${PYTHON_VERSION}-slim

WORKDIR /app
COPY --from=builder /app/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./blackcraft_exporter ./blackcraft_exporter
ENTRYPOINT ["python3", "-um", "blackcraft_exporter"]
