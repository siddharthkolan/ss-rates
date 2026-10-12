@echo off
rem Shree SS Jewellers - Rate Board starter
rem Is file ko usi folder me rakho jahan serve.py aur rate_board.html hain (C:\RateBoard)

cd /d "%~dp0"

rem Python 3.12 pakka kiya hai (computer par 3.12 aur 3.14 dono hone par bhi yehi chalega)
rem truststore ek baar install ho jata hai; dobara chalane par bas check hota hai
py -3.12 -m pip install --quiet truststore >nul 2>&1

rem server minimized window me chalu
start "Rate Board Server" /min py -3.12 serve.py

rem server ko 3 second do, phir board full screen me kholo
timeout /t 3 /nobreak >nul
start "" firefox --kiosk http://localhost:8000

rem Firefox na mile to upar wali line ki jagah ye likho:
rem start "" "C:\Program Files\Mozilla Firefox\firefox.exe" --kiosk http://localhost:8000
rem Firefox pehle se khula ho to nayi window full screen me na khule, tab board par F dabao
rem Full screen se bahar aane ke liye: Alt + F4
