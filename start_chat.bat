@echo off
echo === Chat Application Quick Start ===
echo.
echo This script will help you start the chat application quickly.
echo.
echo Options:
echo 1. Start Server Only
echo 2. Start Client Only  
echo 3. Start Demo (Server + Instructions)
echo 4. Exit
echo.

:menu
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto start_server
if "%choice%"=="2" goto start_client
if "%choice%"=="3" goto start_demo
if "%choice%"=="4" goto exit
echo Invalid choice. Please enter 1-4.
goto menu

:start_server
echo Starting chat server...
python server.py
pause
goto menu

:start_client
echo Starting chat client...
python client.py
pause
goto menu

:start_demo
echo Starting demo...
python demo.py
pause
goto menu

:exit
echo Goodbye!
pause
exit
