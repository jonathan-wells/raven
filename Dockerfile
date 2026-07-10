FROM prefecthq/prefect:3.7.8-python3.13

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl openssh-client
RUN curl -LsSf https://astral.sh/uv/0.11.7/install.sh | sh
WORKDIR /home/raven
COPY ./ ./

RUN uv sync --no-cache --frozen --no-install-project --no-dev
