; define by auto build system ======
; ==================================
!ifndef PROGRAM_NAME
    !define PROGRAM_NAME "NextGIS QGIS"
!endif
!ifndef PROGRAM_VERSION
    !include "nextgis_qgis-verison.nsh"
!endif
!ifdef NGQ_BUILD_NUM
    !define PROGRAM_VERSION_FULL "${PROGRAM_VERSION}.${NGQ_BUILD_NUM}"
    !undef PROGRAM_VERSION
    !define PROGRAM_VERSION ${PROGRAM_VERSION_FULL}
!endif

!define PUBLISHER "NextGIS"
!define WEB_SITE "http://www.nextgis.ru"
!define WIKI_PAGE ""

!ifndef INSTALLER_NAME    
    !define INSTALLER_NAME "nextgis-qgis-setup"
!endif

!define INSTALLER_NAME_WITH_VERS "${INSTALLER_NAME}-${PROGRAM_VERSION}"

!ifdef INSTALLER_OUTPUT_DIR
    !define INSTALLER_NAME_FULL "${INSTALLER_OUTPUT_DIR}\${INSTALLER_NAME_WITH_VERS}"
    !undef INSTALLER_NAME
    !define INSTALLER_NAME ${INSTALLER_NAME_FULL}
!endif
!define OUTPUT_FILE "${INSTALLER_NAME}.exe"

!define DEFAULT_INSTALL_DIR "c:\${PROGRAM_NAME}"

!ifndef SMPROGRAMS_FOLDER_NAME_EN
    !define SMPROGRAMS_FOLDER_NAME_EN "${PROGRAM_NAME}"
!endif

!ifndef NextGIS_QGIS_RUN_LNK_NAME
    !define NextGIS_QGIS_RUN_LNK_NAME "NextGIS QGIS (${PROGRAM_VERSION})"
!endif

!ifndef NextGIS_QGIS_RUN_LNK_ICO_FileName
    !define NextGIS_QGIS_RUN_LNK_ICO_FileName "qgis.ico"
    !define NextGIS_QGIS_RUN_LNK_ICO_Path "..\..\..\src\app\${NextGIS_QGIS_RUN_LNK_ICO_FileName}"
!endif

!ifndef NextGIS_QGIS_UNINSTALLER_FileName
    !define NextGIS_QGIS_UNINSTALLER_FileName "Uninstall-ngq.exe"
!endif
!define NextGIS_QGIS_UNINSTALL_LNK_NAME_SUFFIX "${NextGIS_QGIS_RUN_LNK_NAME}"

; define by auto build system ======
;!define OSGEO4W_SRC_DIR ""
;!define QGIS_SRC_DIR ""
;!define GRASS_SRC_DIR ""
;!define SAGA_SRC_DIR ""
; ==================================

!ifndef QGIS_DEFAULT_OPTIONS_PATH
    !define QGIS_DEFAULT_OPTIONS_PATH "..\ngq_default_options"
!endif

!ifndef QGIS_RUN_SCRIPTS_DIR
    !define QGIS_RUN_SCRIPTS_DIR "..\ngq_run_scripts"
!endif

; define by auto build system ======
;!define PLUGINS "d:\builds\plugins\identifyplus"
;!define QGIS_MANUAL_FILE_NAME_RU "QGIS-2.6-UserGuide-ru.pdf"
;!define QGIS_MANUAL_FILE_NAME_EN "QGIS-2.6-UserGuide-en.pdf"
;!define FONTS_DIR "fonts"
;!define EXAMPLES_DIR "ngq-examples"
;!define NGQ_STYLES_DIR "ngq-symbology-style"
;!define NGQ_PRINT_TEMPLATES_DIR "ngq-print-templates"
; ==================================

!include "nextgis_qgis-base.nsh"