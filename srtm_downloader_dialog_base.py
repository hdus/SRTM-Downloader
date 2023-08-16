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
                                                     QFileInfo)
                                      
from qgis.PyQt.QtWidgets import (QDialog,  
                                                            QMessageBox,  
                                                            QTableWidgetItem,  
                                                            QProgressBar, 
                                                            QApplication,  
                                                            QFileDialog)                                      

from .about.do_about import About
from .about.metadata import Metadata
from .download import Download

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
              
        self.spb_east.valueChanged.connect(self.coordinates_valid)
        self.spb_west.valueChanged.connect(self.coordinates_valid)
        self.spb_north.valueChanged.connect(self.coordinates_valid)
        self.spb_south.valueChanged.connect(self.coordinates_valid)
        
        self.overall_progressBar.setValue(0)
        self.downloader = Download(self,  self.iface)
        self.progress_widget_item_list = {}
        self.row_count = 0
        self.progressTableWidget.setColumnCount(2)
        self.setWindowTitle("SRTM-Downloader %s" % (Metadata().version()))
        self.lne_SRTM_path.setText(tempfile.gettempdir())
        self.min_tile = ''
        self.max_tile = ''
        self.n_tiles = 0
        
                
    @pyqtSlot()
    def on_button_box_rejected(self):
        """
        Slot documentation goes here.
        """
        self.downloader.abort_reply()
        self.close()

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
        
    def create_vrt(self):
        # Das Projektobjekt abrufen
        group_name = 'srtm_images'
        group = QgsProject.instance().layerTreeRoot().findGroup(group_name)        
        
        # Eine Liste zum Speichern der Rasterlayer erstellen
        raster_layers = []

        for child in group.children():
            raster_layers.append(child.name())
                
        outputs = {}
        
        # Build virtual raster
        alg_params = {
            'ADD_ALPHA': False,
            'ASSIGN_CRS': None,
            'EXTRA': '',
            'INPUT': raster_layers,
            'PROJ_DIFFERENCE': False,
            'RESAMPLING': 0,  # Nearest Neighbour
            'RESOLUTION': 0,  # Average
            'SEPARATE': False,
            'SRC_NODATA': '',
            'OUTPUT': '{}/{}_{}.vrt'.format(self.lne_SRTM_path.text(),  self.min_tile,  self.max_tile)
        }
        outputs['BuildVirtualRaster'] = processing.run('gdal:buildvirtualraster', alg_params, is_child_algorithm=True)
        raster_layer = QgsRasterLayer(outputs['BuildVirtualRaster']['OUTPUT'], '{}_{}'.format(self.min_tile,  self.max_tile))
        QgsProject.instance().addMapLayer(raster_layer)

    def get_tiles(self):
            lat_diff = abs(self.spb_north.value() - self.spb_south.value())
            lon_diff = abs(self.spb_east.value() - self.spb_west.value())
            self.n_tiles = lat_diff * lon_diff
            self.image_counter = 0
            self.init_progress()
            self.is_error = None

            self.overall_progressBar.setMaximum(self.n_tiles)
            self.overall_progressBar.setValue(0)
            
            for lat in range(self.spb_south.value(), self.spb_north.value()):
                for lon in range(self.spb_west.value(), self.spb_east.value()):
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
                        elif lat <= -10 and lat > -100:
                            lat_tx = "S%s" % abs(lat)
                        
                        if self.min_tile == '':
                            self.min_tile = '%s%s'  % (lat_tx, lon_tx)
                        self.max_tile = '%s%s'  % (lat_tx, lon_tx)
                        
                        try:
                            url = "https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/%s%s.SRTMGL1.hgt.zip" % (lat_tx, lon_tx)
                            file = "%s/%s" % (self.dir,  url.split('/')[len(url.split('/'))-1])
                            if not self.downloader.layer_exists('%s%s.hgt' % (lat_tx,  lon_tx)): 
                                if self.chk_load_image.checkState() == Qt.Checked:
                                    self.downloader.get_image(url,  file, lat_tx, lon_tx, True)
                                else:
                                    self.downloader.get_image(url,  file, lat_tx, lon_tx, False)
                            else:
                                self.set_progress()
                                self.download_finished(False)
                        except:
                            QMessageBox.warning(None,  self.tr("Error"),  self.tr("Wrong definition of coordinates"))
                            return False
            
            return True
            
            
    def download_finished(self,  show_message=True,  abort=False):
        if self.n_tiles == self.overall_progressBar.value() or abort:
            if show_message:
                if self.is_error != None and not "server replied: Not Found" in self.is_error:
                    QMessageBox.information(None, 'Error',  self.is_error)
            elif abort:
                    QMessageBox.information(None, self.tr("Abort"),  self.tr('Download terminated'))
            else:
                    self.create_vrt()
                    QMessageBox.information(None,  self.tr("Result"),  self.tr("Download completed"))
                
            self.button_box.setEnabled(True)
            self.n_tiles = 0
            self.image_counter = 0
        
        QApplication.restoreOverrideCursor()
            
            
    @pyqtSlot()
    def on_btn_download_clicked(self):
        """
        Slot documentation goes here.
        """
        self.min_tile = ''
        self.max_tile = ''
        self.button_box.setEnabled(True)
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
        
        
    def add_download_progress(self,  reply):
        
        is_image = QFileInfo(reply.url().path()).completeSuffix() == 'SRTMGL1.hgt.zip'
        
        if is_image:
            self.progressTableWidget.setRowCount(self.row_count+1)
            self.progressTableWidget.setItem(self.row_count,  0,  QTableWidgetItem(QFileInfo(reply.url().path()).baseName(),  Qt.DisplayRole))
            self.progressTableWidget.setCellWidget(self.row_count, 1,  QProgressBar())
            self.progress_widget_item_list[QFileInfo(reply.url().path()).baseName()] = self.row_count
            self.row_count += 1
        
    def set_progress(self,  akt_val=None,  all_val=None):
        if all_val == None:
            progress_value = self.overall_progressBar.value() + 1
            self.overall_progressBar.setValue(progress_value)
            self.lbl_file_download.setText((self.tr("Download-Progress: %s of %s images") % (progress_value,  self.n_tiles)))
                    
            if progress_value == self.n_tiles:
                self.lbl_file_download.setText((self.tr("Download-Progress: %s of %s images") % (progress_value,  self.n_tiles)))
                self.download_finished(show_message=True)
        else:
            self.overall_progressBar.setMaximum(all_val)
            self.overall_progressBar.setValue(akt_val)
