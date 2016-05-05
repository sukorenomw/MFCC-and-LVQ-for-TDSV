# coding=utf-8
import view.trainingWindow as trainingWindow
import audioPlayer
import testingWindowController as twc
import threading

from databaseconnector import DatabaseConnector
from mfcc import MFCC
from filereader import FileReader
from PyQt4 import QtCore, QtGui

class DBThread(QtCore.QThread):
    def __init__(self, parent, audioFile, audioClassInput, features):
        QtCore.QThread.__init__(self, parent)
        self.db = DatabaseConnector()
        self.audioFile = audioFile
        self.audioClassInput = audioClassInput
        self.features = features

    def run(self):
        output_class_id = self.db.insert("output_classes",
                                         {"file_path": self.audioFile, "class": self.audioClassInput.text()})
        for i in xrange(self.features.shape[0]):
            self.db.insert_features(output_class_id, i, self.features[i, 1:14])
            self.emit(QtCore.SIGNAL("update()"))

        self.db.close()
        self.emit(QtCore.SIGNAL("finish()"))

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

    def show_open_dialog(self):
        self.audioFile = QtGui.QFileDialog.getOpenFileName(self, 'Open audio file',
                                                           '',
                                                           "Audio Files (*.wav)",
                                                           None, QtGui.QFileDialog.DontUseNativeDialog)
        if self.audioFile != "":
            self.featuresTbl.setRowCount(0)
            self.featuresTbl.setColumnCount(0)
            self.audioClassInput.setText("")

            fileName = str(self.audioFile)
            self.audio_signal, self.audio_fs = FileReader.read_audio(fileName)
            self.silenced_signal, self.audio_fs = self.mfcc.remove_silence(fileName)

            self.fsValLbl.setText(": " + str(self.audio_fs) + " Hz")
            self.sampleValLbl.setText(": " + str(len(self.audio_signal)) + " | "+str(len(self.silenced_signal))+" (silenced)")
            self.audioFilenameLbl.setText(": " + fileName[fileName.rfind('/') + 1:len(fileName)])
            self.audioClassInput.setText(FileReader.get_output_class(fileName))

            self.audioPlayBtn.setDisabled(False)

            self.extractSaveBtn.setDisabled(False)
            self.player.set_audio_source(self.audioFile)

    def finish_thread(self):
        QtGui.QMessageBox.information(None, "Success!",
                                      "Save features to database success!")

    def update_progress(self):
        self.n+=1
        self.trainProgress.setValue(self.n)

    def extract_and_save(self):
        if self.audioClassInput.text() == "":
            QtGui.QMessageBox.critical(None, "Training Data",
                                       "You must provide audio output class!",
                                       QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                                       QtGui.QMessageBox.NoButton)
            return False

        self.num_frames, self.framed_signal = self.mfcc.frame_blocking(self.silenced_signal)
        self.windowed_signal = self.mfcc.hamm_window(self.framed_signal)
        self.fft_signal = self.mfcc.calc_fft(self.windowed_signal)
        self.log_energy, self.fbank = self.mfcc.fbank(self.fft_signal, self.audio_fs)
        self.features = self.mfcc.features(self.log_energy)

        self.n = 0
        self.trainProgress.setMaximum(self.features.shape[0])
        self.trainProgress.setValue(0)
        insert_feature = DBThread(self, self.audioFile, self.audioClassInput, self.features)
        insert_feature.start()
        QtCore.QObject.connect(insert_feature, QtCore.SIGNAL("finish()"), self.finish_thread)
        QtCore.QObject.connect(insert_feature, QtCore.SIGNAL("update()"), self.update_progress)

        self.featuresTbl.setRowCount(self.features.shape[0])
        self.featuresTbl.setColumnCount(13)
        for i in xrange(self.features.shape[0]):
            for j in xrange(1, 14):
                isi_feature = QtGui.QTableWidgetItem(str(self.features[i, j]))
                # print "i: "+str(i)+" j: "+str(j)+" isi: "+str(isi_feature)
                self.featuresTbl.setItem(i, j - 1, isi_feature)


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

