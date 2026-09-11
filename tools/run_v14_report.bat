@echo off
setlocal
pushd "%~dp0.."

echo.
echo ARUBA FATP V14.5 RC - Operational UAT
echo Select ARUBA_MIC and/or ARUBA_PREMIC archives. RawData_RD is optional.
echo The bundled clean template is used automatically.
echo Generated Excel files are written to the report folder.
echo.

if not "%~1"=="" (
    echo This UAT launcher accepts no arguments.
    echo For developer CLI overrides, run: py -3 -m src.v14_main --help
    set "EXIT_CODE=2"
    goto :finish
)

if exist "templates\Post-MIC limit_20260911.xlsx" goto :run
echo ERROR: Bundled template is missing: templates\Post-MIC limit_20260911.xlsx
echo Reinstall the V14.5 RC package. Do not select a substitute template.
set "EXIT_CODE=2"
goto :finish

:run
if not exist "report" mkdir "report"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -m src.v14_main
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo ERROR: Python 3 was not found. Install Python 3, then run:
        echo        py -3 -m pip install -r requirements.txt
        set "EXIT_CODE=2"
        goto :finish
    )
    python -m src.v14_main
)
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
    echo.
    echo V14.5 RC did not complete. Review the error above and retry.
    goto :finish
)
echo.
echo V14.5 RC completed. Summary and report workbooks are in the report folder.

:finish
popd
echo.
pause
exit /b %EXIT_CODE%
