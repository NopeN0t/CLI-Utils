@echo off
setlocal enabledelayedexpansion

for %%F in (*.*) do (
    echo Converting: %%F
    ffmpeg -y -i "%%F" -c copy "%%~nF.mp4"
    if exist "%%~nF.mp4" (
        echo Conversion successful, deleting original: %%F
        del "%%F"
    ) else (
        echo Conversion failed: %%F
    )
)

echo.
echo All tasks completed!
echo.

REM ---- Sound alert ----
powershell -c "(New-Object Media.SoundPlayer 'C:\Windows\Media\Windows Notify System Generic.wav').PlaySync()"
pause
