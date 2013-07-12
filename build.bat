@echo off
set HOME=%~dp0
set PATH=%~dp0bin\MinGW\bin;%~dp0bin\Python32
move .\c_file_cache\* .\
python .\setup.py build_ext --inplace
move .\*.c .\c_file_cache\