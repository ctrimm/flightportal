@echo off
REM Flight Portal Hostname Setup Script (Windows)
REM Adds 'flightportal' to hosts file for easy access
REM Must be run as Administrator

set HOSTNAME=flightportal
set IP=127.0.0.1
set HOSTS_FILE=%SystemRoot%\System32\drivers\etc\hosts
set ENTRY=%IP%    %HOSTNAME%

echo ======================================
echo Flight Portal Hostname Setup
echo ======================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script requires Administrator privileges.
    echo Please right-click and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

REM Check if entry already exists
findstr /C:"%HOSTNAME%" "%HOSTS_FILE%" >nul 2>&1
if %errorLevel% equ 0 (
    echo Entry for '%HOSTNAME%' already exists in hosts file
    echo Current entry:
    findstr /C:"%HOSTNAME%" "%HOSTS_FILE%"
    echo.
    set /p UPDATE="Do you want to update it? (Y/N): "
    if /i "%UPDATE%"=="Y" (
        REM Remove old entry and add new one
        findstr /V /C:"%HOSTNAME%" "%HOSTS_FILE%" > "%HOSTS_FILE%.tmp"
        move /Y "%HOSTS_FILE%.tmp" "%HOSTS_FILE%" >nul
        echo. >> "%HOSTS_FILE%"
        echo # Flight Portal Web Interface >> "%HOSTS_FILE%"
        echo %ENTRY% >> "%HOSTS_FILE%"
        echo Updated entry in hosts file
    ) else (
        echo No changes made.
        exit /b 0
    )
) else (
    REM Add new entry
    echo. >> "%HOSTS_FILE%"
    echo # Flight Portal Web Interface >> "%HOSTS_FILE%"
    echo %ENTRY% >> "%HOSTS_FILE%"
    echo Added entry to hosts file
)

echo.
echo ======================================
echo Setup Complete!
echo ======================================
echo.
echo You can now access the web interface at:
echo   http://flightportal:3100
echo.
echo Or use the direct URL:
echo   http://localhost:3100
echo.

REM Flush DNS cache
ipconfig /flushdns >nul 2>&1

pause
