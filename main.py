import sys
import os
import re

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

import yt_dlp

if getattr(sys, 'frozen', False):
    BUNDLE_DIR = sys._MEIPASS
else:
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))

class DownloadWorker(QThread):
    message_signal = pyqtSignal(str)
    result_signal = pyqtSignal(bool, str)
    
    def __init__(self, url, ydl_opts):
        super().__init__()
        self.url = url
        self.ydl_opts = ydl_opts
        
    def _hook(self, d):
        if d['status'] == 'downloading':
            self.message_signal.emit(f"Descargando... {d.get('_percent_str', 'N/A')} de {d.get('_total_bytes_str', 'N/A')}")
        elif d['status'] == 'finished':
            self.message_signal.emit("Finalizando...")

    def run(self):
        try:
            self.ydl_opts['progress_hooks'] = [self._hook]
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([self.url])
            self.result_signal.emit(True, "¡Descarga completada!")
        except Exception as e:
            self.result_signal.emit(False, f"Error: {e}")

class YouTubeDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.download_thread = None
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(100, 100, 600, 300)
        self.setStyleSheet("background-color: #2e2e2e; color: #f0f0f0;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        url_layout = QHBoxLayout()
        url_label = QLabel("URL de YouTube:")
        url_label.setFont(QFont("Arial", 12))
        url_label.setStyleSheet("color: #cccccc;")
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Pega aquí el URL del video...")
        self.url_entry.setFont(QFont("Arial", 10))
        self.url_entry.setStyleSheet("background-color: #4a4a4a; border: 1px solid #666; padding: 5px; color: #f0f0f0;")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_entry)
        main_layout.addLayout(url_layout)

        selection_layout = QHBoxLayout()
        type_label = QLabel("Tipo de descarga:")
        type_label.setFont(QFont("Arial", 12))
        type_label.setStyleSheet("color: #cccccc;")
        self.type_combobox = self._create_combobox()
        self.type_combobox.addItems(["Video", "Audio"])
        selection_layout.addWidget(type_label)
        selection_layout.addWidget(self.type_combobox)

        quality_label = QLabel("Calidad:")
        quality_label.setFont(QFont("Arial", 12))
        quality_label.setStyleSheet("color: #cccccc;")
        self.quality_combobox = self._create_combobox()
        selection_layout.addWidget(quality_label)
        selection_layout.addWidget(self.quality_combobox)
        
        main_layout.addLayout(selection_layout)

        self.download_button = QPushButton("Descargar")
        self.download_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.download_button.setStyleSheet(
            """
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005f99;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #aaa;
            }
            """
        )
        self.download_button.clicked.connect(self.start_download)
        main_layout.addWidget(self.download_button)

        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #cccccc;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFixedHeight(20)
        main_layout.addWidget(self.status_label)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        author_label = QLabel("by: Ars-byte")
        author_label.setFont(QFont("Arial", 9))
        author_label.setStyleSheet("color: #888888;")
        footer_layout.addWidget(author_label)
        main_layout.addLayout(footer_layout)

        self.url_entry.returnPressed.connect(self.start_download)
        self.type_combobox.currentTextChanged.connect(self.update_quality_options)
        self.update_quality_options(self.type_combobox.currentText())

    def closeEvent(self, event):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.quit()
            self.download_thread.wait(5000)
            if self.download_thread.isRunning():
                self.download_thread.terminate()
                self.download_thread.wait(5000)
        event.accept()

    def _create_combobox(self):
        combo = QComboBox()
        combo.setFont(QFont("Arial", 10))
        combo.setStyleSheet(
            """
            QComboBox {
                background-color: #4a4a4a;
                border: 1px solid #666;
                padding: 5px;
                color: #f0f0f0;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #4a4a4a;
                color: #f0f0f0;
                selection-background-color: #007acc;
            }
            """
        )
        return combo

    def update_quality_options(self, download_type):
        self.quality_combobox.clear()
        if download_type == "Video":
            self.quality_combobox.addItems(["Mejor (video+audio)", "1080p", "720p", "480p", "360p"])
        elif download_type == "Audio":
            self.quality_combobox.addItems(["MP3"])

    def start_download(self):
        if self.download_thread and self.download_thread.isRunning():
            QMessageBox.warning(self, "Espera", "Una descarga ya está en curso. Por favor, espera a que termine.")
            return

        url = self.url_entry.text().strip()
        if not self.is_valid_youtube_url(url):
            QMessageBox.warning(self, "Error", "Por favor, introduce una URL de YouTube válida.")
            return

        download_type = self.type_combobox.currentText()
        quality = self.quality_combobox.currentText()
        
        ydl_opts = self.get_ydl_options(download_type, quality)
        output_path = os.path.join(BUNDLE_DIR, '%(title)s.%(ext)s')
        ydl_opts['outtmpl'] = output_path
        
        self.download_button.setDisabled(True)
        self.status_label.setText("Obteniendo información...")

        self.worker = DownloadWorker(url, ydl_opts)
        self.download_thread = QThread()
        self.worker.moveToThread(self.download_thread)
        
        self.download_thread.started.connect(self.worker.run)
        self.worker.result_signal.connect(self.on_download_finished)
        self.worker.message_signal.connect(self.update_status)

        self.download_thread.start()

    def get_ydl_options(self, download_type, quality):
        base_opts = {}
        if download_type == "Video":
            format_map = {
                "Mejor (video+audio)": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "1080p": "bestvideo[height=1080][ext=mp4]+bestaudio[ext=m4a]/best[height=1080]",
                "720p": "bestvideo[height=720][ext=mp4]+bestaudio[ext=m4a]/best[height=720]",
                "480p": "bestvideo[height=480][ext=mp4]+bestaudio[ext=m4a]/best[height=480]",
                "360p": "bestvideo[height=360][ext=mp4]+bestaudio[ext=m4a]/best[height=360]",
            }
            base_opts['format'] = format_map.get(quality, "best")
        elif download_type == "Audio":
            base_opts['format'] = "bestaudio/best"
            base_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        return base_opts

    def is_valid_youtube_url(self, url):
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?'
            r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        return youtube_regex.match(url)

    def update_status(self, message):
        self.status_label.setText(message)

    def on_download_finished(self, success, message):
        self.download_button.setDisabled(False)
        self.status_label.setText("")
        if success:
            QMessageBox.information(self, "Éxito", message)
        else:
            QMessageBox.critical(self, "Error", message)

        
        self.download_thread.quit()
        self.download_thread.wait()
        
        self.worker.deleteLater()
        self.download_thread.deleteLater()
        
        self.worker = None
        self.download_thread = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloaderApp()
    window.show()
    sys.exit(app.exec())

