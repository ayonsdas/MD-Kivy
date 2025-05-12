@echo off
REM Navigate to the project directory
cd /d "C:\Users\visloc\molecular-dynamics-kivy"

REM Activate the virtual environment
call kivyenv\Scripts\activate

REM Run the application
python main.py

REM Optional: Keep the command prompt open after running
pause
