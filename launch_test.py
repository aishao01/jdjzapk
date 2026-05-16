import sys, os, traceback
os.chdir(r'F:\jzapk')
sys.path.insert(0, r'F:\jzapk')
log_file = r'F:\jzapk\app_output.log'
try:
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write('Starting main.py...\n')
        f.flush()
        # Redirect stdout/stderr
        old_out = sys.stdout
        old_err = sys.stderr
        sys.stdout = f
        sys.stderr = f
        import main
        sys.stdout = old_out
        sys.stderr = old_err
        f.write('main.py imported OK\n')
except Exception as e:
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f'ERROR: {e}\n')
        traceback.print_exc(file=f)
