@echo off 
call "%~dp0venv\Scripts\activate.bat" 
python -B "%~dp0VTranslator\main.py" 
pause