#!/bin/sh
python3 -m venv .venv
. ./.venv/bin/activate
pip install -r requirements.txt
python3 utils/install.py
