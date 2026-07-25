@echo off
REM ============================================================================
REM SoftDent Autorun — New Ridge Family Dental
REM ============================================================================
REM This batch script runs the SoftDent export converter.
REM You can run it manually or schedule it with Windows Task Scheduler.
REM
REM SETUP:
REM   1. Edit the paths below to match your SoftDent export folder
REM   2. Test by double-clicking this file
REM   3. For automation, schedule it in Windows Task Scheduler (see SOFTDENT_SETUP.md)
REM ============================================================================

setlocal EnableDelayedExpansion

REM --- CONFIGURE THESE PATHS ---
REM Path where SoftDent exports its CSV files (usually set in SoftDent export dialog)
set "EXPORT_DIR=C:\softdent\exports"

REM Path to this project folder (where radiographs.html lives)
set "PROJECT_DIR=%~dp0"

REM Path to Python (leave as "python" if Python is in your PATH)
set "PYTHON=python"

REM Output directory (relative to project)
set "OUTPUT_DIR=%PROJECT_DIR%data"

REM Patient CSV filename pattern (adjust if your exports use different names)
set "PATIENT_PATTERN=*patient*.csv"
set "PROCEDURE_PATTERN=*procedure*.csv"

REM Enable analysis stub generation? (yes/no)
set "STUB_ANALYSIS=yes"
REM ==============================

REM --- LOGGING ---
set "LOGFILE=%PROJECT_DIR%softdent-run.log"
echo [%date% %time%] SoftDent autorun started >> "%LOGFILE%"

REM --- FIND FILES ---
set "PATIENT_FILE="
set "PROCEDURE_FILE="

for %%F in ("%EXPORT_DIR%\%PATIENT_PATTERN%") do (
    if "!PATIENT_FILE!"=="" (
        set "PATIENT_FILE=%%F"
    ) else (
        REM Keep the most recently modified file
        for %%A in ("!PATIENT_FILE!") do set "OLD=%%~tA"
        for %%B in ("%%F") do set "NEW=%%~tB"
        REM Simple string comparison (works for same-day; for robust use python watcher)
        if "!NEW!" gtr "!OLD!" set "PATIENT_FILE=%%F"
    )
)

for %%F in ("%EXPORT_DIR%\%PROCEDURE_PATTERN%") do (
    if "!PROCEDURE_FILE!"=="" (
        set "PROCEDURE_FILE=%%F"
    )
)

if "%PATIENT_FILE%"=="" (
    echo ERROR: No patient export file found in %EXPORT_DIR% matching %PATIENT_PATTERN%
    echo [%date% %time%] ERROR: No patient file found >> "%LOGFILE%"
    pause
    exit /b 1
)

echo Found patient file: %PATIENT_FILE%
if not "%PROCEDURE_FILE%"=="" echo Found procedure file: %PROCEDURE_FILE%

REM --- BUILD ARGUMENTS ---
set "ARGS=--patients "%PATIENT_FILE%" --output "%OUTPUT_DIR%"

if not "%PROCEDURE_FILE%"=="" (
    set "ARGS=%ARGS% --procedures "%PROCEDURE_FILE%"
)

if /I "%STUB_ANALYSIS%"=="yes" (
    set "ARGS=%ARGS% --stub-analysis"
)

REM --- RUN CONVERTER ---
cd /d "%PROJECT_DIR%"
echo Running converter...
%PYTHON% softdent-converter.py %ARGS%

if errorlevel 1 (
    echo [%date% %time%] Converter FAILED >> "%LOGFILE%"
    echo.
    echo Conversion failed. See log: %LOGFILE%
    pause
    exit /b 1
)

echo [%date% %time%] Converter OK >> "%LOGFILE%"

REM --- OPTIONAL: Auto-commit and push to GitHub ---
REM Uncomment the lines below if you want automatic deployment.
REM Make sure git is in your PATH and credentials are cached.
REM
echo.
echo Pushing to GitHub...
git add data/
git commit -m "Auto-update: SoftDent export %date% %time%"
git push origin HEAD
echo [%date% %time%] Pushed to GitHub >> "%LOGFILE%"
REM

echo.
echo Done! Data converted and updated.
echo [%date% %time%] Autorun complete >> "%LOGFILE%"

REM --- Keep window open if double-clicked ---
if "%1"=="--pause" pause
