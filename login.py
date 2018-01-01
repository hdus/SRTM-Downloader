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
from qgis.PyQt.QtCore import pyqtSlot
from qgis.PyQt.QtWidgets import QDialog
from registration_view import RegistrationView
import os

    
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'login.ui'))


class Login(QDialog, FORM_CLASS):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(Login, self).__init__(parent)
        self.setupUi(self)
        self.opener = parent
    
    @pyqtSlot()
    def on_buttonBox_accepted(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.opener.username = self.lne_username.text()
        self.opener.password = self.lne_password.text()
        self.opener.success = True
        self.close()
    
    @pyqtSlot()
    def on_buttonBox_rejected(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.opener.success = False
        self.close()
    
    @pyqtSlot("QString")
    def on_lbl_registration_linkActivated(self, link):
        """
        Slot documentation goes here.
        
        @param link DESCRIPTION
        @type QString
        """
        # TODO: not implemented yet
        self.registration = RegistrationView(link)
        self.registration.exec_()

