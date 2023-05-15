@echo off
GOTO:MAIN

:cleanup
    rmdir  /s /q build
    rmdir  /s /q dist
    rmdir  /s /q JSON_RPC_Protocol.egg-info
EXIT /B 0

:build
    call:cleanup
    call python -m pip install --upgrade build
    call python -m build
EXIT /B %ERRORLEVEL%

:install
    call:build
    call pip install .
EXIT /B %ERRORLEVEL%

:MAIN
IF NOT "%~1" == "" call:%1