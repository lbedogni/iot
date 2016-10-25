#!/usr/bin/python3

import time
from datetime import date, timedelta

yesterday = (date.today() - timedelta(1)).strftime('%d.%m.%Y')
provinces = ["PR", "RE", "PC", "MO", "BO", "FE", "RA", "FC", "RN"]

for PR in provinces:
	prCmd = ["python3", "getARPAE.py", PR, yesterday, yesterday]
    prProc = subprocess.Popen(prCmd, stdout=sys.stdout, stderr=sys.stderr)
    prProc.wait()

