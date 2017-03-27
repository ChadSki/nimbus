@echo off
:: We only want the first line of output (default python)
:: so break out of the loop immediately.
for /f %%i in ('where pythonw') do (
    set python=%%i
    goto :endloop
)

:: Pass python's path as an argument so we can manipulate it.
:endloop
call :launchidle %python%
goto :eof

:: The ~dp1 nonsense means "the folder component of argument 1".
:launchidle
start pythonw %~dp1lib\idlelib\idle.py -e mem_example.py
goto :eof