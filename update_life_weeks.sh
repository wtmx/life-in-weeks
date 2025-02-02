#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python life.py
deactivate 