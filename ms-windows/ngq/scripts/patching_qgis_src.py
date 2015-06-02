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
def putFile(qgis_src_dir, settings_dir, src, dest):
    dest_dir_name = os.path.dirname(os.path.join(qgis_src_dir, dest))
    if os.path.exists(dest_dir_name) == False:
        os.mkdir(dest_dir_name)
    shutil.copyfile(
        os.path.join(settings_dir, src), 
        os.path.join(qgis_src_dir, dest)
    )

def addTranslate(expression_en, expression_tr, context, dst_filename):
    translation_dir = tempfile.mkdtemp('','ngq_translate_')
    additional_tr_filename = os.path.join(translation_dir, 'additional.tr')
    f = open(additional_tr_filename, 'w')
    
    f.write(
        '''<TS version="2.0" language="ru">
        <context>
            <name>%s</name>
            <message>
                <source>%s</source>
                <translation>%s</translation>
            </message>
        </context>
        
        </TS>'''%(context.encode('utf-8'), expression_en.encode('utf-8'), expression_tr.encode('utf-8'))
    )
    f.close()
    
    try:
        res = subprocess.check_call(['lconvert', '-i', additional_tr_filename, '-i', dst_filename, '-o', dst_filename])
        
    except subprocess.CalledProcessError as ex:
        sys.exit("ERROR! Merge ts files (lconvert): %s\n"%str(ex))
    except:
        sys.exit("ERROR!  Merge ts files (lconvert): Unexpected error: %s\n"%sys.exc_info()[0])
    
    shutil.rmtree(translation_dir)
    
def patchQGISsrc(qgis_src_dir, settings_dir, configuration):
    """
        Change icon & splash
    """
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
    
    """
        Change qgis about
    """
    ts_dst_filename = os.path.join(qgis_src_dir, 'i18n', 'qgis_ru.ts')
    if configuration.has_key(u'ngq_about_pages'):
        shutil.copytree(
            os.path.join(settings_dir, u'about_pages_contents'),
            os.path.join(qgis_src_dir, u'resources/about_pages_contents'),
            )
        #page_indexes = configuration[u'ngq_about_pages'].keys()
        page_indexes = range(0, len(configuration[u'ngq_about_pages']))
        #page_indexes.sort()
        indexes4del =[]
        indexes4add =[]
        names4add =[]
        files4add =[]
        for index in page_indexes:
            page_setting = configuration[u'ngq_about_pages'][index]
            if page_setting[u'visible'] == False:
                indexes4del.append(index)
            if page_setting.has_key(u'name') and page_setting.has_key(u'content_file'):
                indexes4add.append(index)
                names4add.append(page_setting[u'name'][0])
                files4add.append(page_setting[u'content_file'])
                #putFile(qgis_src_dir, settings_dir, u'about_pages_contents/%s'%page_setting[u'content_file'], "resources/about_pages_contents/%s"%page_setting[u'content_file'])
                addTranslate(page_setting[u'name'][0], page_setting[u'name'][1], "QgsAbout", ts_dst_filename)
        patch_template_filename = os.path.join( patches_templates_dir, "change_about_dialog.patch.template")
        patch_filename = os.path.join(patch_dir, "change_about_dialog.patch")
        
        vars = {
            u'LIST_INDEX_DEL': ",".join([str(v) for v in indexes4del]),
            u'LIST_INDEX_ADD': ",".join([str(v) for v in indexes4add]),
            u'LIST_NAME_ADD': ",".join(['"%s"'%v for v in names4add]),
            u'LIST_CONTENT_FILENAME_ADD': ",".join(['"%s"'%v for v in files4add])
        }
        processPatchTemplate(vars, patch_template_filename, patch_filename)
        
        
        
        if not os.path.exists(patch_filename):
            sys.exit( "ERROR: Patch file (%s) not found"%patch_filename)
        
        applyOnePatch(qgis_src_dir, patch_filename)
    shutil.rmtree(patch_dir)