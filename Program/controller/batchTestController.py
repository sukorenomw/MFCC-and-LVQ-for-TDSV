import view.batchTestWindow as batch_wdw

from lvq import LVQ
from mfcc import MFCC
from filereader import FileReader
from PyQt4 import QtCore, QtGui
from os import listdir
from os.path import isfile, join

class TestingThread(QtCore.QThread):
    def __init__(self, parent, audio_files):
        QtCore.QThread.__init__(self, parent)
        self.audio_files = audio_files
        self.mfcc = MFCC()
        self.par = parent

    def run(self):
        self.emit(QtCore.SIGNAL("update()"))
        self.mfcc.frame_size = int(self.par.frameSizeVal.currentText())
        self.mfcc.overlap = self.mfcc.frame_size/2
        speaker_correct = 0
        speaker_word_correct = 0

        for index,file_audio in enumerate(self.audio_files):
            file_audio = str(file_audio)
            self.audio_signal, self.audio_fs = FileReader.read_audio(file_audio)
            self.silenced_signal, self.audio_fs = self.mfcc.remove_silence(file_audio)
            self.num_frames, self.framed_signal = self.mfcc.frame_blocking(self.silenced_signal)
            self.windowed_signal = self.mfcc.hamm_window(self.framed_signal)
            self.fft_signal = self.mfcc.calc_fft(self.windowed_signal)
            self.log_energy, self.fbank = self.mfcc.fbank(self.fft_signal, self.audio_fs)
            self.features = self.mfcc.features(self.log_energy)

            self.lvq = LVQ(str(self.par.databaseSelect.currentText()))
            result = self.lvq.test_data(self.features[:, 1:14])
            speaker = str(result[0][0])
            word = speaker[speaker.rfind('-')+1:] if speaker.rfind('-') != -1 else "-"
            print "vote for file "+str(index)+" : " + str(result)
            self.par.featuresTbl.setItem(index, 2, QtGui.QTableWidgetItem(speaker[:speaker.rfind('-')]))
            self.par.featuresTbl.setItem(index, 3, QtGui.QTableWidgetItem(word))

            if speaker[:speaker.rfind('-')] == self.par.featuresTbl.item(index,0).text():
                speaker_correct += 1

            if speaker[:speaker.rfind('-')] == self.par.featuresTbl.item(index,0).text() and word == self.par.featuresTbl.item(index,1).text():
                speaker_word_correct += 1

            self.par.speaker_word_acc = (speaker_word_correct / float(len(self.audio_files))) * 100
            self.par.speaker_only_acc = (speaker_correct / float(len(self.audio_files))) * 100

            self.emit(QtCore.SIGNAL("update()"))

        self.emit(QtCore.SIGNAL("finish()"))

class BatchTestWindow(QtGui.QMainWindow, batch_wdw.Ui_MainWdw):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.init_databases()

        self.mfcc = MFCC()

        self.speaker_only_acc = 0.0
        self.speaker_word_acc = 0.0

        self.audio_files = []
        self.progressLbl.setVisible(False)

        self.openAudioBtn.clicked.connect(self.show_open_dialog)
        self.startTestBtn.clicked.connect(self.start_testing)

        self.startTestBtn.setDisabled(True)
        self.frameSizeVal.setDisabled(True)

    def init_databases(self):
        self.database_list = [f[:len(f) - 3] for f in listdir('database/') if isfile(join('database/', f))]
        self.databaseSelect.addItems(QtCore.QStringList(self.database_list))

    def start_testing(self):
        self.progressLbl.setVisible(True)
        self.n = 0
        self.progressBar.setMaximum(len(self.audio_files) + 1)
        self.progressBar.setValue(0)

        testing = TestingThread(self, self.audio_files)
        testing.start()
        QtCore.QObject.connect(testing, QtCore.SIGNAL("finish()"), self.finish_thread)
        QtCore.QObject.connect(testing, QtCore.SIGNAL("update()"), self.update_progress)

    def show_open_dialog(self):
        audioFiles = QtGui.QFileDialog.getOpenFileNames(self, 'Open audio file',
                                                        '',
                                                        "Audio Files (*.wav)",
                                                        None, QtGui.QFileDialog.DontUseNativeDialog)

        for file in audioFiles:
            speaker = str(FileReader.get_output_class(str(file)))
            word = speaker[speaker.rfind('-')+1:] if speaker.rfind('-') != -1 else ""
            self.audio_files.append(file)
            currentRow = self.featuresTbl.rowCount()
            self.featuresTbl.insertRow(currentRow)
            self.featuresTbl.setItem(currentRow, 0, QtGui.QTableWidgetItem(str(speaker[:speaker.rfind('-')])))
            self.featuresTbl.setItem(currentRow, 1, QtGui.QTableWidgetItem(str(word)))

        self.audioFilenameLbl.setText(": " + str(len(self.audio_files)))
        self.startTestBtn.setDisabled(False)
        self.frameSizeVal.setDisabled(False)

    def finish_thread(self):
        self.progressLbl.setStyleSheet("color:green;")
        self.progressLbl.setText("COMPLETE!")

        self.accuracyVal.setText(str(self.speaker_word_acc)+"%")
        self.speakerAccVal.setText(str(self.speaker_only_acc)+"%")

        QtGui.QMessageBox.information(None, "Success!",
                                      "Testing " + str(len(self.audio_files)) + " files complete!\n"
                                      "Accuracy : "+str(self.speaker_word_acc)+"%")

    def update_progress(self):
        self.n += 1
        self.audioFilenameLbl_3.setText(": " + str(self.n - 1))
        self.progressBar.setValue(self.n)