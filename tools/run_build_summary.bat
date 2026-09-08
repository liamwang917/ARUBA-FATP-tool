@echo off
setlocal
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py -3 "%~dp0..\src\build_summary.py" %*
) else (
    python "%~dp0..\src\build_summary.py" %*
)
echo.
pause
