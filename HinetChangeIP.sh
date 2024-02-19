#!/usr/bin/bash


cd /root/HinetChangeIPShare

/root/HinetChangeIPShare/.venv/bin/python3 HinetChangeIP.py
# 0 3 * * * /root/HinetChangeIPShare/HinetChangeIP.sh >/dev/null 2>&1
