@echo off
setlocal

py -m pip install --upgrade pip
if errorlevel 1 goto :failed

py -m pip install -r requirements-brian.txt
if errorlevel 1 goto :failed

py -m PyInstaller --clean --noconfirm Brian_Rotary_CAM.spec
if errorlevel 1 goto :failed

echo.
echo Build complete: dist\Rotary Axis CAM - 3 Axis\Rotary Axis CAM - 3 Axis.exe
exit /b 0

:failed
echo.
echo Build failed. Review the messages above.
exit /b 1
