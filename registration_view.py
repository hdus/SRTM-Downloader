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
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtWidgets import QDialog
import os
    
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'registration_view.ui'))


class RegistrationView(QDialog, FORM_CLASS):
    """
    Class documentation goes here.
    """
    def __init__(self, link,  parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(RegistrationView, self).__init__(parent)
        self.setupUi(self)
        self.link = link
        self.webView.setUrl(QUrl(link))
        
