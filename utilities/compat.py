import sys
# Syntax sugar.
_ver = sys.version_info
#: Python 2.x?
is_py2 = (_ver[0] == 2)
#: Python 3.x?
is_py3 = (_ver[0] == 3)

if is_py3:
    from importlib import reload as cpreload
else:
    cpreload=reload
    