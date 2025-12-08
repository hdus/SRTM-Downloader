### `downloader.py`
# Core download logic used by providers and UI
import requests
#from requests.auth import HTTPBasicAuth
from qgis.PyQt.QtCore import QSettings,  Qt
from qgis.PyQt.QtWidgets import QApplication,  QMessageBox
                                                        


class Downloader:
    def __init__(self,  opener):
        self.settings = QSettings()          
        self._cancel = False
        self.opener = opener
            
    from contextlib import contextmanager
    
    @contextmanager
    def wait_cursor(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            yield
        finally:
            QApplication.restoreOverrideCursor()            
            

    def cancel(self):
        self._cancel = True
        
    # OpenTopography API
    def download_opentopo_globaldem(self, product, south, north, west, east, out_path):
        with self.wait_cursor():
            api_key = self.opener.lne_api_key.text()

            url = (
                'https://portal.opentopography.org/API/globaldem?'
                f'demtype={product}&south={south}&north={north}&west={west}&east={east}&outputFormat=GTiff'
            )
            
            if api_key:
                url += f'&API_Key={api_key}'
                self.download_stream(url,
                    out_path,
                    progress_callback=lambda p: int(p)
                )
        
        return out_path

    def download_stream(self, url, out_path, progress_callback=None, cancel_callback=None):
        r = requests.get(url, stream=True)
        
        if r.status_code != 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(r.text)
            error = root.text.split(':')
            
            QMessageBox.critical(
                None,
                "Error",
                error[1],
                (
                    QMessageBox.StandardButton.Ok),
            )
        else:
            downloaded = 0

            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if cancel_callback and cancel_callback():
                        raise Exception("Download canceled")

                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback:
                            progress_callback(downloaded)
