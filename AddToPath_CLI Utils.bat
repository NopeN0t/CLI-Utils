@echo off
setlocal EnableDelayedExpansion

REM Get the folder where this script is located
set "CLITOOL_DIR=%~dp0"
REM Remove trailing backslash if exists
if "%CLITOOL_DIR:~-1%"=="\" set "CLITOOL_DIR=%CLITOOL_DIR:~0,-1%"

REM Read current user PATH
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do (
    set "CURPATH=%%b"
)

REM Check if it's already in PATH
echo !CURPATH! | find /i "%CLITOOL_DIR%" >nul
if not errorlevel 1 (
    echo Already in PATH.
    goto end
)

REM Append to PATH
setx PATH "!CURPATH!;%CLITOOL_DIR%"
echo Added "%CLITOOL_DIR%" to user PATH.

:end
pause
