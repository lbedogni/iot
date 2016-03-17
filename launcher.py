import subprocess, sys

cmd = ["python3", "sparkfunParse.py", "300"]
proc = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
proc.wait()

for x in range(15):
	cmd = ["python3", "sparkfunParse.py", "20"]
	proc = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
	proc.wait()
