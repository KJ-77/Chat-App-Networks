@echo off
echo === Chat Application Quick Start ===
echo.
echo This script will help you start the chat application quickly.
echo.
echo Options:
echo 1. Start Console Server
echo 2. Start Server Admin GUI
echo 3. Start Console Client
echo 4. Start GUI Client
echo 5. Start Demo (Server + Instructions)
echo 6. Exit
echo.

:menu
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto start_console_server
if "%choice%"=="2" goto start_server_gui
if "%choice%"=="3" goto start_console_client
if "%choice%"=="4" goto start_gui_client
if "%choice%"=="5" goto start_demo
if "%choice%"=="6" goto exit
echo Invalid choice. Please enter 1-6.
goto menu

:start_console_server
echo Starting console chat server...
python server.py
pause
goto menu

:start_server_gui
echo Starting server admin GUI...
python server_gui.py
pause
goto menu

:start_console_client
echo Starting console chat client...
python client.py
pause
goto menu

:start_gui_client
echo Starting GUI chat client...
python gui_client.py
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
