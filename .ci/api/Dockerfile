# # Stage 1: Build stage for dependencies
# FROM python:3.11.3
#
# WORKDIR /home/app
# COPY pyproject.toml poetry.lock ./
#
# # Set the poetry version and install it
# ENV POETRY_VERSION=1.8.3
# RUN pip install "poetry==${POETRY_VERSION}"
# RUN pip install uvicorn
# RUN poetry install
#
# WORKDIR /cargoapi
# COPY . .
#
# # Expose port 8000 and define the command to run the app
# EXPOSE 8000
#
# # Command to run the FastAPI application using Uvicorn
# CMD ["uvicorn", "cargoapi.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.11.3 as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    POETRY_VERSION=1.0.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
FROM python-base as builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential

RUN pip install poetry
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev

FROM python-base as production
ENV FASTAPI_ENV=production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY ./cargoapi /app/cargoapi/
RUN pip install uvicorn
WORKDIR /app
EXPOSE 8000
CMD ["uvicorn", "cargoapi.main:app", "--host", "0.0.0.0", "--port", "8000",  "--reload"]
