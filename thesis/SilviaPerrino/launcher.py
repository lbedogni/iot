#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess, sys

# cmd = ["python3", "sparkfunParse.py", "300"]
cmd = ["python", "sparkfunParse.py", "2"]
proc = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
proc.wait()

for x in range(2):
    # cmd = ["python3", "sparkfunParse.py", "20"]
    cmd = ["python", "sparkfunParse.py", "2"]
    proc = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
    proc.wait()
