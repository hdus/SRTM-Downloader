#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
QNetworkAccessManager in PyQt

In this example, we show how to authenticate
to a web page.

Author: Jan Bodnar
Website: zetcode.com
Last edited: September 2017
'''
import sip
sip.setapi('QVariant',2)
from PyQt4 import QtCore, QtNetwork
import sys, json
from download import Download
      
#      
#class Download:
#
#    def __init__(self,  url=None,  filename=None):    
#      self.url = url
#      self.filename = filename
#      
#      self.doRequest()
#        
#    def doRequest(self):   
#        print ("Start")
#        url = "https://e4ftl01.cr.usgs.gov/MODV6_Dal_D/SRTM/SRTMGL1.003/2000.02.11/N45E006.SRTMGL1.hgt.zip"
#        self.filename = "/home/hdus/temp/image.zip"
#        req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
#        self.nam = QtNetwork.QNetworkAccessManager()
#        self.nam.authenticationRequired.connect(self.authenticate)
#        self.nam.finished.connect(self.replyFinished)
#        reply = self.nam.get(req)  
#        
#        
#    def authenticate(self, reply, auth):
#        auth.setUser("hdus")
#        auth.setPassword("W3ldgmn!")         
#             
#
#    def replyFinished(self, reply): 
#        
#        possibleRedirectUrl = reply.attribute(QtNetwork.QNetworkRequest.RedirectionTargetAttribute);
#
#    # We'll deduct if the redirection is valid in the redirectUrl function
#        _urlRedirectedTo = possibleRedirectUrl
#
#    # If the URL is not empty, we're being redirected. 
#        if _urlRedirectedTo != None:
#            print ("Redirect")    
#    # We'll do another request to the redirection url. */
#            self.nam.get(QtNetwork.QNetworkRequest(_urlRedirectedTo))
#            
#        else:
#            print ("Finished")
#            result = reply.readAll()
#            f = open(self.filename, 'wb')
#            f.write(result)
#            f.close()      
#    
#        # Clean up. */
#            reply.deleteLater()
#            QtCore.QCoreApplication.quit()

   
app = QtCore.QCoreApplication([])
ex = Download()
sys.exit(app.exec_())
QtCore.QCoreApplication.quit()
