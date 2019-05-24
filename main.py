"""
This is a video converter
"""
import sys
from pathlib import Path
import re

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

        # class variable declarations
        self.available_formats = []
        self.selected_files = []
        self.process_argument = ""
        self.current_file_duration = None
        self.duration_re = re.compile(r'Duration: ([0-9:.]+)')
        self.time_re = re.compile(r'time=\s*([0-9:.]+) ')
        self.process = QProcess()
        self.kill_process = QProcess()
        self.file_picker = QFileDialog(self)
        self.output_dir = ""
        self.current_file_idx = 0
        self.conversion_started = False

        self.output_folder_picker = QFileDialog(self)
        self.output_folder_picker.setFileMode(QFileDialog.DirectoryOnly)

        # listview & models
        self.file_list_model = QStandardItemModel(self.listViewFiles)
        self.listViewFiles.setModel(self.file_list_model)
        self.type_list_model = QStandardItemModel(self.listViewTypes)
        self.listViewTypes.setModel(self.type_list_model)

        # signals & slots
        self.process.readyReadStandardError.connect(self.read_output)
        self.file_list_model.itemChanged.connect(self.update_selected_files)
        self.btnStop.clicked.connect(self.stop_convertion)
        self.btnAdd.clicked.connect(self.add_files)
        self.btnConvert.clicked.connect(self.start_convertion)

        # call post_init
        self.post_init()

    def post_init(self):
        """runs after init"""
        self.btnConvert.setIcon(QPixmap('./icons/start.ico'))
        self.btnAdd.setIcon(QPixmap('./icons/file.ico'))
        self.btnStop.setIcon(QPixmap('./icons/stop.ico'))

        self.progressBarCurrent.setValue(0)
        self.progressBarTotal.setValue(0)

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

    def get_file_name(self, idx: int, suffix: str):
        """returns the filename from path (static)"""
        return Path(self.selected_files[idx]).with_suffix(suffix).name

    def start_convertion(self):
        """implement conversion task"""
        # check if output dir is already defined else get outdir
        if not self.conversion_started:
            self.get_output_dir()
            self.progressBarTotal.setMaximum(len(self.selected_files))
            self.btnConvert.setEnabled(False)
            self.conversion_started = True

        # setting up arguments
        current_file_name = self.selected_files[self.current_file_idx]
        current_outfile_name = Path(self.output_dir).joinpath(
            self.get_file_name(self.current_file_idx, ".avi"))
        self.process_argument = " -i {} {}".format(current_file_name,
                                                   current_outfile_name)

        # create a process everytime it's called
        # NOTE: this is a local instance of the process so it changes after every call
        process = QProcess()
        process.readyReadStandardError.connect(
            lambda: self.parse_output(process))
        process.finished.connect(self.recursion_handler)
        process.started.connect(lambda : self.ref_process(process))
        process.start("ffmpeg", self.process_argument.split())

    def ref_process(self, process):
        self.process = process
    
    def get_output_dir(self):
        """ get the output directory """
        if self.output_folder_picker.exec_():
            self.output_dir = self.output_folder_picker.selectedFiles()[0]

    def recursion_handler(self):
        """controls the multiple process iterations"""
        # prepare next file for xonversion
        self.current_file_idx += 1
        self.current_file_duration = None
        self.progressBarCurrent.setValue(0)
        self.progressBarTotal.setValue(self.current_file_idx)

        # check if the number of files converted exceed total number
        if self.current_file_idx == len(self.selected_files):
            print("conversion complete!")
            self.btnConvert.setEnabled(True)
            self.conversion_started = False
            return

        # if everything okay, start conversion again
        self.start_convertion()

    @staticmethod
    def parse_time(time):
        """parsing time format to second"""
        _t = list(map(float, time.split(":")))
        return _t[0] * 3600 + _t[1] * 60 + _t[2]

    def parse_output(self, process):
        """ parses current progress """
        # update progress
        data = process.readAllStandardError().data().decode("utf-8")
        if self.current_file_duration is None:
            match = self.duration_re.search(data)
            if match:
                self.current_file_duration = self.parse_time(match.group(1))
        else:
            match = self.time_re.search(data)
            if match:
                current_progress = self.parse_time(match.group(1))
                self.progressBarCurrent.setValue(
                    min((current_progress / self.current_file_duration) * 100,
                        100))

    # deprecated
    def read_output(self):
        """process the output of ffmpeg"""
        data = self.process.readAllStandardError().data().decode("utf-8")
        if self.current_file_duration is None:
            match = self.duration_re.search(data)
            if match:
                self.current_file_duration = self.parse_time(match.group(1))
        else:
            match = self.time_re.search(data)
            if match:
                current_progress = self.parse_time(match.group(1))
                self.progressBarCurrent.setValue(
                    min((current_progress / self.current_file_duration) * 100,
                        100))

    def stop_convertion(self):
        """stop running coversion task"""
        # print("Not implemented")
        print("testing stop")
        # pid = self.process.processId()
        if sys.platform == 'linux':
            self.kill_process.start("pkill", "ffmpeg".split())
        self.process.terminate()


if __name__ == "__main__":
    APP = QApplication(sys.argv)
    WINDOW = VidConvertWindow()
    WINDOW.show()
    sys.exit(APP.exec_())
