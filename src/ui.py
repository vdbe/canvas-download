#!/usr/bin/env python3
import sys

from PyQt6.QtCore import pyqtBoundSignal
from lib import config
from lib.ui.gui import Ui_MainWindow
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
import logging
from pathlib import Path
import json

from lib.config import Config, download
from main import main

# SRC: https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Setup title and icon for window
        self.setWindowTitle("Canvas Download")
        # self.noteIcon = os.path.join( os.path.dirname(__file__), 'PyCodeNoteLogo.svg' )
        # self.setWindowIcon(QtGui.QIcon(self.noteIcon))

        self.config_file = "data/config/config.json"

        if Path(self.config_file).is_file():
            with open(self.config_file) as fp:
                cfg = json.load(fp)
                self.config = Config(**cfg)

        if config != None:
            self.ui.hostInput.setText(self.config.canvas.endpoint)
            self.ui.tokenInput.setText(self.config.canvas.bearer_token)
            self.ui.parallelDownloadsSpinBox.setValue(
                self.config.download.parallel_downloads
            )
            self.ui.downloadLockedCheckBox.setChecked(
                self.config.download.download_locked
            )
        else:
            self.ui.hostInput.setPlaceholderText("Hostname")
            self.ui.tokenInput.setPlaceholderText("token")
            self.ui.parallelDownloadsSpinBox.setValue(20)
            self.ui.runPushButton.setChecked(False)

            self.config.canvas.endpoint = ""
            self.config.canvas.bearer_token = ""
            self.config.db.directory = "data/db"
            self.config.db.name = "db.json"
            self.config.download.parallel_downloads = 10
            self.config.download.download_locked = False
            self.config.download.path = "downloads"

        self.logTextBox = QTextEditLogger(self)
        # You can format what is printed to text box
        # logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logTextBox.setLevel(level=logging.INFO)
        self.logTextBox.setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger().addHandler(self.logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)

        self.ui.gridLayout.addWidget(self.logTextBox.widget, 6, 0, 1, 1)

        # Apply page switch buttons
        self.ui.runPushButton.clicked.connect(self.runButtonClicked)

    def runButtonClicked(self):
        self.config.canvas.endpoint = self.ui.hostInput.text()
        self.config.canvas.bearer_token = self.ui.tokenInput.text()
        self.config.download.parallel_downloads = (
            self.ui.parallelDownloadsSpinBox.value()
        )
        self.config.download.download_locked = (
            self.ui.downloadLockedCheckBox.isChecked()
        )

        download = self.config.download

        tmp = Config.create(
            self.config_file,
            self.config.canvas.endpoint,
            self.config.canvas.bearer_token,
            self.config.download.download_locked,
            self.config.download.parallel_downloads,
        )
        if tmp == False:
            return

        self.config = tmp
        self.config.download = download

        main(self.config)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()
    app.exec()
