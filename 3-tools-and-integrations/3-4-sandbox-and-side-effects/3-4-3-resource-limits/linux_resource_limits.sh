#!/bin/bash

firejail \
  --cpu=0,1 \
  --rlimit-as=256000000 \
  --private \
  --net=none \
  --timeout=00:05:00 \
  python3 script.py
