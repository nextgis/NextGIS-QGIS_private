@echo off
rem %1 - font name; %2 - font filename
set FONTS_FOLDER=%SYSTEMROOT%\fonts
echo "Try set %2 (%1)"
if NOT EXIST %FONTS_FOLDER%\%2 (COPY /Y %OSGEO4W_ROOT%\fonts\%2 %FONTS_FOLDER%)
REG QUERY "HKLM\Software\Microsoft\Windows NT\CurrentVersion\Fonts" /v %1
if errorlevel 1 (
     REG ADD "HKLM\Software\Microsoft\Windows NT\CurrentVersion\Fonts" /v %1 /t REG_SZ /d %2
)