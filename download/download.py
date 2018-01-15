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
from qgis.core import *
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply


import os
      
class Download:

    def __init__(self,  parent=None,  iface=None):    
        self.opener = parent
        self.iface = iface

    def get_image(self,  url,  filename,  lat_tx,  lon_tx, load_to_canvas=True):
        
        layer_name = "%s%s.hgt" % (lat_tx,  lon_tx)
        
        if len(QgsMapLayerRegistry.instance().mapLayersByName(layer_name)) == 0:
            self.filename = filename 
            self.load_to_canvas = load_to_canvas
            req = QNetworkRequest(QUrl(url))
            self.nam = QgsNetworkAccessManager.instance()
            self.nam.finished.connect(self.replyFinished)
            self.nam.get(req)  
        else:
            self.set_progress()

    def replyFinished(self, reply): 

            if  reply.error() != QNetworkReply.NoError:
               self.nam.get(QNetworkRequest(reply.url()))          

            possibleRedirectUrl = reply.attribute(QNetworkRequest.RedirectionTargetAttribute);
    
        # We'll deduct if the redirection is valid in the redirectUrl function
            _urlRedirectedTo = possibleRedirectUrl
    
        # If the URL is not empty, we're being redirected. 
            if _urlRedirectedTo != None:
                self.nam.get(QNetworkRequest(_urlRedirectedTo))                
            else:                    
                result = reply.readAll()
                f = open(self.filename, 'wb')
                f.write(result)
                f.close()      
                
                try:
                    if self.load_to_canvas:
                        out_image = self.unzip(self.filename)
                        (dir, file) = os.path.split(out_image)
                        self.iface.addRasterLayer(out_image, file)
                    self.set_progress()
                except:
                    pass
                    
            # Clean up. */
                reply.deleteLater()

                
        
    def unzip(self,  zip_file):
        import zipfile
        (dir, file) = os.path.split(zip_file)

        if not dir.endswith(':') and not os.path.exists(dir):
            os.mkdir(dir)
        
        try:
            zf = zipfile.ZipFile(zip_file)
    
            # extract files to directory structure
            for i, name in enumerate(zf.namelist()):
                if not name.endswith('/'):
                    outfile = open(os.path.join(dir, name), 'wb')
                    outfile.write(zf.read(name))
                    outfile.flush()
                    outfile.close()
                    print ("Out-File: %s" % os.path.join(dir, name))
                    return os.path.join(dir, name)
        except:
            return None


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
        
    def set_progress(self):
        self.opener.overall_progressBar.setMaximum(self.opener.n_tiles)
        progress_value = self.opener.overall_progressBar.value() + 1
        self.opener.overall_progressBar.setValue(progress_value)
        self.lbl_file_download.setText((self.tr("Download-Progress: %s of %s") % (progress_value,  self.opener.n_tiles)))
