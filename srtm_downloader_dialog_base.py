#!/usr/bin/python
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SrtmDownloader
                                 A QGIS plugin
 Downloads SRTM Tiles from NASA Server
                              -------------------
        begin                : 2017-12-30
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Dr. Horst Duester
        email                : horst.duester@kappasys.ch
 ***************************************************************************/

/*************************************************************************
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
from qgis.core import (QgsCoordinateReferenceSystem,  
                                      QgsCoordinateTransform,  
                                      QgsProject, 
                                      QgsRasterLayer)
                                      
from qgis.PyQt.QtCore import (pyqtSlot,  
                                                     Qt,  
                                                     QSettings, 
                                                     QFileInfo)
                                      
from qgis.PyQt.QtWidgets import (QDialog,  
                                                            QMessageBox,  
                                                            QTableWidgetItem,  
                                                            QProgressBar, 
                                                            QApplication,  
                                                            QFileDialog, 
                                                            QDialogButtonBox)                                      

from .about.do_about import About
from .about.metadata import Metadata
from .download import Download
from .downloader import Downloader
import processing
import math
import os
import tempfile

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'srtm_downloader_dialog_base.ui'))

        
class SrtmDownloaderDialogBase(QDialog, FORM_CLASS):
    """
    Class documentation goes here.
    """
    
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
        self.cancelled = False
        self.dir = tempfile.gettempdir()
        self.btn_download.setEnabled(False)
        self.request_is_aborted = False
        self.is_error = None
        
        self.spb_east.valueChanged.connect(self.coordinates_valid)
        self.spb_west.valueChanged.connect(self.coordinates_valid)
        self.spb_north.valueChanged.connect(self.coordinates_valid)
        self.spb_south.valueChanged.connect(self.coordinates_valid)
        
        self.overall_progressBar.setValue(0)
        self.setWindowTitle("SRTM-Downloader %s" % (Metadata().version()))
        self.lne_SRTM_path.setText(tempfile.gettempdir())
        self.min_tile = ''
        self.max_tile = ''
        self.n_tiles = 0
        self.button_box.button(QDialogButtonBox.Close).setEnabled(True)
        self.button_box.button(QDialogButtonBox.Abort).setEnabled(False)
        self.settings = QSettings()
        self.init_gui()
        
        self.downloader = Downloader(self)
        
    def init_gui(self):
        dem_dict = {
            "SRTMGL3": "SRTM GL3 90m",
            "SRTMGL1": "SRTM GL1 30m",
            "SRTMGL1_E": "SRTM GL1 Ellipsoidal 30m",
            "AW3D30": "ALOS World 3D 30m",
            "AW3D30_E": "ALOS World 3D Ellipsoidal, 30m",
            "SRTM15Plus": "Global Bathymetry SRTM15+ V2.1 500m",
            "NASADEM": "NASADEM Global DEM",
            "COP30": "Copernicus Global DSM 30m",
            "COP90": "Copernicus Global DSM 90m",
            "EU_DTM": "DTM 30m",
            "GEDI_L3": "DTM 1000m",
            "GEBCOIceTopo": "Global Bathymetry 500m",
            "GEBCOSubIceTopo": "Global Bathymetry 500m",
            "CA_MRDEM_DSM": "DSM 30m",
            "CA_MRDEM_DTM": "DTM 30m"
        }
        self.cmb_demtype.clear() 
        
        for key, desc in dem_dict.items(): 
            self.cmb_demtype.addItem(f"{key} ({desc})", key)        
            
        index = self.cmb_demtype.findData(self.settings.value('/SRTM-Downloader/dem'))
        if index >= 0:
            self.cmb_demtype.setCurrentIndex(index)            
            
        self.lne_api_key.setText(self.settings.value('/SRTM-Downloader/api_key'))
                
    @pyqtSlot()
    def on_button_box_rejected(self):
        """
        Slot documentation goes here.
        """
        selected_dem = self.cmb_demtype.currentData() 
        self.settings.setValue('/SRTM-Downloader/dem', selected_dem)
        self.settings.setValue('/SRTM-Downloader/api_key', self.lne_api_key.text())
        self.reject()

    @pyqtSlot()
    def on_btn_extent_clicked(self):
        """
        Slot documentation goes here.
        """
        crsDest = QgsCoordinateReferenceSystem(4326)  # WGS84
        crsSrc =self.iface.mapCanvas().mapSettings().destinationCrs()
        xform = QgsCoordinateTransform()
        xform.setSourceCrs(crsSrc)
        xform.setDestinationCrs(crsDest)
            
        extent = xform.transform(self.iface.mapCanvas().extent())        

        self.spb_west.setValue(math.floor(extent.xMinimum()))
        self.spb_east.setValue(math.ceil(extent.xMaximum()))
        self.spb_south.setValue(math.floor(extent.yMinimum()))
        self.spb_north.setValue(math.ceil(extent.yMaximum()))

    def coordinates_valid(self,  text):
        if self.spb_north.value() < -56 and self.spb_south.value() < -56: 
            res = QMessageBox.warning(
                None,
                self.tr("Box out of covered area"),
                self.tr("""The area you have defined is completely outside the area covered by the SRTM tiles. """),
                QMessageBox.StandardButtons(
                    QMessageBox.Cancel))
            self.btn_download.setEnabled(False)
        elif self.spb_north.value() > 59 or self.spb_south.value() < -56 and self.spb_north.value() != 0:
            res = QMessageBox.warning(
                None,
                self.tr("Box out of covered area"),
                self.tr("""The area you have defined is partly outside the area covered by the SRTM tiles. Do you like to continue?"""),
                QMessageBox.StandardButtons(
                    QMessageBox.No |
                    QMessageBox.Yes))            
            if res == QMessageBox.Yes:
                self.btn_download.setEnabled(True)
            else:
                self.btn_download.setEnabled(False)
        else:
            self.btn_download.setEnabled(True)
        

    def get_tiles(self):
        self.lbl_downloaded_bytes.setText("Preparing Download ...")

        product = self.cmb_demtype.currentData()
        
        out_path = '/tmp/{}.tiff'.format(product)
        out_path = '{}/{}.tiff'.format(self.lne_SRTM_path.text(),  product)
        
        self.downloader.download_opentopo_globaldem(product, 
                            self.spb_south.value(), 
                            self.spb_north.value(), 
                            self.spb_west.value(), 
                            self.spb_east.value(), 
                            out_path)
        
        return True
            
            
    @pyqtSlot()
    def on_btn_download_clicked(self):
        """
        Slot documentation goes here.
        """
        self.min_tile = ''
        self.max_tile = ''
        self.button_box.setEnabled(True)
        self.button_box.button(QDialogButtonBox.Close).setEnabled(False)
        self.button_box.button(QDialogButtonBox.Abort).setEnabled(True)
        self.get_tiles()

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
    
    @pyqtSlot()
    def on_btn_about_clicked(self):
        """
        Slot documentation goes here.
        """
        self.about = About()
        self.about.exec_()
        
    def init_progress(self):
        self.overall_progressBar.setMaximum(self.n_tiles)
        self.overall_progressBar.setValue(0)
        self.lbl_file_download.setText((self.tr("Download-Progress: %s of %s images") % (0,  self.n_tiles)))


    @pyqtSlot(str)
    def on_lne_api_key_textChanged(self, p0):
        """
        Slot documentation goes here.

        @param p0 DESCRIPTION
        @type str
        """
        self.settings.setValue('/SRTM-Downloader/api_key', p0)
        
