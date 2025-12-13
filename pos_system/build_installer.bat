@echo off
title Building Installer for Shine Art Studio POS
color 0A

echo ================================================================
echo    Shine Art Studio POS - Installer Builder
echo ================================================================
echo.

REM Check if Inno Setup is installed
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if not exist "%INNO_PATH%" (
    echo ERROR: Inno Setup is not installed!
    echo.
    echo Please install Inno Setup first:
    echo 1. Download from: https://jrsoftware.org/isdl.php
    echo 2. Install Inno Setup 6
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

echo [1/2] Found Inno Setup installation...
echo [2/2] Building installer...
echo.

REM Build the installer
"%INNO_PATH%" "installer_script.iss"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================
    echo    BUILD SUCCESSFUL!
    echo ================================================================
    echo.
    echo Installer created at:
    echo %~dp0installer_output\ShineArtStudio_POS_Setup.exe
    echo.
    echo You can now give this installer to your client!
    echo.
    echo When they double-click it, they will get a professional
    echo Windows installation wizard.
    echo ================================================================
    echo.
) else (
    echo.
    echo ERROR: Build failed!
    echo Please check the error messages above.
    echo.
)

pause
