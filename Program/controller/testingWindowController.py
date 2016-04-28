# coding=utf-8
import view.testingWindow as testingWindow
import audioPlayer
import trainingWindowController as twc

import matplotlib
matplotlib.rc('xtick', labelsize=7)
matplotlib.rc('ytick', labelsize=7)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas)

from mfcc import MFCC
from filereader import FileReader
from PyQt4 import QtCore, QtGui


class TestingWindow(QtGui.QMainWindow, testingWindow.Ui_TestWdw ):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.mfcc = MFCC()
        self.player = audioPlayer.AudioPlayer(self.volumeSlider,
                                              self.seekSlider,
                                              self.lcdNumber,
                                              self.audioPlayBtn,
                                              self.audioPauseBtn,
                                              self.audioStopBtn)
        self.init_ui()
        self.canvas = None
        self.actionTest_Data.setDisabled(True)

        self.actionExit.triggered.connect(self.close)
        self.actionTraining_Data.triggered.connect(self.open_train_wdw)
        self.actionAbout_Qt.triggered.connect(QtGui.qApp.aboutQt)
        self.actionAbout.triggered.connect(self.about)

        self.openAudioBtn.clicked.connect(self.show_open_dialog)
        self.extractSaveBtn.clicked.connect(self.extract_features)

    def init_ui(self):
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Light, QtCore.Qt.darkGray)

        self.audioPlayBtn.setDisabled(True)
        self.audioPauseBtn.setDisabled(True)
        self.audioStopBtn.setDisabled(True)
        self.extractSaveBtn.setDisabled(True)

        self.testProgress.setValue(0)
        self.lcdNumber.display("00:00")
        self.lcdNumber.setPalette(palette)

    def extract_features(self):
        self.num_frames, self.framed_signal = self.mfcc.frame_blocking(self.silenced_signal)

        fig = Figure()
        self.framedSignalPlot = fig.add_subplot(111)
        self.framedSignalPlot.plot(self.framed_signal.flatten(1))
        self.add_figure(fig, self.framedPlotLyt)

    def add_figure(self, fig, container):
        if self.canvas is not None:
            container.removeWidget(self.canvas)
        self.canvas = FigureCanvas(fig)
        container.addWidget(self.canvas)
        self.canvas.draw()

    def open_train_wdw(self):
        self.hide()
        self.mainWdw = twc.MainWindow()
        self.mainWdw.show()

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
            self.sampleValLbl.setText(
                ": " + str(len(self.audio_signal)) + " | " + str(len(self.silenced_signal)) + " (silenced)")
            self.audioFilenameLbl.setText(": " + fileName[fileName.rfind('/') + 1:len(fileName)])

            self.audioPlayBtn.setDisabled(False)

            fig = Figure()
            self.origSignalPlot = fig.add_subplot(111)
            self.origSignalPlot.plot(self.audio_signal)
            self.add_figure(fig, self.originalPlotLyt)

            self.extractSaveBtn.setDisabled(False)
            self.player.set_audio_source(self.audioFile)

    def about(self):
        QtGui.QMessageBox.information(self, "Text Dependent Speaker Verification",
                                      "Text Dependent Speaker Verification - the "
                                      "Final project software to identify and verify Speaker based on their speech.\n\n"
                                      "\xa9 Sukoreno Mukti - 1112051 \n Informatics Engineering Dept. ITHB")

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
