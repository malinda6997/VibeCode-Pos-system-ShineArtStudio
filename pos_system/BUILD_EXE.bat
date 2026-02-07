@echo off
REM ============================================================
REM Shine Art Studio POS - Standalone EXE Builder
REM Developer: Malinda Prabath
REM ============================================================

echo.
echo ============================================================
echo   SHINE ART STUDIO - POS SYSTEM
echo   Standalone EXE Builder
echo   Developer: Malinda Prabath
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Run the build script
python build_standalone_exe.py

pause
