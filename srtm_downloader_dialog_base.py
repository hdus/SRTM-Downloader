# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SrtmDownloader
                                 A QGIS plugin
 Downloads SRTM Tiles from NASA Server
                              -------------------
        begin                : 2017-12-30
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Dr. Horst Duester / Sourcepole AG
        email                : horst.duester@sourcepole.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSlot,  Qt
from qgis.PyQt.QtGui import QIntValidator
from qgis.PyQt.QtWidgets import QDialog,  QFileDialog, QApplication, QMessageBox
from .about.do_about import About
from qgis.core import *
from .login import Login
import urllib.request, urllib.error, urllib.parse, base64
import math,  os,  tempfile


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'srtm_downloader_dialog_base.ui'))
        
        
class SrtmDownloaderDialogBase(QDialog, FORM_CLASS):
    """
    Class documentation goes here.
    """
    
    try:            # QGIS3
        VERSION_INT = Qgis.QGIS_VERSION_INT
        VERSION = Qgis.QGIS_VERSION
    except:     # QGIS2
        VERSION_INT = QGis.QGIS_VERSION_INT
        VERSION = QGis.QGIS_VERSION
    
    
    def __init__(self, iface,  parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(SrtmDownloaderDialogBase, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.username = None
        self.password = None
        self.success = False
        self.dir = tempfile.gettempdir()
        self.btn_download.setEnabled(False)
        
        self.int_validator = QIntValidator()
        self.lne_east.setValidator(self.int_validator)
        self.lne_west.setValidator(self.int_validator)
        self.lne_north.setValidator(self.int_validator)
        self.lne_south.setValidator(self.int_validator)
        
        self.lne_east.textChanged.connect(self.coordinates_valid)
        self.lne_west.textChanged.connect(self.coordinates_valid)
        self.lne_north.textChanged.connect(self.coordinates_valid)
        self.lne_south.textChanged.connect(self.coordinates_valid)

    @pyqtSlot()
    def on_button_box_rejected(self):
        """
        Slot documentation goes here.
        """
        self.close()

    @pyqtSlot()
    def on_btn_extent_clicked(self):
        """
        Slot documentation goes here.
        """
        crsDest = QgsCoordinateReferenceSystem(4326)  # WGS84
        
        if self.VERSION_INT < 29900:    # QGIS2
            crsSrc =self.iface.mapCanvas().mapRenderer().destinationCrs()    
            xform = QgsCoordinateTransform(crsSrc, crsDest)
        else:                                           # QGIS3
            crsSrc =self.iface.mapCanvas().mapSettings().destinationCrs()
            xform = QgsCoordinateTransform()
            xform.setSourceCrs(crsSrc)
            xform.setDestinationCrs(crsDest)
            
        extent = xform.transform(self.iface.mapCanvas().extent())        

        self.lne_west.setText(str(int(math.floor(extent.xMinimum()))))
        self.lne_east.setText(str(math.ceil(extent.xMaximum())))
        self.lne_south.setText(str(int(math.floor(extent.yMinimum()))))
        self.lne_north.setText(str(math.ceil(extent.yMaximum())))


    def coordinates_valid(self,  text):
        
        if self.lne_west.text() != '' and self.lne_east.text() != '' and self.lne_south.text() != '' and self.lne_north.text() != '':
            self.btn_download.setEnabled(True)
        else:
            self.btn_download.setEnabled(False)

    def get_tiles(self,  username,  password):
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
#            if self.VERSION_INT < 29900:    # QGIS2
#                username = b'%s' % username
#                password = b'%s' % password
#            else:
#            username = str.encode(username)
#            password = str.encode(password)

            
            lat_diff = abs(int(self.lne_north.text()) - int(self.lne_south.text()))
            lon_diff = abs(int(self.lne_east.text()) - int(self.lne_west.text()))
            n_tiles = lat_diff * lon_diff
            tile_counter = 1
            
            for lat in range(int(self.lne_south.text()), int(self.lne_north.text())):
                for lon in range(int(self.lne_west.text()), int(self.lne_east.text())):
                    try:
                        self.image_progressBar.setValue(0)
                        if lon < 10 and lon >= 0:
                            lon_tx = "E00%s" % lon
                        elif lon >= 10 and lon < 100:
                            lon_tx = "E0%s" % lon
                        elif lon >= 100:
                            lon_tx = "E%s" % lon
                        elif lon > -10 and lon < 0:
                            lon_tx = "W00%s" % abs(lon)
                        elif lon <= -10 and lon > -100:
                            lon_tx = "W0%s" % abs(lon)
                        elif lon <= -100:
                            lon_tx = "W%s" % abs(lon)
    
                        if lat < 10 and lat >= 0:
                            lat_tx = "N0%s" % lat
                        elif lat >= 10 and lat < 100:
                            lat_tx = "N%s" % lat
                        elif lat > -10 and lat < 0:
                            lat_tx = "S0%s" % abs(lat)
                        elif lat < -10 and lat > -100:
                            lat_tx = "S%s" % abs(lat)
    
    
                        url = u"https://e4ftl01.cr.usgs.gov//MODV6_Dal_D/SRTM/SRTMGL1.003/2000.02.11/%s%s.SRTMGL1.hgt.zip" % (lat_tx, lon_tx)
                        file_name = "%s/%s" % (self.dir,  url.split('/')[len(url.split('/'))-1])
    
                        passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
                        passman.add_password(None, url, username, password)
                        urllib.request.install_opener(urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(passman)))
                        urllib.request.install_opener(urllib.request.build_opener(urllib.request.HTTPCookieProcessor()))
    
                        request = urllib.request.Request(url)
                        
                        if self.VERSION_INT < 29900:    # QGIS2
                            base64string = base64.b64encode(b'%s:%s' % (username, password))
                        else:
                            base64string = base64.b64encode(str.encode(username)+str.encode(':')+str.encode(password))
                            
                        request.add_header("Authorization", b"Basic %s" % base64string)   
                        u = urllib.request.urlopen(request)
    
                        f = open(file_name, 'wb')
                        meta = u.info()
                        file_size = int(meta["Content-Length"])
    
                        file_size_dl = 0
                        block_sz = 8192
                        while True:
                            buffer = u.read(block_sz)
                            if not buffer:
                                break
    
                            file_size_dl += len(buffer)
                            f.write(buffer)
                            self.image_progressBar.setValue(file_size_dl * 100. / file_size)
    
                        f.close()

                        self.overall_progressBar.setValue(tile_counter * 100 / n_tiles)
                        tile_counter += 1
    
                        if self.chk_load_image.checkState() == Qt.Checked:
                            out_image = self.unzip(file_name)
                            (dir, file) = os.path.split(out_image)
                            self.iface.addRasterLayer(out_image, file)
    
                    except urllib.error.HTTPError as err:
                        if err.code == 401:
                            QMessageBox.critical(None, self.tr('Error'),  self.tr('Earth Data Authentication Error!'))
                            QApplication.restoreOverrideCursor()
                            return False
                        elif err.code == 404:
                            # sector not covered by image
                            tile_counter += 1
                        else:
                            QMessageBox.critical(None, self.tr('Error'),  self.tr("HTTP-Error: %s") % err.reason)
                            QApplication.restoreOverrideCursor()
                            return False
    
            QApplication.restoreOverrideCursor()
            QMessageBox.information(None,  self.tr("Result"),  self.tr("Download completed"))
            return True
            

    @pyqtSlot()
    def on_btn_download_clicked(self):
        """
        Slot documentation goes here.
        """
        if self.username==None or self.password==None:
            self.login = Login(self)
            self.login.exec_()
            if self.success:       
                self.get_tiles(self.username, self.password)
            else:
                pass
        else:
            self.get_tiles(self.username, self.password)

    @pyqtSlot()
    def on_btn_file_dialog_clicked(self):
        """
        Slot documentation goes here.
        """
        from os.path import expanduser
        home = expanduser("~")
        self.dir = QFileDialog.getExistingDirectory(None, self.tr("Open Directory"),
                                                 home,
                                                 QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)

        self.lne_SRTM_path.setText(self.dir)

    def unzip(self,  zip_file):
        import zipfile
        (dir, file) = os.path.split(zip_file)

        if not dir.endswith(':') and not os.path.exists(dir):
            os.mkdir(dir)

        zf = zipfile.ZipFile(zip_file)

        # create directory structure to house files
#        self._createstructure(file, dir)

        # extract files to directory structure
        for i, name in enumerate(zf.namelist()):
            if not name.endswith('/'):
                outfile = open(os.path.join(dir, name), 'wb')
                outfile.write(zf.read(name))
                outfile.flush()
                outfile.close()
                print ("Out-File: %s" % os.path.join(dir, name))
                return os.path.join(dir, name)


    def _makedirs(self, directories, basedir):
        """ Create any directories that don't currently exist """
        for dir in directories:
            curdir = os.path.join(basedir, dir)
            if not os.path.exists(curdir):
                os.mkdir(curdir)           


    def _listdirs(self, file):
        """ Grabs all the directories in the zip structure
        This is necessary to create the structure before trying
        to extract the file to it. """
        zf = zipfile.ZipFile(file)

        dirs = []

        for name in zf.namelist():
            if name.endswith('/'):
                dirs.append(name)

        dirs.sort()
        return dirs           
    
    @pyqtSlot()
    def on_btn_about_clicked(self):
        """
        Slot documentation goes here.
        """
        self.about = About()
        self.about.exec_()
    

