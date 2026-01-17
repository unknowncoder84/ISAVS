@echo off
echo ========================================
echo ISAVS - Opening Fresh Instance
echo ========================================
echo.
echo Clearing browser data and opening app...
echo.

REM Open in Microsoft Edge (InPrivate mode - no cache)
start msedge.exe -inprivate "http://localhost:6002"

echo.
echo ========================================
echo Opened in Edge InPrivate Mode
echo This bypasses all cache issues!
echo ========================================
echo.
echo If Edge doesn't open, try Chrome:
echo Press any key to open in Chrome Incognito...
pause >nul

REM Open in Chrome (Incognito mode - no cache)
start chrome.exe --incognito "http://localhost:6002"

echo.
echo Done! Check your browser.
echo.
pause
