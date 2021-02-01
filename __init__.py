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

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SrtmDownloader class from file SrtmDownloader.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .srtm_downloader import SrtmDownloader
    return SrtmDownloader(iface)
