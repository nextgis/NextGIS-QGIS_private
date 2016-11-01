################################################################################
# Project:  CMake4GDAL
# Purpose:  CMake build scripts
# Author:   Dmitry Baryshnikov, polimax@mail.ru
################################################################################
# Copyright (C) 2015, NextGIS <info@nextgis.com>
# Copyright (C) 2012,2013,2014 Dmitry Baryshnikov
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


function(check_version major minor rev)

    # parse the version number from gdal_version.h and include in
    # major, minor and rev parameters

    file(READ ${CMAKE_CURRENT_SOURCE_DIR}/core/gcore/gdal_version.h GDAL_VERSION_H_CONTENTS)

    string(REGEX MATCH "GDAL_VERSION_MAJOR[ \t]+([0-9]+)"
      GDAL_MAJOR_VERSION ${GDAL_VERSION_H_CONTENTS})
    string (REGEX MATCH "([0-9]+)"
      GDAL_MAJOR_VERSION ${GDAL_MAJOR_VERSION})
    string(REGEX MATCH "GDAL_VERSION_MINOR[ \t]+([0-9]+)"
      GDAL_MINOR_VERSION ${GDAL_VERSION_H_CONTENTS})
    string (REGEX MATCH "([0-9]+)"
      GDAL_MINOR_VERSION ${GDAL_MINOR_VERSION})
    string(REGEX MATCH "GDAL_VERSION_REV[ \t]+([0-9]+)"
      GDAL_REV_VERSION ${GDAL_VERSION_H_CONTENTS})
    string (REGEX MATCH "([0-9]+)"
      GDAL_REV_VERSION ${GDAL_REV_VERSION})

    set(${major} ${GDAL_MAJOR_VERSION} PARENT_SCOPE)
    set(${minor} ${GDAL_MINOR_VERSION} PARENT_SCOPE)
    set(${rev} ${GDAL_REV_VERSION} PARENT_SCOPE)

endfunction(check_version)

# search python module
function(find_python_module module)
    string(TOUPPER ${module} module_upper)
    if(ARGC GREATER 1 AND ARGV1 STREQUAL "REQUIRED")
        set(${module}_FIND_REQUIRED TRUE)
    else()
        if (ARGV1 STREQUAL "QUIET")
            set(PY_${module}_FIND_QUIETLY TRUE)
        endif()
    endif()

    if(NOT PY_${module_upper})
        # A module's location is usually a directory, but for binary modules
        # it's a .so file.
        execute_process(COMMAND "${PYTHON_EXECUTABLE}" "-c"
            "import re, ${module}; print(re.compile('/__init__.py.*').sub('',${module}.__file__))"
            RESULT_VARIABLE _${module}_status
            OUTPUT_VARIABLE _${module}_location
            ERROR_QUIET
            OUTPUT_STRIP_TRAILING_WHITESPACE)
        if(NOT _${module}_status)
            set(PY_${module_upper} ${_${module}_location} CACHE STRING
                "Location of Python module ${module}")
        endif(NOT _${module}_status)
    endif(NOT PY_${module_upper})
    find_package_handle_standard_args(PY_${module} DEFAULT_MSG PY_${module_upper})
endfunction(find_python_module)

function(set_libraries libs is_shared bld_dir release_name debug_name)
    if (MSVC)
        if(is_shared)
            set(${libs}
                    debug "${bld_dir}/Debug/${CMAKE_SHARED_LIBRARY_PREFIX}${debug_name}${CMAKE_STATIC_LIBRARY_SUFFIX}"
                    optimized "${bld_dir}/Release/${CMAKE_SHARED_LIBRARY_PREFIX}${release_name}${CMAKE_STATIC_LIBRARY_SUFFIX}"
                PARENT_SCOPE)
        else()
            set(${libs}
                    debug"${bld_dir}/Debug/${CMAKE_STATIC_LIBRARY_PREFIX}${debug_name}${CMAKE_STATIC_LIBRARY_SUFFIX}"
                    optimized "${bld_dir}/Release/${CMAKE_STATIC_LIBRARY_PREFIX}${release_name}${CMAKE_STATIC_LIBRARY_SUFFIX}"
                PARENT_SCOPE)
        endif()
    else()
        if(is_shared)
            set(${libs}
                "${bld_dir}/${CMAKE_SHARED_LIBRARY_PREFIX}${debug_name}${CMAKE_SHARED_LIBRARY_SUFFIX}"
            PARENT_SCOPE)
        else()
            set(${libs}
                "${bld_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}${release_name}${CMAKE_STATIC_LIBRARY_SUFFIX}"
            PARENT_SCOPE)
        endif()            
    endif()    
endfunction(set_libraries)

function(report_version name ver)

    string(ASCII 27 Esc)
    set(BoldYellow  "${Esc}[1;33m")
    set(ColourReset "${Esc}[m")
        
    message(STATUS "${BoldYellow}${name} version ${ver}${ColourReset}")
    
endfunction() 

function(warning_msg text)
    if(NOT SUPPRESS_VERBOSE_OUTPUT)
    string(ASCII 27 Esc)
    set(Red         "${Esc}[31m")
    set(ColourReset "${Esc}[m")
        
    message(STATUS "${Red}${text}${ColourReset}")
    endif()
endfunction()    


# macro to find packages on the host OS
macro( find_exthost_package )
    if(CMAKE_CROSSCOMPILING)
        set( CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER )
        set( CMAKE_FIND_ROOT_PATH_MODE_LIBRARY NEVER )
        set( CMAKE_FIND_ROOT_PATH_MODE_INCLUDE NEVER )
        if( CMAKE_HOST_WIN32 )
            SET( WIN32 1 )
            SET( UNIX )
        elseif( CMAKE_HOST_APPLE )
            SET( APPLE 1 )
            SET( UNIX )
        endif()
        find_package( ${ARGN} )
        SET( WIN32 )
        SET( APPLE )
        SET( UNIX 1 )
        set( CMAKE_FIND_ROOT_PATH_MODE_PROGRAM ONLY )
        set( CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY )
        set( CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY )
    else()
        find_package( ${ARGN} )
    endif()
endmacro()


# macro to find programs on the host OS
macro( find_exthost_program )
    if(CMAKE_CROSSCOMPILING)
        set( CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER )
        set( CMAKE_FIND_ROOT_PATH_MODE_LIBRARY NEVER )
        set( CMAKE_FIND_ROOT_PATH_MODE_INCLUDE NEVER )
        if( CMAKE_HOST_WIN32 )
            SET( WIN32 1 )
            SET( UNIX )
        elseif( CMAKE_HOST_APPLE )
            SET( APPLE 1 )
            SET( UNIX )
        endif()
        find_program( ${ARGN} )
        SET( WIN32 )
        SET( APPLE )
        SET( UNIX 1 )
        set( CMAKE_FIND_ROOT_PATH_MODE_PROGRAM ONLY )
        set( CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY )
        set( CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY )
    else()
        find_program( ${ARGN} )
    endif()
endmacro()
