#!/bin/bash

cd ${PWD}/backend \
    && source .venv/bin/activate \
    &&  uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload --log-level info