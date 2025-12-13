@echo off
echo ========================================
echo Shine Art Studio POS - Desktop Shortcut
echo ========================================
echo.

set "EXE_PATH=%~dp0ShineArtStudio_POS.exe"
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\Shine Art Studio POS.lnk"

echo Creating desktop shortcut...

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%EXE_PATH%'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Shine Art Studio POS System'; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo.
    echo SUCCESS! Desktop shortcut created successfully!
    echo Location: %SHORTCUT%
    echo.
    echo You can now run the POS system from your desktop!
) else (
    echo.
    echo ERROR! Failed to create desktop shortcut.
    echo Please run this file as Administrator.
)

echo.
pause
