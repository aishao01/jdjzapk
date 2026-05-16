import subprocess, sys, os
os.chdir(r'F:\jzapk')
with open(r'F:\jzapk\app_output.log', 'w', encoding='utf-8') as f:
    p = subprocess.Popen(
        [r'C:\Program Files\Python312\python.exe', 'main.py'],
        stdout=f, stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    print(f'PID: {p.pid}')
    sys.exit(0)
