#!/usr/bin/bash


cd /root/HinetChangeIPShare

/root/HinetChangeIPShare/.venv/bin/python3 HinetCheckNF.py
# */30 * * * * /root/HinetChangeIPShare/HinetCheckNF.sh >/dev/null 2>&1
