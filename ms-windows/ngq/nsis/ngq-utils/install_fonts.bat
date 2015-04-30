@echo off

cd /D %OSGEO4W_ROOT%\ngq-utils

set FONTS_FOLDER=%SYSTEMROOT%\fonts

call "install_font.bat" "OpenGost Type A TT Regular (TrueType)" "OpenGostTypeA-Regular.ttf"
call "install_font.bat" "OpenGost Type B TT Regular (TrueType)" "OpenGostTypeB-Regular.ttf"
call "install_font.bat" "SymbolSigns-Basisset (TrueType)" "symbol-signs.otf"
call "install_font.bat" "WebHostingHub-Glyphs (TrueType)" "webhostinghub-glyphs.ttf"
call "install_font.bat" "Heydings Icons (TrueType)" "heydings_icons.ttf"
