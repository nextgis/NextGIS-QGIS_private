# -*- coding: utf-8 -*-

"""
***************************************************************************
    Processing.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import sys

from PyQt4.QtCore import Qt, QCoreApplication
from PyQt4.QtGui import QApplication, QCursor

from qgis.utils import iface
from qgis.core import QgsMessageLog

import processing
from processing.gui import AlgorithmClassification
from processing.modeler.ModelerUtils import ModelerUtils
from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.ProcessingLog import ProcessingLog
from processing.gui.MessageBarProgress import MessageBarProgress
from processing.gui.RenderingStyles import RenderingStyles
from processing.gui.Postprocessing import handleAlgorithmResults
from processing.gui.AlgorithmExecutor import runalg
from processing.modeler.ModelerAlgorithmProvider import ModelerAlgorithmProvider
from processing.modeler.ModelerOnlyAlgorithmProvider import ModelerOnlyAlgorithmProvider
from processing.algs.qgis.QGISAlgorithmProvider import QGISAlgorithmProvider
from processing.algs.grass.GrassAlgorithmProvider import GrassAlgorithmProvider
from processing.algs.grass7.Grass7AlgorithmProvider import Grass7AlgorithmProvider
from processing.algs.lidar.LidarToolsAlgorithmProvider import LidarToolsAlgorithmProvider
from processing.algs.gdal.GdalOgrAlgorithmProvider import GdalOgrAlgorithmProvider
from processing.algs.otb.OTBAlgorithmProvider import OTBAlgorithmProvider
from processing.algs.r.RAlgorithmProvider import RAlgorithmProvider
from processing.algs.saga.SagaAlgorithmProvider import SagaAlgorithmProvider
from processing.script.ScriptAlgorithmProvider import ScriptAlgorithmProvider
from processing.algs.taudem.TauDEMAlgorithmProvider import TauDEMAlgorithmProvider
from processing.tools import dataobjects


class Processing:

    listeners = []
    providers = []

    # A dictionary of algorithms. Keys are names of providers
    # and values are list with all algorithms from that provider
    algs = {}

    # Same structure as algs
    actions = {}

    # All the registered context menu actions for the toolbox
    contextMenuActions = []

    modeler = ModelerAlgorithmProvider()

    @staticmethod
    def addProvider(provider, updateList=True):
        """Use this method to add algorithms from external providers.
        """

        # Note: this might slow down the initialization process if
        # there are many new providers added. Should think of a
        # different solution
        try:
            provider.initializeSettings()
            Processing.providers.append(provider)
            ProcessingConfig.readSettings()
            if updateList:
                Processing.updateAlgsList()
        except:
            ProcessingLog.addToLog(
                ProcessingLog.LOG_ERROR,
                Processing.tr('Could not load provider: %s\n%s')
                % (provider.getDescription(), unicode(sys.exc_info()[1])))
            Processing.removeProvider(provider)

    @staticmethod
    def removeProvider(provider):
        """Use this method to remove a provider.

        This method should be called when unloading a plugin that
        contributes a provider.
        """
        try:
            provider.unload()
            Processing.providers.remove(provider)
            del Processing.algs[provider.getName()]
            Processing.fireAlgsListHasChanged()
        except:
            # This try catch block is here to avoid problems if the
            # plugin with a provider is unloaded after the Processing
            # framework itself has been unloaded. It is a quick fix
            # before I found out how to properly avoid that.
            pass

    @staticmethod
    def getProviderFromName(name):
        """Returns the provider with the given name."""
        for provider in Processing.providers:
            if provider.getName() == name:
                return provider
        return Processing.modeler

    @staticmethod
    def initialize():
        # Add the basic providers
        Processing.addProvider(QGISAlgorithmProvider(), updateList=False)
        Processing.addProvider(ModelerOnlyAlgorithmProvider(), updateList=False)
        Processing.addProvider(GdalOgrAlgorithmProvider(), updateList=False)
        Processing.addProvider(LidarToolsAlgorithmProvider(), updateList=False)
        Processing.addProvider(OTBAlgorithmProvider(), updateList=False)
        Processing.addProvider(RAlgorithmProvider(), updateList=False)
        Processing.addProvider(SagaAlgorithmProvider(), updateList=False)
        Processing.addProvider(GrassAlgorithmProvider(), updateList=False)
        Processing.addProvider(Grass7AlgorithmProvider(), updateList=False)
        Processing.addProvider(ScriptAlgorithmProvider(), updateList=False)
        Processing.addProvider(TauDEMAlgorithmProvider(), updateList=False)
        Processing.addProvider(Processing.modeler, updateList=False)
        Processing.modeler.initializeSettings()

        # And initialize
        AlgorithmClassification.loadClassification()
        ProcessingConfig.initialize()
        ProcessingConfig.readSettings()
        RenderingStyles.loadStyles()
        Processing.loadFromProviders()
        # Inform registered listeners that all providers' algorithms have been loaded
        Processing.fireAlgsListHasChanged()

    @staticmethod
    def updateAlgsList():
        """Call this method when there has been any change that
        requires the list of algorithms to be created again from
        algorithm providers.
        """
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        Processing.loadFromProviders()
        Processing.fireAlgsListHasChanged()
        QApplication.restoreOverrideCursor()

    @staticmethod
    def loadFromProviders():
        Processing.loadAlgorithms()
        Processing.loadActions()
        Processing.loadContextMenuActions()

    @staticmethod
    def updateProviders():
        providers = [p for p in Processing.providers if p.getName() != "model"]
        for provider in providers:
            provider.loadAlgorithms()

    @staticmethod
    def addAlgListListener(listener):
        """
        Listener should implement a algsListHasChanged() method.

        Whenever the list of algorithms changes, that method will be
        called for all registered listeners.
        """
        Processing.listeners.append(listener)

    @staticmethod
    def removeAlgListListener(listener):
        try:
            Processing.listeners.remove(listener)
        except:
            pass

    @staticmethod
    def fireAlgsListHasChanged():
        for listener in Processing.listeners:
            listener.algsListHasChanged()

    @staticmethod
    def loadAlgorithms():
        Processing.algs = {}
        Processing.updateProviders()
        providers = [p for p in Processing.providers if p.getName() != "model"]
        for provider in providers:
            providerAlgs = provider.algs
            algs = {}
            for alg in providerAlgs:
                algs[alg.commandLineName()] = alg
            Processing.algs[provider.getName()] = algs

        provs = {}
        for provider in Processing.providers:
            provs[provider.getName()] = provider

        ModelerUtils.allAlgs = Processing.algs
        ModelerUtils.providers = provs

        Processing.modeler.loadAlgorithms()

        algs = {}
        for alg in Processing.modeler.algs:
            algs[alg.commandLineName()] = alg
        Processing.algs[Processing.modeler.getName()] = algs

    @staticmethod
    def loadActions():
        for provider in Processing.providers:
            providerActions = provider.actions
            actions = list()
            for action in providerActions:
                actions.append(action)
            Processing.actions[provider.getName()] = actions

        Processing.actions[provider.getName()] = actions

    @staticmethod
    def loadContextMenuActions():
        Processing.contextMenuActions = []
        for provider in Processing.providers:
            providerActions = provider.contextMenuActions
            for action in providerActions:
                Processing.contextMenuActions.append(action)

    @staticmethod
    def getAlgorithm(name):
        for provider in Processing.algs.values():
            if name in provider:
                return provider[name]
        return None

    @staticmethod
    def getAlgorithmFromFullName(name):
        for provider in Processing.algs.values():
            for alg in provider.values():
                if alg.name == name:
                    return alg
        return None

    @staticmethod
    def getObject(uri):
        """Returns the QGIS object identified by the given URI."""
        return dataobjects.getObjectFromUri(uri)

    @staticmethod
    def runandload(name, *args):
        Processing.runAlgorithm(name, handleAlgorithmResults, *args)

    @staticmethod
    def runAlgorithm(algOrName, onFinish, *args, **kwargs):
        if isinstance(algOrName, GeoAlgorithm):
            alg = algOrName
        else:
            alg = Processing.getAlgorithm(algOrName)
        if alg is None:
            print 'Error: Algorithm not found\n'
            QgsMessageLog.logMessage(Processing.tr('Error: Algorithm {0} not found\n').format(algOrName), Processing.tr("Processing"))
            return
        alg = alg.getCopy()

        if len(args) == 1 and isinstance(args[0], dict):
            # Set params by name and try to run the alg even if not all parameter values are provided,
            # by using the default values instead.
            setParams = []
            for (name, value) in args[0].items():
                param = alg.getParameterFromName(name)
                if param and param.setValue(value):
                    setParams.append(name)
                    continue
                output = alg.getOutputFromName(name)
                if output and output.setValue(value):
                    continue
                print 'Error: Wrong parameter value %s for parameter %s.' % (value, name)
                QgsMessageLog.logMessage(Processing.tr('Error: Wrong parameter value {0} for parameter {1}.').format(value, name), Processing.tr("Processing"))
                ProcessingLog.addToLog(
                    ProcessingLog.LOG_ERROR,
                    Processing.tr('Error in %s. Wrong parameter value %s for parameter %s.') % (
                        alg.name, value, name)
                )
                return
            # fill any missing parameters with default values if allowed
            for param in alg.parameters:
                if param.name not in setParams:
                    if not param.setDefaultValue():
                        print ('Error: Missing parameter value for parameter %s.' % (param.name))
                        QgsMessageLog.logMessage(Processing.tr('Error: Missing parameter value for parameter {0}.').format(param.name), Processing.tr("Processing"))
                        ProcessingLog.addToLog(
                            ProcessingLog.LOG_ERROR,
                            Processing.tr('Error in %s. Missing parameter value for parameter %s.') % (
                                alg.name, param.name)
                        )
                        return
        else:
            if len(args) != alg.getVisibleParametersCount() + alg.getVisibleOutputsCount():
                print 'Error: Wrong number of parameters'
                QgsMessageLog.logMessage(Processing.tr('Error: Wrong number of parameters'), Processing.tr("Processing"))
                processing.alghelp(algOrName)
                return
            i = 0
            for param in alg.parameters:
                if not param.hidden:
                    if not param.setValue(args[i]):
                        print 'Error: Wrong parameter value: ' \
                            + unicode(args[i])
                        QgsMessageLog.logMessage(Processing.tr('Error: Wrong parameter value: ') + unicode(args[i]), Processing.tr("Processing"))
                        return
                    i = i + 1

            for output in alg.outputs:
                if not output.hidden:
                    if not output.setValue(args[i]):
                        print 'Error: Wrong output value: ' + unicode(args[i])
                        QgsMessageLog.logMessage(Processing.tr('Error: Wrong output value: ') + unicode(args[i]), Processing.tr("Processing"))
                        return
                    i = i + 1

        msg = alg._checkParameterValuesBeforeExecuting()
        if msg:
            print 'Unable to execute algorithm\n' + unicode(msg)
            QgsMessageLog.logMessage(Processing.tr('Unable to execute algorithm\n{0}').format(msg), Processing.tr("Processing"))
            return

        if not alg.checkInputCRS():
            print 'Warning: Not all input layers use the same CRS.\n' \
                + 'This can cause unexpected results.'
            QgsMessageLog.logMessage(Processing.tr('Warning: Not all input layers use the same CRS.\nThis can cause unexpected results.'), Processing.tr("Processing"))

        # Don't set the wait cursor twice, because then when you
        # restore it, it will still be a wait cursor.
        overrideCursor = False
        if iface is not None:
            cursor = QApplication.overrideCursor()
            if cursor is None or cursor == 0:
                QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
                overrideCursor = True
            elif cursor.shape() != Qt.WaitCursor:
                QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
                overrideCursor = True

        progress = None
        if kwargs is not None and "progress" in kwargs.keys():
            progress = kwargs["progress"]
        elif iface is not None:
            progress = MessageBarProgress(alg.name)

        ret = runalg(alg, progress)
        if ret:
            if onFinish is not None:
                onFinish(alg, progress)
        else:
            QgsMessageLog.logMessage(Processing.tr("There were errors executing the algorithm."), Processing.tr("Processing"))

        if overrideCursor:
            QApplication.restoreOverrideCursor()
        if isinstance(progress, MessageBarProgress):
            progress.close()
        return alg

    @staticmethod
    def tr(string, context=''):
        if context == '':
            context = 'Processing'
        return QCoreApplication.translate(context, string)
