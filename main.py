# Python 3
# Create a QT program that displays a "File Url" text field and a "Download" button.
# There should be a "paste" button to the left of the file url. It will paste the contents of the clipboard on the text field
# Below the "Download" button, add a progress bar that will show the download progress for the file
# Right next to "Download" button, add a "Cancel" button. When the user clicks the "Cancel" button, the download should be cancelled


import os
import re
import sys
import time
import urllib.request

from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QProgressBar, \
    QPushButton, \
    QVBoxLayout, QWidget

class DownloadThread(QThread):
    onprogress = pyqtSignal(int)
    onread = pyqtSignal(int)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.filename = url.split('/')[-1]
        self.total_size = 0

    def run(self):
        urllib.request.urlretrieve(self.url, self.filename, self.report)

    def report(self, blocknum, blocksize, totalsize):
        readsofar = blocknum * blocksize
        self.total_size = totalsize
        if totalsize > 0:
            percent = min(readsofar * 100 / totalsize, 100)
            self.onprogress.emit(int(percent))
            self.onread.emit(readsofar)
            # print a ascii progress bar
            print('\r', end='')
            print('#' * int(percent / 2), end='')
            print(' ' * (50 - int(percent / 2)), end='')
            print('[%d%%]' % percent, end='')
            sys.stdout.flush()
            
    def terminate(self):
        sys.stdout.write('\n')
        print('Download cancelled')
        super().terminate()

class Downloader(QWidget):
    def __init__(self):
        super().__init__()
        self.download_thread = None
        self.download_started_time = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Downloader')
        self.setWindowIcon(QIcon('download.png'))
        self.setGeometry(300, 300, 800, 100)

        self.url_label = QLabel('File Url')
        self.url_text = QLineEdit()
        self.url_text.setPlaceholderText('Enter file url')
        self.url_text.textChanged.connect(self.validate_url)
        
        self.paste_button = QPushButton('Paste')
        self.paste_button.clicked.connect(self.paste_url)
        
        self.download_button = QPushButton('Download')
        self.download_button.clicked.connect(self.download_file)
        self.download_button.setEnabled(False)
        
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setEnabled(False)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        
        self.progress_text = QLabel('Progress')
        self.progress_text_value = QLabel('')
        
        self.progress_text_layout = QHBoxLayout()
        self.progress_text_layout.addWidget(self.progress_text, 1, Qt.AlignLeft)
        self.progress_text_layout.addWidget(self.progress_text_value)

        self.url_layout = QHBoxLayout()
        self.url_layout.addWidget(self.url_label)
        self.url_layout.addWidget(self.url_text)
        self.url_layout.addWidget(self.paste_button)

        self.download_layout = QHBoxLayout()
        self.download_layout.addWidget(self.download_button)
        self.download_layout.addWidget(self.cancel_button)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.url_layout)
        self.main_layout.addLayout(self.download_layout)
        self.main_layout.addLayout(self.progress_text_layout)
        self.main_layout.addWidget(self.progress_bar)

        self.setLayout(self.main_layout)

    def paste_url(self):
        clipboard = QApplication.clipboard()
        self.url_text.setText(clipboard.text())

    def download_file(self):
        if self.download_thread is not None:
            # display a message box to the user that the download is already in progress
            QMessageBox.about(self, 'Download in progress', 'The download is already in progress')
            return
        
        self.download_thread = DownloadThread(self.url_text.text())
        self.download_thread.onprogress.connect(self.progress_bar.setValue)
        self.download_thread.onread.connect(self.update_progress_text)
        self.download_thread.start()
        self.download_button.setEnabled(False)
        self.download_started_time = time.time()
        
        self.cancel_button.setEnabled(True)
        
    def update_progress_text(self, readsofar):
        if self.download_thread is None:
            return
        total_size = self.download_thread.total_size
        total_size_mb = total_size / 1024 / 1024
        readsofar_mb = readsofar / 1024 / 1024
        speed = readsofar / (time.time() - self.download_started_time)
        self.progress_text_value.setText(f'{readsofar_mb:.2f}/{total_size_mb:.2f} mb at {speed / 1024 / 1024:.2f} mb/s')
        
    def validate_url(self):
        # validates the provided url using regex and disables the download button if the url is invalid
        url_regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if url_regex.match(self.url_text.text()):
            self.download_button.setEnabled(True)
        else:
            self.download_button.setEnabled(False)

    def cancel_download(self):
        filename = self.download_thread.filename
        self.download_thread.terminate()
        self.progress_bar.setValue(0)
        # remove the file if it was partially downloaded
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except PermissionError:
                # schedule the file for deletion in 5 seconds
                os.system(f'del /f /q /s /t 5 {filename}')
        self.download_thread = None
        self.cancel_button.setEnabled(False)
        self.download_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    downloader = Downloader()
    downloader.show()
    sys.exit(app.exec_())
