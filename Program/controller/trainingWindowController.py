# coding=utf-8
import view.trainingWindow as trainingWindow
import audioPlayer
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
        self.initUI()
        self.actionExit.triggered.connect(self.close)
        self.actionAbout_Qt.triggered.connect(QtGui.qApp.aboutQt)
        self.actionAbout.triggered.connect(self.about)
        self.openAudioBtn.clicked.connect(self.showOpenDialog)

    def about(self):
        QtGui.QMessageBox.information(self, "Text Dependent Speaker Verification",
                                      "Text Dependent Speaker Verification - the "
                                      "Final project software to identify and verify Speaker based on their speech.\n\n"
                                      "\xa9 Sukoreno Mukti - 1112051 \n Informatics Engineering Dept. ITHB")

    def showOpenDialog(self):
        self.audioFile = QtGui.QFileDialog.getOpenFileName(self, 'Open audio file',
                                                           '',
                                                           "Audio Files (*.mp3 *.wav *.ogg)",
                                                           None, QtGui.QFileDialog.DontUseNativeDialog)
        fileName = str(self.audioFile)
        self.audioFilenameLbl.setText(fileName[fileName.rfind('/') + 1:len(fileName)])
        self.audioPlayBtn.setDisabled(False)
        self.audioPlayBtn.clicked.connect(self.player.mediaObject.play)
        self.audioPauseBtn.clicked.connect(self.player.mediaObject.pause)
        self.audioStopBtn.clicked.connect(self.player.mediaObject.stop)
        self.extractSaveBtn.setDisabled(False)
        self.player.setAudioSource(self.audioFile)

    def initUI(self):
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
