FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY acs_conformance ./acs_conformance
COPY packs ./packs
RUN pip install --no-cache-dir . && useradd --uid 10001 runner
USER 10001
ENTRYPOINT ["acs-conformance"]
