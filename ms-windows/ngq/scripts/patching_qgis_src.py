# -*- coding: utf-8 -*-
import os
import sys
import shutil
import tempfile
import subprocess

currnet_dir = os.path.dirname( os.path.abspath(__file__) )
patches_templates_dir = os.path.join(currnet_dir, "qgis_patches")

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

def applyOnePatch(qgis_src_dir, patch_file):    
    cwd = os.getcwd()
    os.chdir(qgis_src_dir)
    cmd = "git apply --ignore-whitespace \"%(patch)s\" " % {
        "patch": patch_file
    }
    
    print "cmd: ", cmd
    
    try:
        subprocess.call(cmd, stdout=sys.stdout)
    except:
        print "ERROR: Patching QGIS sources faild. cmd:\n", cmd
    
    os.chdir(cwd)
    
def replaceFile(qgis_src_dir, settings_dir, configuration, config_key, ngq_src_dest):
    if configuration.has_key(config_key):
        shutil.copyfile(
            os.path.join(settings_dir, configuration[config_key]), 
            os.path.join(qgis_src_dir, ngq_src_dest) 
        )

def patchQGISsrc(qgis_src_dir, settings_dir, configuration):
    """
        Change icon & splash
    """
    '''
    if configuration.has_key(u'ngq_icon'):
        shutil.copyfile(
            os.path.join(settings_dir, configuration[u'ngq_icon']), 
            os.path.join(qgis_src_dir, "src/app/qgis.ico") 
        )
    
    if configuration.has_key(u'ngq_splash'):
        shutil.copyfile(
            os.path.join(settings_dir, configuration[u'ngq_splash']), 
            os.path.join(qgis_src_dir, "images/splash/splash.png") 
        )
    '''
    replaceFile(qgis_src_dir, settings_dir, configuration, u'ngq_icon', "src/app/qgis.ico")
    replaceFile(qgis_src_dir, settings_dir, configuration, u'ngq_splash', "images/splash/splash.png")
    replaceFile(qgis_src_dir, settings_dir, configuration, u'ngq_icon_svg', "images/themes/default/mActionHelpAbout.svg")
    replaceFile(qgis_src_dir, settings_dir, configuration, u'ngq_icon_png_16', "images/icons/qgis-icon-16x16.png")
    replaceFile(qgis_src_dir, settings_dir, configuration, u'ngq_icon_png_64', "images/icons/qgis-icon-60x60.png")
    
    patch_dir = tempfile.mkdtemp('','ngq_patch_')
    
    """
        Change qgis title
    """
    if configuration.has_key(u'ngq_title_en') and configuration.has_key(u'ngq_title_tr'):
        patch_template_filename = os.path.join( patches_templates_dir, "set_title.patch.template")
        patch_filename = os.path.join(patch_dir, "set_title.patch")
        
        vars = {
            u'NGQ_TITLE_SRC': configuration[u'ngq_title_en'],
            u'NGQ_TITLE_TRANSLATE': configuration[u'ngq_title_tr']
        }
        processPatchTemplate(vars, patch_template_filename, patch_filename)

        if not os.path.exists(patch_filename):
            sys.exit( "ERROR: Patch file (%s) not found"%patch_filename)
        
        applyOnePatch(qgis_src_dir, patch_filename)
    
    #shutil.rmtree(patch_dir)