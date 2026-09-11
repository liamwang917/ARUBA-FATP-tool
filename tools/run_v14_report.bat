@echo off
setlocal
pushd "%~dp0.."
echo.
echo ARUBA FATP V14.5 RC - Operational UAT
echo Select ARUBA_MIC and/or ARUBA_PREMIC archives. RawData_RD is optional.
echo The approved template is loaded automatically from templates\Post-MIC limit_EV3_20260911.xlsx.
echo.
if not "%~1"=="" (
    echo This UAT launcher accepts no arguments.
    echo For developer CLI overrides, run: py -3 -m src.v14_main --help
    set EXIT_CODE=2
    goto :finish
)
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py -3 -m src.v14_main
) else (
    python -m src.v14_main
)
set EXIT_CODE=%ERRORLEVEL%
:finish
popd
echo.
pause
exit /b %EXIT_CODE%
