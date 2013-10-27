@echo off
set HOME=%~dp0..\
set PATH=%~dp0..\bin\MinGW\bin;%~dp0..\bin\Python33
del *.pyd
python .\setup.py build_ext --inplace
del *.c
