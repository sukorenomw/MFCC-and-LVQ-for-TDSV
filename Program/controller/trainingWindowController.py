import sys
import view.trainingWindow as trainingWindow


from PyQt4 import QtCore, QtGui
try:
    from PyQt4.phonon import Phonon
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "Music Player",
            "Your Qt installation does not have Phonon support.",
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
            QtGui.QMessageBox.NoButton)
    sys.exit(1)


class MainWindow(QtGui.QMainWindow, trainingWindow.Ui_MainWdw):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.initAudioPlayer()
        self.initUI()
        self.actionExit.triggered.connect(self.close)
        self.openAudioBtn.clicked.connect(self.showOpenDialog)

    def showOpenDialog(self):
        self.audioFile = QtGui.QFileDialog.getOpenFileName(self,'Open audio file',
                         '',
                         "Audio Files (*.mp3 *.wav *.ogg)",
                         None, QtGui.QFileDialog.DontUseNativeDialog)
        fileName = str(self.audioFile)
        self.audioFilenameLbl.setText(fileName[fileName.rfind('/')+1:len(fileName)])
        self.audioPlayBtn.setDisabled(False)
        self.audioPlayBtn.clicked.connect(self.mediaObject.play)
        self.audioPauseBtn.clicked.connect(self.mediaObject.pause)
        self.audioStopBtn.clicked.connect(self.mediaObject.stop)

        self.mediaObject.setCurrentSource(Phonon.MediaSource(self.audioFile))

    def initAudioPlayer(self):
        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.mediaObject = Phonon.MediaObject(self)
        self.metaInformationResolver = Phonon.MediaObject(self)

        self.mediaObject.setTickInterval(1000)
        self.mediaObject.tick.connect(self.tick)
        self.mediaObject.stateChanged.connect(self.stateChanged)
        self.mediaObject.finished.connect(self.mediaObject.stop)

        Phonon.createPath(self.mediaObject, self.audioOutput)

        self.volumeSlider.setAudioOutput(self.audioOutput)
        self.volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                        QtGui.QSizePolicy.Maximum)

        self.seekSlider.setMediaObject(self.mediaObject)

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

    def tick(self, time):
        displayTime = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)
        self.lcdNumber.display(displayTime.toString('mm:ss'))

    def stateChanged(self, newState, oldState):
        if newState == Phonon.ErrorState:
            if self.mediaObject.errorType() == Phonon.FatalError:
                QtGui.QMessageBox.warning(self, "Fatal Error",
                                          self.mediaObject.errorString())
            else:
                QtGui.QMessageBox.warning(self, "Error",
                                          self.mediaObject.errorString())

        elif newState == Phonon.PlayingState:
            self.audioPlayBtn.setEnabled(False)
            self.audioPauseBtn.setEnabled(True)
            self.audioStopBtn.setEnabled(True)

        elif newState == Phonon.StoppedState:
            self.audioStopBtn.setEnabled(False)
            self.audioPlayBtn.setEnabled(True)
            self.audioPauseBtn.setEnabled(False)
            self.lcdNumber.display("00:00")

        elif newState == Phonon.PausedState:
            self.audioPauseBtn.setEnabled(False)
            self.audioStopBtn.setEnabled(True)
            self.audioPlayBtn.setEnabled(True)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
