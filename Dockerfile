FROM node:22-bookworm

ARG CODEX_VERSION=latest

ENV DEBIAN_FRONTEND=noninteractive
ENV CODEX_HOME=/codex-home

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    file \
    git \
    jq \
    less \
    pandoc \
    poppler-utils \
    python3 \
    python3-pip \
    python3-venv \
    qpdf \
    ripgrep \
    tesseract-ocr \
    tree \
    unzip \
    vim-tiny \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g "@openai/codex@${CODEX_VERSION}" \
    && npm cache clean --force

RUN useradd --create-home --shell /bin/bash codex \
    && mkdir -p /work "$CODEX_HOME" \
    && printf '%s\n' \
        'model = "gpt-5.5"' \
        'model_provider = "openai"' \
        'model_reasoning_effort = "xhigh"' \
        'plan_mode_reasoning_effort = "xhigh"' \
        'model_verbosity = "medium"' \
        > "$CODEX_HOME/config.toml" \
    && chown -R codex:codex /work "$CODEX_HOME"

USER codex
WORKDIR /work

CMD ["codex", "--cd", "/work"]
