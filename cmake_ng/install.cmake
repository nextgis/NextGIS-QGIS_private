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

if(NOT DEFINED PACKAGE_NAME)
    set(PACKAGE_NAME "NGQ")
endif()
string(REPLACE " " "_" INSTALL_DIR_NAME ${PACKAGE_NAME})

if(NOT DEFINED PACKAGE_VENDOR)
    set(PACKAGE_VENDOR "Nextgis")
endif()

if(NOT DEFINED PACKAGE_INSTALL_DIRECTORY)
    #set(PACKAGE_INSTALL_DIRECTORY ${PACKAGE_VENDOR})
    set(PACKAGE_INSTALL_DIRECTORY "nextgis")
endif()

if(NOT DEFINED PACKAGE_BUGREPORT)
    set(PACKAGE_BUGREPORT info@nextgis.ru)
endif()

if(CUSTOMIZATION_NGQ_PROGNAME)
    string(TOLOWER ${CUSTOMIZATION_NGQ_PROGNAME} QGIS_CONFIG_DIR_NAME)
    string(REPLACE " " "_" QGIS_CONFIG_DIR_NAME ${QGIS_CONFIG_DIR_NAME})
    set(QGIS_CONFIG_DIR_NAME ".${QGIS_CONFIG_DIR_NAME}")
else()
    set (QGIS_CONFIG_DIR_NAME ".ngq2")
endif()

if(CUSTOMIZATION_NGQ_SHORTCUT_NAME)
    set (NGQ_RUN_SHORTCUT_NAME "${CUSTOMIZATION_NGQ_SHORTCUT_NAME}")
else()
    set (NGQ_RUN_SHORTCUT_NAME "NextGIS QGIS")
endif()

set (CPACK_PACKAGE_NAME "${PACKAGE_NAME}")
set (CPACK_PACKAGE_VENDOR "${PACKAGE_VENDOR}")
set (CPACK_PACKAGE_VERSION "${NGQ_VERSION}")
set (CPACK_PACKAGE_VERSION_MAJOR "${NGQ_VERSION_MAJOR}")
set (CPACK_PACKAGE_VERSION_MINOR "${NGQ_VERSION_MINOR}")
if (NGQ_VERSION_PATCH)
    set (CPACK_PACKAGE_VERSION_PATCH "${NGQ_VERSION_PATCH}")
endif()
set (CPACK_PACKAGE_DESCRIPTION_SUMMARY "${PACKAGE_NAME} Installation")
set (CPACK_PACKAGE_DESCRIPTION_FILE "${CMAKE_CURRENT_SOURCE_DIR}/README.md")
set (CPACK_PACKAGE_INSTALL_DIRECTORY "${PACKAGE_INSTALL_DIRECTORY}")
set (CPACK_PACKAGE_INSTALL_REGISTRY_KEY "${PACKAGE_NAME} ${NGQ_VERSION}")
set (CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/doc/LICENSE")
set (CPACK_RESOURCE_FILE_README "${CMAKE_CURRENT_SOURCE_DIR}/NEWS")
set (CPACK_PACKAGE_RELOCATABLE TRUE)
#set (CPACK_PACKAGE_ICON ${CMAKE_SOURCE_DIR}/images/icons\\\\qgis-icon.png) # http://stackoverflow.com/a/28768495
set (CPACK_ARCHIVE_COMPONENT_INSTALL ON)

if (WIN32)
#  set (CPACK_SET_DESTDIR FALSE)
#  set (CPACK_PACKAGING_INSTALL_PREFIX "/opt")
  
#  set(scriptPath ${CMAKE_MODULE_PATH}/EnvVarUpdate.nsh) 
#  file(TO_NATIVE_PATH ${scriptPath} scriptPath )
#  string(REPLACE "\\" "\\\\" scriptPath  ${scriptPath} ) 
#  set (CPACK_NSIS_ADDITIONAL_INCLUDES "!include \\\"${scriptPath}\\\" \\n")

  set (CPACK_GENERATOR "NSIS")
  set (CPACK_MONOLITHIC_INSTALL ON)
  set (CPACK_NSIS_DISPLAY_NAME "${PACKAGE_NAME}")
  set (CPACK_NSIS_COMPONENT_INSTALL ON)
  set (CPACK_NSIS_CONTACT "${PACKAGE_BUGREPORT}")
  set (CPACK_NSIS_MODIFY_PATH OFF)
  set (CPACK_NSIS_PACKAGE_NAME "${CPACK_PACKAGE_NAME} ${NGQ_VERSION}")
  set (CPACK_NSIS_ENABLE_UNINSTALL_BEFORE_INSTALL ON)
  
  set (CPACK_NSIS_MUI_ICON ${CMAKE_SOURCE_DIR}/src/app/qgis.ico)

  # string (REPLACE "/" "\\\\" NSIS_INSTALL_SHARE_DIR "${INSTALL_SHARE_DIR}")
  # string (REPLACE "/" "\\\\" NSIS_INSTALL_LIB_DIR "${INSTALL_LIB_DIR}")
  # string (REPLACE "/" "\\\\" NSIS_INSTALL_BIN_DIR "${INSTALL_BIN_DIR}")
  
  
  # set (CPACK_NSIS_EXTRA_INSTALL_COMMANDS
  #      "  Push 'GDAL_DATA'
  #   Push 'A'
  #   Push 'HKCU'
  #   Push '$INSTDIR\\\\${NSIS_INSTALL_SHARE_DIR}'
  #   Call EnvVarUpdate
  #   Pop  '$0' ")
          
  # set (CPACK_NSIS_EXTRA_UNINSTALL_COMMANDS
  #      "  Push 'GDAL_DATA'
  #   Push 'R'
  #   Push 'HKCU'
  #   Push '$INSTDIR\\\\${NSIS_INSTALL_SHARE_DIR}'
  #   Call un.EnvVarUpdate
  #   Pop  '$0' ")
    
    
  # set (CPACK_NSIS_EXTRA_INSTALL_COMMANDS
  #      "  Push 'PATH'
  #   Push 'A'
  #   Push 'HKCU'
  #   Push '$INSTDIR\\\\${NSIS_INSTALL_BIN_DIR}'
  #   Call EnvVarUpdate
  #   Pop  '$0' ")
          
  # set (CPACK_NSIS_EXTRA_UNINSTALL_COMMANDS
  #      "  Push 'PATH'
  #   Push 'R'
  #   Push 'HKCU'
  #   Push '$INSTDIR\\\\${NSIS_INSTALL_BIN_DIR}'
  #   Call un.EnvVarUpdate
  #   Pop  '$0' ")
  
  
  # # https://docs.python.org/3/install/      
  # find_package(PythonInterp REQUIRED)
  # if(PYTHONINTERP_FOUND)
  #   set (CPACK_NSIS_EXTRA_INSTALL_COMMANDS ${CPACK_NSIS_EXTRA_INSTALL_COMMANDS}
  #        "  Push 'PYTHONPATH'
  #   Push 'A'
  #   Push 'HKCU'
  #   Push '$INSTDIR\\\\${NSIS_INSTALL_LIB_DIR}\\\\Python${PYTHON_VERSION_MAJOR}${PYTHON_VERSION_MINOR}\\\\site-packages'
  #   Call EnvVarUpdate
  #   Pop  '$0' ")    
        
  #   set (CPACK_NSIS_EXTRA_UNINSTALL_COMMANDS ${CPACK_NSIS_EXTRA_UNINSTALL_COMMANDS}     
  #      "  Push 'PYTHONPATH'
  #   Push 'R'
  #   Push 'HKCU'
  #   Push '$INSTDIR\\\\${NSIS_INSTALL_LIB_DIR}\\\\Python${PYTHON_VERSION_MAJOR}${PYTHON_VERSION_MINOR}\\\\site-packages'
  #   Call un.EnvVarUpdate
  #   Pop  '$0' ")
  # endif()   
  # string (REPLACE ";" "\n" CPACK_NSIS_EXTRA_INSTALL_COMMANDS "${CPACK_NSIS_EXTRA_INSTALL_COMMANDS}")
  # string (REPLACE ";" "\n" CPACK_NSIS_EXTRA_UNINSTALL_COMMANDS "${CPACK_NSIS_EXTRA_UNINSTALL_COMMANDS}")

else ()
	#TODO
endif ()

#-----------------------------------------------------------------------------
# INSTALLation of not building components
#-----------------------------------------------------------------------------
include(InstallRequiredSystemLibraries)

include (CPack)

if (WIN32)
  #PYTHON
  get_filename_component(PYTHON_HOME ${PYTHON_EXECUTABLE} DIRECTORY)
  file(GLOB PYTHON_DLLs ${PYTHON_HOME}/python27.dll)
  install(FILES ${PYTHON_DLLs} DESTINATION ${QGIS_BIN_DIR})
  install(DIRECTORY ${PYTHON_HOME}/Lib DESTINATION lib/Python27)
  install(DIRECTORY ${PYTHON_HOME}/DLLs DESTINATION lib/Python27)
  # QT
  get_filename_component(QT_LIBRARIES_DIR ${QT_QTCORE_LIBRARY} DIRECTORY)
  file(GLOB QT_DLLs ${QT_LIBRARIES_DIR}/*.dll)
  install(FILES ${QT_DLLs} DESTINATION ${QGIS_BIN_DIR})
  install(DIRECTORY ${QT_PLUGINS_DIR} DESTINATION ${QGIS_BIN_DIR} FILES_MATCHING PATTERN "*.dll")
  # QWT
  get_filename_component(QWT_LIBRARIES_DIR ${QWT_LIBRARY} DIRECTORY)
  file(GLOB QWT_DLLs ${QWT_LIBRARIES_DIR}/*.dll)
  install(FILES ${QWT_DLLs} DESTINATION ${QGIS_BIN_DIR})
  # QWT Polar
  get_filename_component(QWTPOLAR_LIBRARIES_DIR ${QWTPOLAR_LIBRARY} DIRECTORY)
  file(GLOB QWTPOLAR_DLLs ${QWTPOLAR_LIBRARIES_DIR}/*.dll)
  install(FILES ${QWTPOLAR_DLLs} DESTINATION ${QGIS_BIN_DIR})
  # QCA
  get_filename_component(QCA_LIBRARIES_DIR ${QCA_LIBRARY} DIRECTORY)
  get_filename_component(QCA_INSTALL_DIR ${QCA_LIBRARIES_DIR} DIRECTORY)
  set(QCA_BIN_DIR ${QCA_INSTALL_DIR}/bin)
  file(GLOB QCA_DLLs ${QCA_BIN_DIR}/*.dll)
  install(FILES ${QCA_DLLs} DESTINATION ${QGIS_BIN_DIR})
  # install(DIRECTORY ${QCA_LIBRARIES_DIR}/qca/crypto DESTINATION ${QGIS_BIN_DIR}) # this is in qt plugins

  # OpenSSL need for openssl qca plugin
  find_anyproject(OpenSSL REQUIRED)
  # get_filename_component(OPENSSL_ROOT_DIR ${OPENSSL_INCLUDE_DIR} DIRECTORY)
  # file(GLOB OPENSSL_DLLs ${OPENSSL_ROOT_DIR}/*.dll)
  # install(FILES ${OPENSSL_DLLs} DESTINATION ${QGIS_BIN_DIR})

  #---
  #   win run script
  #---
  CONFIGURE_FILE(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake_templates/ngq.bat.in"
    "${CMAKE_CURRENT_BINARY_DIR}/ngq.bat"
  )
  install(FILES ${CMAKE_CURRENT_BINARY_DIR}/ngq.bat DESTINATION ${QGIS_BIN_DIR})

  #-----------------------------------------------------------------------------
  # Create the desktop link
  #-----------------------------------------------------------------------------
  string(REPLACE "/" "\\\\" QGIS_ICO_DIR_4_NSIS ${QGIS_DATA_DIR})
  LIST(APPEND CPACK_NSIS_EXTRA_INSTALL_COMMANDS "CreateShortCut '$DESKTOP\\\\${NGQ_RUN_SHORTCUT_NAME}.lnk' '$INSTDIR\\\\bin\\\\ngq.bat' '' '$INSTDIR\\\\${QGIS_ICO_DIR_4_NSIS}\\\\qgis.ico''' SW_SHOWNORMAL '' 'Run NextGIS QGIS' ")
  LIST(APPEND CPACK_NSIS_EXTRA_UNINSTALL_COMMANDS "Delete '$DESKTOP\\\\${NGQ_RUN_SHORTCUT_NAME}.lnk'")


  file(WRITE "${CMAKE_BINARY_DIR}/ftp_upload.bat" "curl -u %1 -T ${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}-${CPACK_SYSTEM_NAME}.exe %2")

elseif(UNIX)
  # for adding into debian applications list
  install(FILES ${CMAKE_SOURCE_DIR}/inst/debian/ngqgis.desktop DESTINATION share/applications)

endif()
#-----------------------------------------------------------------------------
# Now list the cpack commands
#-----------------------------------------------------------------------------
cpack_add_component (applications 
    DISPLAY_NAME "${PACKAGE_NAME} utility programs" 
    DEPENDS libraries
    GROUP Applications
)
cpack_add_component (libraries 
    DISPLAY_NAME "${PACKAGE_NAME} libraries"
    GROUP Runtime
)
cpack_add_component (headers 
    DISPLAY_NAME "${PACKAGE_NAME} headers" 
    DEPENDS libraries
    GROUP Development
)
cpack_add_component (documents 
    DISPLAY_NAME "${PACKAGE_NAME} documents"
    GROUP Documents
)
