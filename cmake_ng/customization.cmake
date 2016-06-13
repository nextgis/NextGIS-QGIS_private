################################################################################
# Project:  CMake4GDAL
# Purpose:  CMake build scripts
# Author:   Alexander Lisovenko, alexander.lisovenko@gmail.ru
################################################################################
# Copyright (C) 2015-2016, NextGIS <info@nextgis.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
################################################################################

message(STATUS "Customization: START!")

SET (CUSTOMIZATION_DIR "" CACHE PATH "The directory containing the customization files")

if(EXISTS "${CUSTOMIZATION_DIR}")
    message(STATUS "Use customization dir: ${CUSTOMIZATION_DIR}")
else()
    message(FATAL_ERROR "Customization dir not found. Set correct value for CUSTOMIZATION_DIR value")
endif()

set(CUSTOMIZATION_CONFIG "${CUSTOMIZATION_DIR}/ngw_customization_ini.cmake")
include(${CUSTOMIZATION_CONFIG})

#-----------------
# Castomize program name
#-----------------
message(STATUS "Customization: Castomize program name...")
if(CUSTOMIZATION_NGQ_PROGNAME)
    set(PACKAGE_NAME ${CUSTOMIZATION_NGQ_PROGNAME})
else()
    set(PACKAGE_NAME "NextGIS QGIS")
endif()

#-----------------
# Castomize title
#-----------------
message(STATUS "Customization: Castomize title...")
if(NOT CUSTOMIZATION_NGQ_TITLE_EN)
    SET (CUSTOMIZATION_NGQ_TITLE_EN "NextGIS QGIS")
endif()
if(NOT CUSTOMIZATION_NGQ_TITLE_RU)
    SET (CUSTOMIZATION_NGQ_TITLE_RU "NextGIS QGIS")
endif()

CONFIGURE_FILE(
  "${CMAKE_CURRENT_SOURCE_DIR}/cmake_templates/customization/src/app/qgisapp.cpp.in"
  "${CMAKE_CURRENT_SOURCE_DIR}/src/app/qgisapp.cpp"
)
CONFIGURE_FILE(
  "${CMAKE_CURRENT_SOURCE_DIR}/cmake_templates/customization/i18n/qgis_ru.ts.in"
  "${CMAKE_CURRENT_SOURCE_DIR}/i18n/qgis_ru.ts"
)

#-----------------
# Castomize icons
#-----------------
function(customize_icon cmake_define_name customized_icon)
    if(${cmake_define_name})
        set(cmake_define ${${cmake_define_name}})
        set(CUSTOMIZE_FILE "${CUSTOMIZATION_DIR}/${cmake_define}")
        IF (EXISTS "${CUSTOMIZE_FILE}")
            file (COPY "${CUSTOMIZE_FILE}" DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/src/app")
            get_filename_component(CUSTOMIZATION_NGQ_ICON_NAME "${CUSTOMIZE_FILE}" NAME)
            file (RENAME "${CMAKE_CURRENT_SOURCE_DIR}/src/app/${CUSTOMIZATION_NGQ_ICON_NAME}" "${CMAKE_CURRENT_SOURCE_DIR}/${customized_icon}")
            message(STATUS "Customization: Castomize icon ${customized_icon} with ${CUSTOMIZE_FILE} done!")
        ELSE()
            message(WARNING "Customization: Castomize icon ${CUSTOMIZE_FILE} not found...")
        ENDIF()
    else()
        message(WARNING "Customization: Castomize icon not set ${cmake_define_name}...")
    endif()
endfunction(customize_icon)

message(STATUS "Customization: Castomize icons...")
customize_icon("CUSTOMIZATION_NGQ_ICON_ICO" "src/app/qgis.ico")
customize_icon("CUSTOMIZATION_NGQ_ICON_PNG_16" "images/icons/qgis-icon-16x16.png")
customize_icon("CUSTOMIZATION_NGQ_ICON_PNG_16" "images/icons/qgis-icon-16x16_xmas.png")
customize_icon("CUSTOMIZATION_NGQ_ICON_PNG_60" "images/icons/qgis-icon-60x60.png")
customize_icon("CUSTOMIZATION_NGQ_ICON_PNG_60" "images/icons/qgis-icon-60x60_xmas.png")
customize_icon("CUSTOMIZATION_NGQ_ICON_SVG" "images/icons/qgis_icon.svg")
customize_icon("CUSTOMIZATION_NGQ_ICON_SVG" "images/icons/qgis_icon_xmas.svg")
customize_icon("CUSTOMIZATION_NGQ_ICON_SVG" "images/themes/default/mActionHelpAbout.svg")
customize_icon("CUSTOMIZATION_NGQ_SPLASH" "images/splash/splash.png")

#---------------
# Shortcut name
#---------------
if(NOT CUSTOMIZATION_NGQ_SHORTCUT_NAME)
    SET (CUSTOMIZATION_NGQ_SHORTCUT_NAME "${CUSTOMIZATION_NGQ_TITLE_EN}")
endif()
message(STATUS "Customization: Shortcut name is ${CUSTOMIZATION_NGQ_SHORTCUT_NAME}")