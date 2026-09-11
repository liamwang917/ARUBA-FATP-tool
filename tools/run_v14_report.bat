@echo off
setlocal
pushd "%~dp0.."
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py -3 -m src.v14_main %*
) else (
    python -m src.v14_main %*
)
set EXIT_CODE=%ERRORLEVEL%
popd
echo.
pause
exit /b %EXIT_CODE%
