@echo off
setlocal
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py -3 "%~dp0..\src\build_summary_windows_v12_calc.py" %*
) else (
    python "%~dp0..\src\build_summary_windows_v12_calc.py" %*
)
echo.
pause
