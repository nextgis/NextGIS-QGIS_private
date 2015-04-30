# -*- coding: utf-8 -*-

import os, sys, subprocess
import argparse
import shutil

from PyQt4 import QtGui
from PyQt4 import QtCore

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
        description='Script for NextGIS QGIS installer')
  
  parser.add_argument('-f', dest='force', action='store_true', help='set options by default')
  parser.add_argument('base_path', metavar='base_path', type=str, help='path to nextgis qgis')
  parser.add_argument('conf_path', metavar='conf_path', type=str, help='path to nextgis qgis configuration')
  
  if len(sys.argv) <= 2:
      parser.print_usage()

  args = parser.parse_args()
  
  print args.force
  
  if not args.force:
    exist_conf = os.path.exists(os.path.normpath(args.conf_path))
    
    if not exist_conf:
      shutil.copytree(
        os.path.normpath( os.path.join(os.path.normpath(args.base_path),"defalut_options") ),
        os.path.normpath( os.path.normpath(args.conf_path) )
      )
      
      qgis_settings = QtCore.QSettings(os.path.join(os.path.normpath(args.base_path), "nextgis_qgis.ini"), QtCore.QSettings.IniFormat)
      qgis_settings.setValue("RunInfo/whether_first_run", True)
      
    else:
      """
      qgis_settings = QtCore.QSettings(os.path.join(os.path.normpath(args.base_path), "nextgis_qgis.ini"), QtCore.QSettings.IniFormat)
      whether_first_run = qgis_settings.value("RunInfo/whether_first_run", True).toBool()
      qgis_settings.setValue("RunInfo/whether_first_run", True)
      
      delete_configs = False
      
      if not whether_first_run:
        app = QtGui.QApplication(sys.argv)
        reply = QtGui.QMessageBox.question(None, u"Обнаружены старые настройки QGIS",
         u"Это первый запуск ПО данной версии. \n"+
         u"При запуске были обнаружены настройки предыдущей установки данного ПО. \n" + 
         u"Удалить старые настройки? \n\n" +
         u"Внимание! При удалении старых настроек будет утеряна информация о настройках ПО, утеряны ранее установленные пользователем плагины и шаблоны проектов!\n" +
         u"При удалении старых настроек будут обновлены и установлены настройки по умолчанию!", QtGui.QMessageBox.Yes |
         QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        
        if reply == QtGui.QMessageBox.Yes:
          delete_configs = True
      
      if delete_configs:
        shutil.rmtree(os.path.normpath(args.conf_path))
        shutil.copytree(
          os.path.normpath( os.path.join(os.path.normpath(args.base_path),"defalut_options") ),
          os.path.normpath( os.path.normpath(args.conf_path) )
        )
      
        QtGui.QMessageBox.question(None, u"Настройки QGIS по-умолчанию устанвлены",
         u"Настройки по-умолчанию устанвлены!", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
      """
      pass
  else:
    print os.path.normpath(args.conf_path)
    exist_conf = os.path.exists(os.path.normpath(args.conf_path))
    print "exist_conf: ", exist_conf
    app = QtGui.QApplication(sys.argv)
    
    if exist_conf:
      reply = QtGui.QMessageBox.question(None, u"Установка настроек QGIS по-умолчанию",
       u"Будут удалены текущие натройки ПО. \n" + 
       u"Внимание! При удалении старых настроек будет утеряна информация о настройках ПО, утеряны ранее установленные пользователем плагины и шаблоны проектов!\n" +
       u"Установить настройки по-умолчанию?", QtGui.QMessageBox.Yes |
       QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        
      if reply == QtGui.QMessageBox.Yes:
        shutil.rmtree(os.path.normpath(args.conf_path))
        shutil.copytree(
          os.path.normpath( os.path.join(os.path.normpath(args.base_path),"defalut_options") ),
          os.path.normpath( os.path.normpath(args.conf_path) )
        )
        QtGui.QMessageBox.question(None, u"Настройки QGIS по-умолчанию устанвлены",
                                  u"Настройки по-умолчанию устанвлены!", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
    else:
      shutil.copytree(
          os.path.normpath( os.path.join(os.path.normpath(args.base_path),"defalut_options") ),
          os.path.normpath( os.path.normpath(args.conf_path) )
        )
      QtGui.QMessageBox.question(None, u"Настройки QGIS по-умолчанию устанвлены",
                                u"Настройки по-умолчанию устанвлены!", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
  