FROM gcc:14

WORKDIR /work

RUN apt-get update && apt-get install -y --no-install-recommends \
    coreutils \
    time \
    && rm -rf /var/lib/apt/lists/*

CMD ["bash"]