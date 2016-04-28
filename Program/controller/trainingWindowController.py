# coding=utf-8
import view.trainingWindow as trainingWindow
import audioPlayer
import testingWindowController as twc

from mfcc import MFCC
from filereader import FileReader
from PyQt4 import QtCore, QtGui


class MainWindow(QtGui.QMainWindow, trainingWindow.Ui_MainWdw):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.player = audioPlayer.AudioPlayer(self.volumeSlider,
                                              self.seekSlider,
                                              self.lcdNumber,
                                              self.audioPlayBtn,
                                              self.audioPauseBtn,
                                              self.audioStopBtn)
        self.mfcc = MFCC()
        self.init_ui()
        self.actionExit.triggered.connect(self.close)
        self.actionTraining_Data.setDisabled(True)
        self.actionTest_Data.triggered.connect(self.open_test_wdw)

        self.actionAbout_Qt.triggered.connect(QtGui.qApp.aboutQt)
        self.actionAbout.triggered.connect(self.about)

        self.openAudioBtn.clicked.connect(self.show_open_dialog)
        self.extractSaveBtn.clicked.connect(self.extract_and_save)

    def open_test_wdw(self):
        self.hide()
        self.testWdw = twc.TestingWindow()
        self.testWdw.show()

    def about(self):
        QtGui.QMessageBox.information(self, "Text Dependent Speaker Verification",
                                      "Text Dependent Speaker Verification - the "
                                      "Final project software to identify and verify Speaker based on their speech.\n\n"
                                      "\xa9 Sukoreno Mukti - 1112051 \n Informatics Engineering Dept. ITHB")

    def show_open_dialog(self):
        self.audioFile = QtGui.QFileDialog.getOpenFileName(self, 'Open audio file',
                                                           '',
                                                           "Audio Files (*.wav)",
                                                           None, QtGui.QFileDialog.DontUseNativeDialog)
        if self.audioFile != "":
            fileName = str(self.audioFile)
            self.audio_signal, self.audio_fs = FileReader.read_audio(fileName)
            self.silenced_signal, self.audio_fs = self.mfcc.remove_silence(fileName)

            self.fsValLbl.setText(": " + str(self.audio_fs) + " Hz")
            self.sampleValLbl.setText(": " + str(len(self.audio_signal)) + " | "+str(len(self.silenced_signal))+" (silenced)")
            self.audioFilenameLbl.setText(": " + fileName[fileName.rfind('/') + 1:len(fileName)])

            self.audioPlayBtn.setDisabled(False)

            self.extractSaveBtn.setDisabled(False)
            self.player.set_audio_source(self.audioFile)

    def extract_and_save(self):
        self.num_frames, self.framed_signal = self.mfcc.frame_blocking(self.silenced_signal)
        self.windowed_signal = self.mfcc.hamm_window(self.mfcc.frame_size, self.framed_signal, self.num_frames)

    def init_ui(self):
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Light, QtCore.Qt.darkGray)

        self.audioPlayBtn.setDisabled(True)
        self.audioPauseBtn.setDisabled(True)
        self.audioStopBtn.setDisabled(True)
        self.extractSaveBtn.setDisabled(True)

        self.trainProgress.setValue(0)
        self.lcdNumber.display("00:00")
        self.lcdNumber.setPalette(palette)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
