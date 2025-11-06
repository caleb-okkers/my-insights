import runpy
import sys

try:
    runpy.run_path(r'c:\Users\rabot\repos\my-insights\dashboard\app.py', run_name='__main__')
    print('RUN_OK')
except Exception as e:
    print('EXC:', type(e).__name__, e)
    sys.exit(1)
