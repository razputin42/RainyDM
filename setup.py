import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "excludes": ["tkinter"], "include_files": [("assets", "assets"), ("RainyDB/5", "RainyDB/5")], "optimize": 2}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "RainyDM",
        version = "1.7",
        description = "The DM tool you've always needed!",
        options = {"build_exe": build_exe_options},
        executables = [Executable("RainyDM.py", base=base)])