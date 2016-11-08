# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
    ---------------------
    Date                 : January 2016
    Copyright            : (C) 2016 by Matthias Kuhn
    Email                : matthias@opengis.ch
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Matthias Kuhn'
__date__ = 'January 2016'
__copyright__ = '(C) 2016, Matthias Kuhn'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = ':%H$'

import os
import sys
import difflib

from PyQt4.QtCore import QVariant
from qgis.core import QgsApplication, QgsFeatureRequest, QgsVectorLayer
from nose2.compat import unittest

# Get a backup, we will patch this one later
_TestCase = unittest.TestCase


class TestCase(_TestCase):

    def assertLayersEqual(self, layer_expected, layer_result, **kwargs):
        """
        :param layer_expected: The first layer to compare
        :param layer_result: The second layer to compare
        :param request: Optional, A feature request. This can be used to specify
                        an order by clause to make sure features are compared in
                        a given sequence if they don't match by default.
        :keyword compare: A map of comparison options. e.g.
                         { fields: { a: skip, b: { precision: 2 }, geometry: { precision: 5 } }
                         { fields: { __all__: cast( str ) } }
        """

        try:
            request = kwargs['request']
        except KeyError:
            request = QgsFeatureRequest()

        try:
            compare = kwargs['compare']
        except KeyError:
            compare = {}

        # Compare CRS
        _TestCase.assertEqual(self, layer_expected.dataProvider().crs().authid(), layer_result.dataProvider().crs().authid())

        # Compare features
        _TestCase.assertEqual(self, layer_expected.featureCount(), layer_result.featureCount())

        try:
            precision = compare['geometry']['precision']
        except KeyError:
            precision = 17

        expected_features = sorted(layer_expected.getFeatures(request), key=lambda f: f.id())
        result_features = sorted(layer_expected.getFeatures(request), key=lambda f: f.id())

        for feats in zip(expected_features, result_features):
            if feats[0].geometry() is not None:
                geom0 = feats[0].geometry().geometry().asWkt(precision)
            else:
                geom0 = None
            if feats[1].geometry() is not None:
                geom1 = feats[1].geometry().geometry().asWkt(precision)
            else:
                geom1 = None
            _TestCase.assertEqual(
                self,
                geom0,
                geom1,
                'Features {}/{} differ in geometry: \n\n {}\n\n vs \n\n {}'.format(
                    feats[0].id(),
                    feats[1].id(),
                    geom0,
                    geom1
                )
            )

            for attr_expected, field_expected in zip(feats[0].attributes(), layer_expected.fields().toList()):
                attr_result = feats[1][field_expected.name()]
                field_result = [fld for fld in layer_expected.fields().toList() if fld.name() == field_expected.name()][0]
                try:
                    cmp = compare['fields'][field1.name()]
                except KeyError:
                    try:
                        cmp = compare['fields']['__all__']
                    except KeyError:
                        cmp = {}

                # Skip field
                if 'skip' in cmp:
                    continue

                # Cast field to a given type
                if 'cast' in cmp:
                    if cmp['cast'] == 'int':
                        attr_expected = int(attr_expected) if attr_expected else None
                        attr_result = int(attr_result) if attr_result else None
                    if cmp['cast'] == 'float':
                        attr_expected = float(attr_expected) if attr_expected else None
                        attr_result = float(attr_result) if attr_result else None
                    if cmp['cast'] == 'str':
                        attr_expected = str(attr_expected) if attr_expected else None
                        attr_result = str(attr_result) if attr_result else None

                # Round field (only numeric so it works with __all__)
                if 'precision' in cmp and field_expected.type() in [QVariant.Int, QVariant.Double, QVariant.LongLong]:
                    attr_expected = round(attr_expected, cmp['precision'])
                    attr_result = round(attr_result, cmp['precision'])

                _TestCase.assertEqual(
                    self,
                    attr_expected,
                    attr_result,
                    'Features {}/{} differ in attributes\n\n * Field1: {} ({})\n * Field2: {} ({})\n\n * {} != {}'.format(
                        feats[0].id(),
                        feats[1].id(),
                        field_expected.name(),
                        field_expected.typeName(),
                        field_result.name(),
                        field_result.typeName(),
                        repr(attr_expected),
                        repr(attr_result)
                    )
                )

    def assertFilesEqual(self, filepath_expected, filepath_result):
        with open(filepath_expected, 'r') as file_expected:
            with open(filepath_result, 'r') as file_result:
                diff = difflib.unified_diff(
                    file_expected.readlines(),
                    file_result.readlines(),
                    fromfile='expected',
                    tofile='result',
                )
                diff = list(diff)
                self.assertEqual(0, len(diff), ''.join(diff))


# Patch unittest
unittest.TestCase = TestCase


def start_app():
    """
    Will start a QgsApplication and call all initialization code like
    registering the providers and other infrastructure. It will not load
    any plugins.

    You can always get the reference to a running app by calling `QgsApplication.instance()`.

    The initialization will only happen once, so it is safe to call this method repeatedly.

        Returns
        -------
        QgsApplication

        A QgsApplication singleton
    """
    global QGISAPP

    try:
        QGISAPP
    except NameError:
        myGuiFlag = True  # All test will run qgis in gui mode

        # In python3 we need to convert to a bytes object (or should
        # QgsApplication accept a QString instead of const char* ?)
        try:
            argvb = list(map(os.fsencode, sys.argv))
        except AttributeError:
            argvb = sys.argv

        # Note: QGIS_PREFIX_PATH is evaluated in QgsApplication -
        # no need to mess with it here.
        QGISAPP = QgsApplication(argvb, myGuiFlag)

        QGISAPP.initQgis()
        s = QGISAPP.showSettings()
        print(s)

    return QGISAPP


def stop_app():
    """
    Cleans up and exits QGIS
    """
    global QGISAPP

    QGISAPP.exitQgis()
    del QGISAPP
