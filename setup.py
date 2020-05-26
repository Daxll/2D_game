import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
additional_modules = []

build_exe_options = {"includes": additional_modules,
                     "packages": ["pygame", "os", "sys"],}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="Jumper",
      version="1.2",
      description="Jump around",
      options={"build_exe": build_exe_options},
      executables=[Executable(script="base.py", base=base)])