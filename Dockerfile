FROM ubuntu:24.04

SHELL ["/bin/bash", "-c"]

RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt update && \
    apt install -y espeak-ng ffmpeg python3 python3-pip python3-venv

COPY epub2tts_edge/epub2tts_edge.py requirements.txt setup.py /app/

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m venv .venv && \
    source .venv/bin/activate && \
    pip install .

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT [ "python","epub2tts_edge.py" ]

CMD ["--help"]
