#!/usr/bin/env bash
cd "$(dirname "$0")"
pip install -q -r requirements.txt
uvicorn app.main:app --reload --port 8000
