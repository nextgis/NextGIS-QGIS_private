@echo off
rem %1 build directory
rem %2 project file

cd /d %1

msbuild /p:Configuration=Release %2
msbuild /p:Configuration=Release INSTALL.vcproj