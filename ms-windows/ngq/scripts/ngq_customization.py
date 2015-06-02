# -*- coding: utf-8 -*-
import os
import tempfile
import shutil
from PyQt4.QtCore import QSettings

def processPatchTemplate(vars, src_filename, dst_filename):
    f = open( src_filename, 'r')
    lines = f.readlines()
    f.close()

    new_lines = []
    for line in lines:
        for var_name in vars.keys():
            var_value = vars[var_name]
            var_value.encode("utf-8")
            line = line.replace("{%s}"%var_name, var_value)
            
        new_lines.append(str(line.encode("utf-8")))
    
    f = open( dst_filename,'w')
    f.writelines(new_lines)
    f.close()

def prepareRunScripts(default_scripts_dir, prog_name):
    scripts_dir = tempfile.mkdtemp('','ngq_run_scripts_')
    vars = {"PROGRAM_NAME":prog_name}
    processPatchTemplate( vars, os.path.join(default_scripts_dir, "qgis.bat.in"), os.path.join(scripts_dir, "qgis.bat") )
    processPatchTemplate( vars, os.path.join(default_scripts_dir, "qgis_preruner.bat.in"), os.path.join(scripts_dir, "qgis_preruner.bat") )
    return scripts_dir
    
def prepareQGISSettings(default_settings_dir, plugins):
    settings_dir = tempfile.mktemp('','ngq_settings_')
    
    shutil.copytree(default_settings_dir, settings_dir)
    
    ini_file = os.path.join(settings_dir, "QGIS2.ini")
    #config = ConfigParser.RawConfigParser()
    #config.read(ini_file)
    config = QSettings(ini_file, QSettings.IniFormat)
    
    # activate python plugin in settings
    #if config.has_section('PythonPlugins') == False:
    #    config.add_section('PythonPlugins')
    for plugin in plugins:
        #config.set('PythonPlugins', os.path.basename(plugin), 'true')
        config.setValue("PythonPlugins/%s"%os.path.basename(plugin), True)
        
    #with open(ini_file, 'wb') as configfile:
    #    config.write(configfile)
        
    return settings_dir