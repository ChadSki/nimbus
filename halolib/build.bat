@echo off

REM Adjust paths
pushd %~dp0
set HOME=..\
set PATH=..\bin\MinGW\bin;..\bin\Python33

del *.pyd
python .\setup.py build_ext --inplace
del *.c

REM Restore cwd
popd
