# -*- coding: utf-8 -*-
import os
import sys
import argparse

import tempfile
import subprocess
import shutil
import zipfile
import json
import re

from patching_qgis_src import patchQGISsrc
from ngq_customization import prepareQGISSettings, prepareRunScripts

currnet_dir = os.path.dirname( os.path.abspath(__file__) )
currnet_working_dir = os.getcwd()

nsis_script_dir = os.path.join(currnet_dir, "..", "nsis")
nsis_script_name = "nextgis_qgis.nsi"

ngq_install_utils_dir = os.path.join(nsis_script_dir, "ngq-utils")
ngq_install_fonts_bat_template = os.path.join(ngq_install_utils_dir, "install_fonts.bat.in")
ngq_install_fonts_bat = os.path.join(ngq_install_utils_dir, "install_fonts.bat")

default_qgis_options_dir = os.path.join(currnet_dir, "..", "ngq_default_options")

default_scripts_dir = os.path.join(currnet_dir, "..", "ngq_run_scripts")

def Configurating(qgis_src_dir, install_dirname):
    conf_qgis_script_filename =  os.path.join(currnet_dir, "configurate.bat")
    qgis_build_dir = tempfile.mkdtemp('','qgis_build_')
    
    try:
        print "conf_qgis_script_filename: ", conf_qgis_script_filename
        print "qgis_build_dir: ", qgis_build_dir
        print "qgis_src_dir: ", qgis_src_dir
        print "install_dirname: ", install_dirname
        res = subprocess.check_call([conf_qgis_script_filename, qgis_build_dir, qgis_src_dir, install_dirname], stdout=sys.stdout)
    except subprocess.CalledProcessError as ex:
        sys.exit("ERROR! Configuration qgis faild: %s\n"%str(ex))
    except:
        sys.exit("ERROR! Configuration qgis faild: Unexpected error: %s\n"%sys.exc_info()[0])
    
    return qgis_build_dir

def Building(qgis_build_dir, project_file):
    print "project_file: ", project_file
    builder_bat = os.path.join(currnet_dir, "ngq-build.bat")
    
    try:
        res = subprocess.check_call([builder_bat, qgis_build_dir, project_file], stdout=sys.stdout)
    except:
        print "ERROR: Building QGIS faild (%s). cmd:\n"%qgis_build_dir, [builder_bat, qgis_build_dir, project_file]
        return False
    
    if res == 0:
        return True
    else:
        return False

def GetVersion(qgis_config_filename):
    import re

    f = open( qgis_config_filename, 'r+')
    lines = f.readlines()
    f.close()

    ngq_version = 0
    for line in lines:
        m = re.search('^#define NGQ_VERSION "[\d,\.]+"', line)
        if m is not None:
            m = re.search('[\d,\.]+',m.group(0))
            if m is not None:
                ngq_version = m.group(0)

    return ngq_version
    
def MakeInstaller(ngq_build_output_dir, ngq_build_num, ngq_installer_dst_dir, ngq_customization_dir, ngq_customization_conf):
    cwd = os.getcwd()
    os.chdir(nsis_script_dir)
    #make_installer_bat = os.path.join(currnet_dir, "make_installer.bat")
    make_installer_command = ["makensis.exe"]
    
    run_scripts_dir = None
    
    if ngq_customization_conf.has_key(u'prog_name'):
        
        make_installer_command.append( "/DPROGRAM_NAME=%s"%ngq_customization_conf[u'prog_name'].encode("cp1251") )
        
        '''QGIS_RUN_SCRIPTS_DIR'''
        run_scripts_dir = prepareRunScripts(default_scripts_dir, ngq_customization_conf[u'prog_name'])
        make_installer_command.append( "/DQGIS_RUN_SCRIPTS_DIR=%s"%run_scripts_dir )
        
        '''NextGIS_QGIS_RUN_LNK_NAME'''
        if ngq_customization_conf.has_key(u'ngq_shortcut_name'):
            make_installer_command.append( "/DNextGIS_QGIS_RUN_LNK_NAME=%s"%ngq_customization_conf[u'ngq_shortcut_name'].encode("cp1251") )
        else:
            make_installer_command.append( "/DNextGIS_QGIS_RUN_LNK_NAME=%s"%ngq_customization_conf[u'prog_name'].encode("cp1251") )
            
    if ngq_customization_conf.has_key(u'installer_name'):
        make_installer_command.append( "/DINSTALLER_NAME=%s"%ngq_customization_conf[u'installer_name'].encode("cp1251") )
    
    '''NextGIS_QGIS_RUN_LNK_ICO_FileName'''
    if ngq_customization_conf.has_key(u'ngq_icon'):
        make_installer_command.append( "/DNextGIS_QGIS_RUN_LNK_ICO_FileName=%s"%ngq_customization_conf[u'ngq_icon'].encode("cp1251") )
        make_installer_command.append( "/DNextGIS_QGIS_RUN_LNK_ICO_Path=%s"%os.path.join(ngq_customization_dir,ngq_customization_conf[u'ngq_icon'].encode("cp1251")) )
        
    '''/DOSGEO4W_SRC_DIR=%OSGEO_ENV_FOR_INSTALLER%'''
    make_installer_command.append( "/DOSGEO4W_SRC_DIR=%s"%os.getenv("OSGEO_ENV_FOR_INSTALLER", "").strip('"') )
    '''/DQGIS_SRC_DIR=%2 ^'''
    make_installer_command.append( "/DQGIS_SRC_DIR=%s"%ngq_build_output_dir )
    '''/DGRASS_SRC_DIR=%GRASS_SRC_DIR% ^'''
    make_installer_command.append( "/DGRASS_SRC_DIR=%s"%os.getenv("GRASS_SRC_DIR", "").strip('"') )
    '''/DSAGA_SRC_DIR=%SAGA_SRC_DIR% ^'''
    make_installer_command.append( "/DSAGA_SRC_DIR=%s"%os.getenv("SAGA_SRC_DIR", "").strip('"') )
    '''/DQGIS_MANUAL_FILE_NAME_RU="QGIS-2.6-UserGuide-ru.pdf" ^'''
    make_installer_command.append( "/DQGIS_MANUAL_FILE_NAME_RU=QGIS-2.6-UserGuide-ru.pdf" )
    '''/DQGIS_MANUAL_FILE_NAME_EN="QGIS-2.6-UserGuide-en.pdf" ^'''
    make_installer_command.append( "/DQGIS_MANUAL_FILE_NAME_EN=QGIS-2.6-UserGuide-en.pdf" )
    '''/DPLUGINS="%PLUGINS_DIR%\publish2ngw %PLUGINS_DIR%\ngw_connect %PLUGINS_DIR%\quick_map_services %PLUGINS_DIR%\identifyplus %PLUGINS_DIR%\qtiles %PLUGINS_DIR%\ru_geocoder %PLUGINS_DIR%\qgis2mobile %~5" ^'''
    plugins = []
    if ngq_customization_conf.has_key(u'ngq_plugins'):
        for pl in ngq_customization_conf[u'ngq_plugins']:
            plugins.append( os.path.join(ngq_customization_dir, "plugins", pl[u'name']) )
    
        plugins_str = " ".join(plugins)
        if len(plugins) > 0:
            make_installer_command.append( "/DPLUGINS=%s"%plugins_str )
    '''/DNGQ_BUILD_NUM=%3 ^'''
    if ngq_build_num is not None:
        make_installer_command.append( "/DNGQ_BUILD_NUM=%s"%str(ngq_build_num) )
    '''/DINSTALLER_OUTPUT_DIR=%4 ^'''
    make_installer_command.append( "/DINSTALLER_OUTPUT_DIR=%s"%ngq_installer_dst_dir )
    '''/DDEFAULT_PROJECT=%9 ^'''
    if ngq_customization_conf.has_key(u'def_project'):
        make_installer_command.append( "/DDEFAULT_PROJECT=%s"%ngq_customization_conf[u'def_project'].encode("cp1251") )
    '''/DQGIS_DEFAULT_OPTIONS_PATH=%8 ^'''
    qgis_options_dir = default_qgis_options_dir
    if ngq_customization_conf.has_key(u'default_qgis_options_dir'):
        qgis_options_dir = os.path.join(ngq_customization_dir, ngq_customization_conf[u'default_qgis_options_dir'].encode("cp1251"))
    qgis_options_dir = prepareQGISSettings(qgis_options_dir, plugins)
    make_installer_command.append( "/DQGIS_DEFAULT_OPTIONS_PATH=%s"%qgis_options_dir )
    
    '''FONTS_DIR'''
    if os.path.exists(ngq_install_fonts_bat):
        os.remove(ngq_install_fonts_bat)
    if ngq_customization_conf.has_key(u'fonts'):
        make_installer_command.append( "/DFONTS_DIR=%s"%os.path.join(ngq_customization_dir, "fonts") )
        f = open(ngq_install_fonts_bat_template, "r")
        content = f.readlines()
        f.close()
        for font in ngq_customization_conf[u'fonts']:
            content.append('call "install_font.bat" "%s" "%s"\n'%(font[u'name'], font[u'file']))
        f = open(ngq_install_fonts_bat, "w")
        f.writelines(content)
        f.close()
    
    '''EXAMPLES_DIR'''
    if ngq_customization_conf.has_key(u'examples'):
        make_installer_command.append( "/DEXAMPLES_DIR=%s"%os.path.join(ngq_customization_dir, ngq_customization_conf[u'examples']) )
    
    '''NGQ_STYLES_DIR'''
    if ngq_customization_conf.has_key(u'symbology_styles'):
        make_installer_command.append( "/DNGQ_STYLES_DIR=%s"%os.path.join(ngq_customization_dir, ngq_customization_conf[u'symbology_styles']) )
        
    '''NGQ_PRINT_TEMPLATES_DIR'''
    if ngq_customization_conf.has_key(u'print_templates'):
        make_installer_command.append( "/DNGQ_PRINT_TEMPLATES_DIR=%s"%os.path.join(ngq_customization_dir, ngq_customization_conf[u'print_templates']) )
        
    make_installer_command.append(nsis_script_name)
    try:
        print "make_installer_command: ", make_installer_command
        res = subprocess.check_output(make_installer_command)
        print res
        
        output_desc_line = re.search('Output: ".+"', res).group()
        print " output_desc_line: ",output_desc_line
        installer_name = re.search('".+"', output_desc_line).group()
        installer_name = installer_name.strip('"')
        print " output_desc_line: ",installer_name
        
        with open(os.path.join(ngq_installer_dst_dir, ".meta-ngq"), 'w') as f:
            f.write(os.path.basename(installer_name))
        
    except subprocess.CalledProcessError as ex:
        sys.exit("ERROR! Make installer error: %s\n"%str(ex))
    except:
        sys.exit("ERROR! Make installer error: Unexpected error: %s\n"%sys.exc_info()[0])
    
    shutil.rmtree(qgis_options_dir)
    if run_scripts_dir is not None:
        shutil.rmtree(run_scripts_dir)
    
    os.chdir(cwd)

parser = argparse.ArgumentParser(description='Script for build NextGIS QGIS')

parser.add_argument('--customization_zip', dest='configuration_zip', help='customization settings as zip archive')
parser.add_argument('--customization_dir', dest='configuration_dir', help='customization settings as directory')
parser.add_argument('-b', '--build', action='store_true', dest='build', help='project name for build')
parser.add_argument('--build_num', dest='build_num', help='build number ')
parser.add_argument('-i', '--make_installer', action='store_true', dest='installer', help='project name for make_installer')
args = parser.parse_args()

#if args.build_num is None:
#    sys.exit("key --build_num must be set")

ngq_customization_dir = None
if args.configuration_zip is not None:
    setting_zip = args.configuration_zip

    if not os.path.exists(setting_zip):
        sys.exit("Configuration zip file not found")

    ngq_customization_dir = tempfile.mkdtemp('','ngq_configuration_')

    zipf = zipfile.ZipFile(setting_zip, 'r')
    zipf.extractall(ngq_customization_dir)

if args.configuration_dir is not None:
    ngq_customization_dir = args.configuration_dir

ngq_customization_conf = {}
if ngq_customization_dir is None or not os.path.exists(ngq_customization_dir):
    #sys.exit("Configuration not found. Use --customization_zip or --customization_dir")
    print "Configuration not found. NGQ will build with default option!\nFor set configuration use --customization_zip or --customization_dir"
else:
    config_file= os.path.join(ngq_customization_dir, "settings.txt")
    if not os.path.exists(config_file):
        sys.exit("Not found settings.txt in configuration")
    try:
        with open(config_file) as data_file:    
            ngq_customization_conf = json.load(data_file)
    except Exception as e:
        sys.exit("Parsing configuration error: %s"%str(e))

    #TODO Validate - configuration
    print "\n=============="
    print "ngq_customization_dir: ", ngq_customization_dir
    print "config_file: ", config_file

print "\n=============="    
print "ngq_customization_conf: ", ngq_customization_conf

platform = "win32"
platform_dir_name = "win32"
ngq_output = os.path.join(currnet_dir, "..", "ngq_output", platform_dir_name)
ngq_src_dir = os.path.join(currnet_dir, "..", "..", "..")

if args.build:
    '''
        Patching
    '''
    print "Patching..."
    patchQGISsrc(ngq_src_dir, ngq_customization_dir, ngq_customization_conf)

    '''
        Configurating
    '''
    print "Configurating..."
    ngq_build_dir = Configurating(ngq_src_dir, ngq_output)

    '''
        Building
    '''
    print "Building..."
    project_file = None
    for file in os.listdir(ngq_build_dir):
        if file.endswith(".sln"):
            project_file = file

    if project_file is None:
        sys.exit("ERROR: MS project not found in directory: %s"%ngq_build_dir)

    res = Building(ngq_build_dir, project_file)
    if res == False:
        sys.exit("ERROR: Build error")
    
    print "remove ", ngq_build_dir
    shutil.rmtree(ngq_build_dir)

if args.installer:
    '''
        Make installer
    '''
    print "Make installer..."
    MakeInstaller(
        ngq_output, 
        args.build_num,
        currnet_working_dir,
        ngq_customization_dir, 
        ngq_customization_conf)

if args.configuration_zip is not None:    
    shutil.rmtree(ngq_customization_dir)