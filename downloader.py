### `downloader.py`
# Core download logic used by providers and UI
import os
import requests
from requests.auth import HTTPBasicAuth
from qgis.PyQt.QtCore import QSettings,  Qt
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtNetwork import (QNetworkRequest, 
                                                            QNetworkReply,  
                                                            QNetworkAccessManager)
from qgis.core import (QgsProject,  
                                       QgsRasterLayer, 
                                       QgsNetworkAccessManager)                                                            


class Downloader:
    def __init__(self):
        self.settings = QSettings('SRTMDownloader','Settings')          
            
    from contextlib import contextmanager
    
    @contextmanager
    def wait_cursor(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            yield
        finally:
            QApplication.restoreOverrideCursor()            
            
    # OpenTopography API
    def download_opentopo_globaldem(self, opener,  product, south, north, west, east, out_path):
        with self.wait_cursor():
            api_key = self.settings.value('opentopo/api_key', '')
            api_key = 'e1ed2fffbfdcc8667c47344be27b854c'
            # product examples: SRTMGL3, COPDEM_GLO30
            url = (
                'https://portal.opentopography.org/API/globaldem?'
                f'demtype={product}&south={south}&north={north}&west={west}&east={east}&outputFormat=GTiff'
            )
            if api_key:
                url += f'&API_Key={api_key}'
                self.download_stream(
                    opener, 
                    url,
                    out_path,
                    progress_callback=lambda p: self.overall_progressbar.setValue(int(p))
                )
#                r   = requests.get(url, stream=True)
#                
#
#            if r.status_code == 200:
#                self._write_stream(r, out_path)
#                return out_path
#            else:
#                raise RuntimeError(f'Error {r.status_code} from OpenTopography: {url}')

    def download_stream(self, opener,  url, out_path, progress_callback=None, cancel_callback=None):
        r = requests.get(url, stream=True)
        total = int(r.headers.get('Content-Length', 0))
        downloaded = 0

        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if cancel_callback and cancel_callback():
                    raise Exception("Download canceled")

                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    opener.lbl_downloaded_bytes.setText(str(downloaded))
                    
                    if progress_callback and total:
                        print (downloaded * 100 / total)
                        progress_callback(downloaded * 100 / total)

        return out_path

    def _write_stream(self, r, out_path):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
                    
    def reply_finished(self, reply):    
        if not self.request_is_aborted:
            if reply != None:
                possibleRedirectUrl = reply.attribute(QNetworkRequest.RedirectionTargetAttribute)
                
            # If the URL is not empty, we're being redirected. 
                if possibleRedirectUrl != None:
                    request = QNetworkRequest(possibleRedirectUrl)
                    result = self.nam.get(request)  
                    self.parent.add_download_progress(reply)
                    result.downloadProgress.connect(lambda done,  all,  reply=result: self.progress(done,  all,  reply))              
                else:             
                    if reply.error() != None and reply.error() != QNetworkReply.NoError:
                        self.parent.is_error = reply.errorString()
                        self.parent.set_progress()
                        reply.abort()
                        if reply in self.reply_list:
                            self.reply_list.remove(reply)
                        reply.deleteLater()
                        
                    elif reply.error() ==  QNetworkReply.NoError:
                        result = reply.readAll()
                        f = open(self.filename, 'wb')
                        f.write(result)
                        f.close()      
                        out_image = self.unzip(self.filename)
                        (dir, file) = os.path.split(out_image)
                        
                        try:
                            if not self.layer_exists(file):
                                raster_layer = QgsRasterLayer(out_image, file)
                                QgsProject.instance().addMapLayer(raster_layer)
                                layer = self.root.findLayer(raster_layer.id())
                                clone = layer.clone()
                                self.group.insertChildNode(0,  clone)
                                self.root.removeChildNode(layer)
                                clone.legend().setExpanded(False)                            
                        except:
                            pass
                            
                        self.parent.set_progress()  
                            
                    # Clean up. */
                        reply.deleteLater()                    
