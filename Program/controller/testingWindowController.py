# coding=utf-8
import view.testingWindow as testingWindow
import audioPlayer
import trainingWindowController as twc
import numpy as np


import matplotlib

matplotlib.rc('xtick', labelsize=7)
matplotlib.rc('ytick', labelsize=7)

from lvq import LVQ
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas)

from mfcc import MFCC
from filereader import FileReader
from PyQt4 import QtCore, QtGui


class TestingWindow(QtGui.QMainWindow, testingWindow.Ui_TestWdw):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.mfcc = MFCC()
        self.lvq = LVQ()
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
        self.identifyBtn.clicked.connect(self.identify_speaker)

    def init_ui(self):
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Light, QtCore.Qt.darkGray)

        self.audioPlayBtn.setDisabled(True)
        self.audioPauseBtn.setDisabled(True)
        self.audioStopBtn.setDisabled(True)
        self.extractSaveBtn.setDisabled(True)

        self.lcdNumber.display("00:00")
        self.lcdNumber.setPalette(palette)

    def identify_speaker(self):
        result = self.lvq.test_data(self.features[:,1:14])
        print "vote : "+str(result)

        self.speakerVal.setText(": "+str(result[0][0][:result[0][0].find('-')]))
        self.wordVal.setText(": "+str(result[0][0][result[0][0].find('-')+1:]))

    def extract_features(self):
        # frame blocking
        self.num_frames, self.framed_signal = self.mfcc.frame_blocking(self.silenced_signal)

        fig = Figure()
        self.framedSignalPlot = fig.add_subplot(111)
        self.framedSignalPlot.plot(self.framed_signal.ravel(1))
        self.add_figure(fig, self.framedPlotLyt)

        # windowing
        self.windowed_signal = self.mfcc.hamm_window(self.framed_signal)

        fig = Figure()
        self.windowedSignalPlot = fig.add_subplot(111)
        self.windowedSignalPlot.plot(self.windowed_signal.ravel(1))
        self.add_figure(fig, self.windowedPlotLyt)

        # hitung FFT
        self.fft_signal = self.mfcc.calc_fft(self.windowed_signal)

        fig = Figure()
        self.fftSignalPlot = fig.add_subplot(111)
        self.fftSignalPlot.plot(self.fft_signal[:, :128].ravel(1))
        self.add_figure(fig, self.fftPloyLyt)

        # hitung filter bank
        self.log_energy, self.fbank = self.mfcc.fbank(self.fft_signal, self.audio_fs)

        fig = Figure()
        self.melwrapPlot = fig.add_subplot(111)
        for i in xrange(self.mfcc.num_filter):
            self.melwrapPlot.plot(self.fbank[i, :])

        self.add_figure(fig, self.melPlotLyt)

        # features
        self.features = self.mfcc.features(self.log_energy)

        fig = Figure()
        self.mfccPlot = fig.add_subplot(111)
        for i in xrange(self.features.shape[0]):
            self.mfccPlot.plot(self.features[i, :])

        self.add_figure(fig, self.mfccPlotLyt)

        # write features to table
        self.testDataTab.setCurrentIndex(len(self.testDataTab)-1)
        self.featuresTbl.setRowCount(self.features.shape[0])
        for i in xrange(self.features.shape[0]):
            for j in xrange(1,14):
                isi_feature = QtGui.QTableWidgetItem(str(self.features[i,j]))
                # print "i: "+str(i)+" j: "+str(j)+" isi: "+str(isi_feature)
                self.featuresTbl.setItem(i,j-1,isi_feature)

    def add_figure(self, fig, container):
        # if self.canvas is not None:
        #     container.removeWidget(self.canvas)
        self.clearLayout(container)
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

            self.clear_all_layout()

            fig = Figure()
            self.origSignalPlot = fig.add_subplot(111)
            self.origSignalPlot.plot(self.audio_signal)
            self.add_figure(fig, self.originalPlotLyt)

            self.extractSaveBtn.setDisabled(False)
            self.player.set_audio_source(self.audioFile)

            self.testDataTab.setCurrentIndex(0)

    def about(self):
        QtGui.QMessageBox.information(self, "Text Dependent Speaker Verification",
                                      "Text Dependent Speaker Verification - the "
                                      "Final project software to identify and verify Speaker based on their speech.\n\n"
                                      "\xa9 Sukoreno Mukti - 1112051 \n Informatics Engineering Dept. ITHB")

    def clear_all_layout(self):
        [self.clearLayout(layout) for layout in
         [self.fftPloyLyt, self.framedPlotLyt, self.melPlotLyt, self.mfccPlotLyt, self.originalPlotLyt,
          self.windowedPlotLyt]]

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
