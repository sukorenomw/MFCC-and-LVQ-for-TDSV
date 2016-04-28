import sys

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

class AudioPlayer():
    def __init__(self, volumeSlider, sliderSeeker, lcdNumber, audioPlayBtn, audioPauseBtn, audioStopBtn):
        self.volumeSlider = volumeSlider
        self.seekSlider = sliderSeeker
        self.lcdNumber = lcdNumber
        self.audioPlayBtn = audioPlayBtn
        self.audioPauseBtn = audioPauseBtn
        self.audioStopBtn = audioStopBtn
        self.init_audio_player()

    def init_audio_player(self):
        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory)
        self.mediaObject = Phonon.MediaObject()
        self.metaInformationResolver = Phonon.MediaObject()

        self.mediaObject.setTickInterval(1000)
        self.mediaObject.tick.connect(self.tick)
        self.mediaObject.stateChanged.connect(self.state_change)
        self.mediaObject.finished.connect(self.mediaObject.stop)

        Phonon.createPath(self.mediaObject, self.audioOutput)

        self.volumeSlider.setAudioOutput(self.audioOutput)
        self.volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                        QtGui.QSizePolicy.Maximum)

        self.seekSlider.setMediaObject(self.mediaObject)

    def set_audio_source(self, audiofile):
        self.audioPlayBtn.clicked.connect(self.mediaObject.play)
        self.audioPauseBtn.clicked.connect(self.mediaObject.pause)
        self.audioStopBtn.clicked.connect(self.mediaObject.stop)
        self.mediaObject.setCurrentSource(Phonon.MediaSource(audiofile))

    def tick(self, time):
        displayTime = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)
        self.lcdNumber.display(displayTime.toString('mm:ss'))

    def state_change(self, newState, oldState):
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