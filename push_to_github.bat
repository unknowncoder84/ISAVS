@echo off
echo ========================================
echo ISAVS 2026 - Push to GitHub
echo ========================================
echo.
echo Repository: https://github.com/unknowncoder84/ISAVS
echo Branch: main
echo Commits ready: 13
echo.
echo ========================================
echo Step 1: Clearing Git Credentials
echo ========================================
git credential-manager delete https://github.com
echo.
echo ========================================
echo Step 2: Pushing to GitHub
echo ========================================
echo You will be prompted to login as unknowncoder84
echo.
git push -u origin main
echo.
echo ========================================
echo Push Complete!
echo ========================================
echo.
echo Verify at: https://github.com/unknowncoder84/ISAVS
echo.
pause
