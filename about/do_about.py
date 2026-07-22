# -*- coding: utf-8 -*-
"""
/***************************************************************************
                                 A QGIS plugin
Class for managing Plugin Abouts                              -------------------
        begin                : 2014-01-15
        copyright            : (C) 2014 by Dr. Horst Duester
        email                : horst.duester@kappasys.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify *
 *   it under the terms of the GNU General Public License as published by *
 *   the Free Software Foundation; either version 2 of the License, or    *
 *   (at your option) any later version.                                  *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from .metadata import Metadata

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_about.ui'))


class About(QDialog, FORM_CLASS):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.plugin_dir = os.path.dirname(__file__)
        self.metadata = Metadata()
        self.setWindowTitle(self.tr(u"About {0} {1}".format(self.metadata.name(), self.metadata.version())))
        self.lblVersion.setText(self.tr(u"Version: {0}".format(self.metadata.version())))
        self.tabWidget.setTabText(0, self.metadata.name())
        self.tabWidget.setTabText(1, self.tr("Author"))
        self.tabWidget.setTabText(2, self.tr("Contact"))
        self.tabWidget.setTabText(3, self.tr("Change Log"))

        # setup texts
        about_string = self.metadata.description()

        contrib_string = self.tr(u"<p><center><b>Author(s):</b></center></p>")
        contrib_string += self.tr(u"<p>{0}<br>".format(self.metadata.author()))

        license_string = self.tr(u"")
        license_string += self.tr(u"")

        license_string += "\n"
        license_string += self.tr(u"Contact:\n")
        license_string += self.metadata.author() + "\n"
        license_string += self.metadata.email() + "\n\n"
        license_string += self.tr(u"Plugin Resources:\n")
        license_string += self.metadata.homepage() + "\n"
        license_string += self.metadata.tracker() + "\n"
        license_string += self.metadata.repository() + "\n"

        # write texts
        self.memAbout.setText(about_string)
        self.memContrib.setText(contrib_string)
        self.memAcknowl.setText(license_string)
        self.memChangeLog.setText(self.metadata.changelog())
