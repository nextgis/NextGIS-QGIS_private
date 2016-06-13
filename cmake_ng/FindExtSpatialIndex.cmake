################################################################################
# Project:  external projects
# Purpose:  CMake build scripts
# Author:   Lisovenko Alexnader, alexander.lisovenko@gmail.com
################################################################################
# Copyright (C) 2016, NextGIS <info@nextgis.com>
# Copyright (C) 2016 Lisovenko Alexnader
#
# This script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this script.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

set(repo_name lib_spatialindex)

if(BUILD_SHARED_LIBS)    
    set(repo_project spatialindex)
else()
    set(repo_project spatialindexstatic)
endif()

set(repo_include spatialindex)
