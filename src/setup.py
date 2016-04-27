from cx_Freeze import *

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ['PyQt4.QtGui','PyQt4.QtCore','datetime','pandas','tushare','talib','os','sys','json'], excludes = ['collections.abc'])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('MainWindow.py', base=base)
]

setup(
    name='Tetris',
    version = '0.1',
    description = 'A PyQt Tetris Program',
    options = dict(build_exe = buildOptions),
    executables = executables
)