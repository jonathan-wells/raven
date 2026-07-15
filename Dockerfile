FROM prefecthq/prefect:3.7.8-python3.13

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl openssh-client \
    && rm -rf /var/lib/apt/lists/
RUN curl -LsSf https://astral.sh/uv/0.11.7/install.sh | sh

WORKDIR /home/raven
COPY ./pyproject.toml ./uv.lock ./.python-version ./

RUN uv sync --no-cache --frozen --no-install-project --no-dev
ENV PATH="/home/raven/.venv/bin:$PATH"
