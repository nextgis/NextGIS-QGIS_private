# -*- coding: utf-8 -*-
"""QGIS Unit tests for the OGR/GPKG provider.

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
__author__ = 'Even Rouault'
__date__ = '2016-04-21'
__copyright__ = 'Copyright 2016, Even Rouault'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import qgis  # NOQA

import os
import tempfile
import shutil
import glob
from osgeo import gdal, ogr

from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsFeatureRequest, QgsRectangle
from qgis.testing import start_app, unittest
from utilities import unitTestDataPath

start_app()


def GDAL_COMPUTE_VERSION(maj, min, rev):
    return ((maj) * 1000000 + (min) * 10000 + (rev) * 100)


class ErrorReceiver():

    def __init__(self):
        self.msg = None

    def receiveError(self, msg):
        self.msg = msg


class TestPyQgsOGRProviderGpkg(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        # Create test layer
        cls.basetestpath = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        """Run after all tests"""
        shutil.rmtree(cls.basetestpath, True)

    def XXXXtestSingleToMultiPolygonPromotion(self):

        tmpfile = os.path.join(self.basetestpath, 'testSingleToMultiPolygonPromotion.gpkg')
        ds = ogr.GetDriverByName('GPKG').CreateDataSource(tmpfile)
        lyr = ds.CreateLayer('test', geom_type=ogr.wkbMultiPolygon)
        ds = None

        vl = QgsVectorLayer(u'{}|layerid=0'.format(tmpfile), u'test', u'ogr')
        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromWkt('POLYGON ((0 0,0 1,1 1,0 0))'))
        vl.dataProvider().addFeatures([f])
        got = [f for f in vl.getFeatures()][0]
        got_geom = got.geometry()
        reference = QgsGeometry.fromWkt('MultiPolygon (((0 0, 0 1, 1 1, 0 0)))')
        # The geometries must be binarily identical
        self.assertEqual(got_geom.asWkb(), reference.asWkb(), 'Expected {}, got {}'.format(reference.exportToWkt(), got_geom.exportToWkt()))

    def XXXXtestCurveGeometryType(self):
        if int(gdal.VersionInfo('VERSION_NUM')) < GDAL_COMPUTE_VERSION(2, 0, 0):
            return

        tmpfile = os.path.join(self.basetestpath, 'testCurveGeometryType.gpkg')
        ds = ogr.GetDriverByName('GPKG').CreateDataSource(tmpfile)
        lyr = ds.CreateLayer('test', geom_type=ogr.wkbCurvePolygon)
        ds = None

        vl = QgsVectorLayer(u'{}'.format(tmpfile), u'test', u'ogr')
        self.assertEqual(vl.dataProvider().subLayers(), [u'0:test:0:CurvePolygon'])
        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromWkt('POLYGON ((0 0,0 1,1 1,0 0))'))
        vl.dataProvider().addFeatures([f])
        got = [f for f in vl.getFeatures()][0]
        got_geom = got.geometry()
        reference = QgsGeometry.fromWkt('CurvePolygon (((0 0, 0 1, 1 1, 0 0)))')
        # The geometries must be binarily identical
        self.assertEqual(got_geom.asWkb(), reference.asWkb(), 'Expected {}, got {}'.format(reference.exportToWkt(), got_geom.exportToWkt()))

    def internalTestBug15351(self, orderClosing):

        tmpfile = os.path.join(self.basetestpath, 'testBug15351.gpkg')
        ds = ogr.GetDriverByName('GPKG').CreateDataSource(tmpfile)
        lyr = ds.CreateLayer('test', geom_type=ogr.wkbPoint)
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetGeometry(ogr.CreateGeometryFromWkt('POINT(0 0)'))
        lyr.CreateFeature(f)
        f = None
        ds = None

        vl = QgsVectorLayer(u'{}'.format(tmpfile), u'test', u'ogr')
        self.assertTrue(vl.startEditing())
        self.assertTrue(vl.changeGeometry(1, QgsGeometry.fromWkt('Point (3 50)')))

        # Iterate over features (will open a new OGR connection), but do not
        # close the iterator for now
        it = vl.getFeatures()
        f = QgsFeature()
        it.nextFeature(f)

        if orderClosing == 'closeIter_commit_closeProvider':
            it = None

        # Commit changes
        cbk = ErrorReceiver()
        vl.dataProvider().raiseError.connect(cbk.receiveError)
        self.assertTrue(vl.commitChanges())
        self.assertIsNone(cbk.msg)

        # Close layer and iterator in different orders
        if orderClosing == 'closeIter_commit_closeProvider':
            vl = None
        elif orderClosing == 'commit_closeProvider_closeIter':
            vl = None
            it = None
        else:
            assert orderClosing == 'commit_closeIter_closeProvider'
            it = None
            vl = None

        # Test that we succeeded restoring default journal mode, and we
        # are not let in WAL mode.
        ds = ogr.Open(tmpfile)
        lyr = ds.ExecuteSQL('PRAGMA journal_mode')
        f = lyr.GetNextFeature()
        res = f.GetField(0)
        ds.ReleaseResultSet(lyr)
        ds = None
        self.assertEqual(res, 'delete')

    # We need GDAL 2.0 to issue PRAGMA journal_mode
    # Note: for that case, we don't strictly need turning on WAL
    def testBug15351_closeIter_commit_closeProvider(self):
        if int(gdal.VersionInfo('VERSION_NUM')) < GDAL_COMPUTE_VERSION(2, 0, 0):
            return
        self.internalTestBug15351('closeIter_commit_closeProvider')

    # We need GDAL 2.0 to issue PRAGMA journal_mode
    def testBug15351_closeIter_commit_closeProvider(self):
        if int(gdal.VersionInfo('VERSION_NUM')) < GDAL_COMPUTE_VERSION(2, 0, 0):
            return
        self.internalTestBug15351('closeIter_commit_closeProvider')

    # We need GDAL 2.0 to issue PRAGMA journal_mode
    def testBug15351_commit_closeIter_closeProvider(self):
        if int(gdal.VersionInfo('VERSION_NUM')) < GDAL_COMPUTE_VERSION(2, 0, 0):
            return
        self.internalTestBug15351('commit_closeIter_closeProvider')

    @unittest.expectedFailure(int(gdal.VersionInfo('VERSION_NUM')) < GDAL_COMPUTE_VERSION(2, 1, 2))
    def testGeopackageExtentUpdate(self):
        ''' test http://hub.qgis.org/issues/15273 '''
        tmpfile = os.path.join(self.basetestpath, 'testGeopackageExtentUpdate.gpkg')
        ds = ogr.GetDriverByName('GPKG').CreateDataSource(tmpfile)
        lyr = ds.CreateLayer('test', geom_type=ogr.wkbPoint)
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetGeometry(ogr.CreateGeometryFromWkt('POINT(0 0)'))
        lyr.CreateFeature(f)
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetGeometry(ogr.CreateGeometryFromWkt('POINT(1 1)'))
        lyr.CreateFeature(f)
        f = None
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetGeometry(ogr.CreateGeometryFromWkt('POINT(1 0.5)'))
        lyr.CreateFeature(f)
        f = None
        gdal.ErrorReset()
        ds.ExecuteSQL('RECOMPUTE EXTENT ON test')
        has_error = gdal.GetLastErrorMsg() != ''
        ds = None
        if has_error:
            print('Too old GDAL trunk version. Please update')
            return

        vl = QgsVectorLayer(u'{}'.format(tmpfile), u'test', u'ogr')

        # Test moving a geometry that touches the bbox
        self.assertTrue(vl.startEditing())
        self.assertTrue(vl.changeGeometry(1, QgsGeometry.fromWkt('Point (0.5 0)')))
        self.assertTrue(vl.commitChanges())
        reference = QgsGeometry.fromRect(QgsRectangle(0.5, 0.0, 1.0, 1.0))
        provider_extent = QgsGeometry.fromRect(vl.extent())
        self.assertTrue(QgsGeometry.compare(provider_extent.asPolygon()[0], reference.asPolygon()[0], 0.00001),
                        provider_extent.asPolygon()[0])

        # Test deleting a geometry that touches the bbox
        self.assertTrue(vl.startEditing())
        self.assertTrue(vl.deleteFeature(2))
        self.assertTrue(vl.commitChanges())
        reference = QgsGeometry.fromRect(QgsRectangle(0.5, 0.0, 1.0, 0.5))
        provider_extent = QgsGeometry.fromRect(vl.extent())
        self.assertTrue(QgsGeometry.compare(provider_extent.asPolygon()[0], reference.asPolygon()[0], 0.00001),
                        provider_extent.asPolygon()[0])

if __name__ == '__main__':
    unittest.main()
