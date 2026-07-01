@echo off
cd /d D:\Traccia\tools

echo [%date% %time%] Blackbox auto conversion start

copy "D:\Android Agent Blackbox\events_fixed.jsonl" events_fixed.jsonl /Y
copy "D:\Android Agent Blackbox\evidence.zip" evidence.zip /Y

python blackbox_to_traccia.py events_fixed.jsonl evidence.zip -o D:\Traccia\evidence\blackbox-%date:~0,4%%date:~5,2%%date:~8,2%-%time:~0,2%%time:~3,2%.evidence

if %errorlevel% equ 0 (
    echo [%date% %time%] Conversion successful
) else (
    echo [%date% %time%] Conversion FAILED
)