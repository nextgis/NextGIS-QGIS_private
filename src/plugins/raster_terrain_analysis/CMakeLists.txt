########################################################
# Files

SET (RASTER_TERRAIN_SRCS
     qgsrasterterrainanalysisplugin.cpp
     qgsrasterterrainanalysisdialog.cpp
)

SET (RASTER_TERRAIN_UIS
    qgsrasterterrainanalysisdialogbase.ui
    )

SET (RASTER_TERRAIN_MOC_HDRS
qgsrasterterrainanalysisdialog.h
qgsrasterterrainanalysisplugin.h
)

SET (RASTER_TERRAIN_RCCS  resources.qrc)
########################################################
# Build

QT4_WRAP_UI (RASTER_TERRAIN_UIS_H  ${RASTER_TERRAIN_UIS})

QT4_WRAP_CPP (RASTER_TERRAIN_MOC_SRCS  ${RASTER_TERRAIN_MOC_HDRS})

QT4_ADD_RESOURCES(RASTER_TERRAIN_RCC_SRCS ${RASTER_TERRAIN_RCCS})

ADD_LIBRARY (rasterterrainplugin MODULE
  ${RASTER_TERRAIN_SRCS}
  ${RASTER_TERRAIN_MOC_SRCS}
  ${RASTER_TERRAIN_RCC_SRCS}
  ${RASTER_TERRAIN_UIS_H})

INCLUDE_DIRECTORIES(
     ${CMAKE_CURRENT_BINARY_DIR}
     ../../core
     ../../core/geometry
     ../../core/raster
     ../../gui
     ../../analysis/raster
     ..
     .
)

INCLUDE_DIRECTORIES(SYSTEM
     ${GDAL_INCLUDE_DIR}
)

TARGET_LINK_LIBRARIES(rasterterrainplugin
  ${QGIS_ANALYSIS_TARGET_NAME}
  ${QGIS_CORE_TARGET_NAME}
  ${QGIS_GUI_TARGET_NAME}
)


########################################################
# Install

INSTALL(TARGETS rasterterrainplugin
  RUNTIME DESTINATION ${QGIS_PLUGIN_DIR}
  LIBRARY DESTINATION ${QGIS_PLUGIN_DIR}
  )
