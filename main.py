"""
This is a video converter
"""
import sys

from PySide2.QtWidgets import QApplication, QWidget, QFileDialog
from PySide2.QtGui import QPixmap, QStandardItemModel, QStandardItem
from PySide2.QtCore import QProcess, Qt

from Form import Ui_Form

DEBUG = False


class VidConvertWindow(QWidget, Ui_Form):
    """this is the main class for video converter"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.available_formats = ["x", "y", "z"]
        self.selected_files = []
        self.process = QProcess()
        self.progress_reader = QProcess()

        self.file_picker = QFileDialog(self)

        self.file_list_model = QStandardItemModel(self.listViewFiles)
        self.listViewFiles.setModel(self.file_list_model)
        self.type_list_model = QStandardItemModel(self.listViewTypes)
        self.listViewTypes.setModel(self.type_list_model)

        self.file_list_model.itemChanged.connect(self.update_selected_files)
        self.btnStop.clicked.connect(self.stop_convertion)
        self.btnAdd.clicked.connect(self.add_files)
        self.btnConvert.clicked.connect(self.start_convertion)
        self.post_init()

    def post_init(self):
        """runs after init"""
        self.btnConvert.setIcon(QPixmap('./icons/start.ico'))
        self.btnAdd.setIcon(QPixmap('./icons/file.ico'))
        self.btnStop.setIcon(QPixmap('./icons/stop.ico'))

        self.setWindowTitle("Simple Video Converter")
        self.setGeometry(100, 100, 640, 480)

        for filetype in self.available_formats:
            self.add_item2model(filetype, self.type_list_model)

    def add_item2model(self, filename: str, model: QStandardItemModel):
        """sample listview code"""
        list_item = QStandardItem(filename)
        list_item.setCheckable(True)
        list_item.setEditable(False)
        list_item.setSelectable(False)
        model.appendRow(list_item)

    def update_selected_files(self, item):
        """selects the checked items"""
        if item.checkState() == Qt.CheckState.Checked and item.text(
        ) not in self.selected_files:
            self.selected_files.append(item.text())
        else:
            self.selected_files.remove(item.text())
        if DEBUG:
            print(self.selected_files)

    def add_files(self):
        """opens file picker for choosing files"""
        self.file_picker.setFileMode(QFileDialog.ExistingFiles)
        self.file_picker.setNameFilter("Videos (*.mp4 *.mkv *.mov)")
        self.file_picker.setViewMode(QFileDialog.Detail)
        if self.file_picker.exec_():
            files_selected = self.file_picker.selectedFiles()
            for file in files_selected:
                self.add_item2model(file, self.file_list_model)
                if DEBUG:
                    print(file)

    def start_convertion(self):
        """implement conversion task"""
        print("Not implemented")

    def stop_convertion(self):
        """stop running coversion task"""
        print("Not implemented")


if __name__ == "__main__":
    APP = QApplication(sys.argv)
    WINDOW = VidConvertWindow()
    WINDOW.show()
    sys.exit(APP.exec_())
