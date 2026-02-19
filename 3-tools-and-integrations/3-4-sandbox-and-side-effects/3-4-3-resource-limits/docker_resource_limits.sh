#!/bin/bash

docker run --rm \
  --memory="256m" \
  --memory-swap="256m" \
  --cpus="1.0" \
  --cpu-shares="512" \
  --pids-limit="100" \
  --network="none" \
  my_sandbox_image python3 script.py
