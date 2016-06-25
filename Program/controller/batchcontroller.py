import view.batchTrainWindow as batch_wdw
import numpy as np
import xlsxwriter as xlwt

from databaseconnector import TYPE
from databaseconnector import DatabaseConnector
from mfcc import MFCC
from filereader import FileReader
from PyQt4 import QtCore, QtGui
from random import sample


class ExtractThread(QtCore.QThread):
    def __init__(self, parent, audio_files, database_name):
        QtCore.QThread.__init__(self, parent)
        self.audio_files = audio_files
        self.mfcc = MFCC()
        self.par = parent
        self.variances = []
        self.all_features = []
        self.db = DatabaseConnector(database_name)

    def write_excel(self,rata2):
        self.all_features = np.asarray(self.all_features).T

        wbk = xlwt.Workbook("hasil-ekstraksi.xlsx")
        sheet = wbk.add_worksheet()

        row = 0
        col = 0
        for x in xrange(32):
            sheet.write(0, x, "data-" + str(x))

        for index, item in enumerate(self.all_features):
            for x in xrange(len(item)):
                try:
                    teext = str(item[x])
                    sheet.write(row + 1, col, teext)
                    row += 1
                except AttributeError:
                    row += 1
            row = 0
            col += 1

        for i in xrange(32):
            sheet.write(5250,i, str(rata2[i]))

        wbk.close()

    def run(self):
        self.emit(QtCore.SIGNAL("update()"))
        self.mfcc.frame_size = int(self.par.frameSizeVal.currentText())
        self.mfcc.overlap = self.mfcc.frame_size / 2
        for index, file_audio in enumerate(self.audio_files):
            file_audio = str(file_audio)
            self.audio_signal, self.audio_fs = FileReader.read_audio(file_audio)
            self.silenced_signal, self.audio_fs = self.mfcc.remove_silence(file_audio)
            self.num_frames, self.framed_signal = self.mfcc.frame_blocking(self.silenced_signal)
            self.windowed_signal = self.mfcc.hamm_window(self.framed_signal)
            self.fft_signal = self.mfcc.calc_fft(self.windowed_signal)
            self.log_energy, self.fbank = self.mfcc.fbank(self.fft_signal, self.audio_fs)
            self.features = self.mfcc.features(self.log_energy)
            # var = [st.variance(self.features[:,i]) for i in xrange(self.mfcc.num_filter)]
            # [self.all_features.append(self.features[i,:]) for i in xrange(self.features.shape[0])]
            # self.variances.append(var)
            features = []


            if TYPE == 1:
                file_id = self.db.insert("files", {"file_path": file_audio})
                for i in xrange(self.features.shape[0]):
                    # [31, 28, 29, 30, 27, 26, 25, 24, 23, 22, 20, 21, 19
                    # features.append([file_id, i, self.features[i, 1:14], str(self.par.featuresTbl.item(index,1).text())])
                    features.append([file_id, i, self.features[i, [1, 2, 3, 4, 5, 7, 6, 9, 8, 10, 11, 12, 13]],
                                     str(self.par.featuresTbl.item(index, 1).text())])

                self.db.insert_features(features)

            else:
                output_class_id = self.db.insert("output_classes",
                                                 {"file_path": file_audio,
                                                  "class": str(FileReader.get_output_class(file_audio))})
                for i in xrange(self.features.shape[0]):
                    features.append([output_class_id, i, self.features[i, 1:14]])
                self.db.insert_features(features)

            self.emit(QtCore.SIGNAL("update()"))

        # self.variances = np.asarray(self.variances)
        # rata2 = [st.mean(self.variances[:,i]) for i in xrange(self.mfcc.num_filter)]
        # self.write_excel(rata2)
        # print str(np.sort(rata2))
        # print str(np.argsort(rata2))
        self.emit(QtCore.SIGNAL("finish()"))


class BatchWindow(QtGui.QMainWindow, batch_wdw.Ui_MainWdw):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.actionAbout_Qt.triggered.connect(QtGui.qApp.aboutQt)
        self.actionAbout.triggered.connect(self.about)

        self.openAudioBtn.clicked.connect(self.show_open_dialog)
        self.extractSaveBtn.clicked.connect(self.extract_and_save)
        self.shuffleBtn.clicked.connect(self.shuffle_files)

        self.inclWordCheck.clicked.connect(self.include_word)

        self.audio_files = []
        self.progressLbl.setVisible(False)

    def show_open_dialog(self):
        audioFiles = QtGui.QFileDialog.getOpenFileNames(self, 'Open audio file',
                                                        '',
                                                        "Audio Files (*.wav)",
                                                        None, QtGui.QFileDialog.DontUseNativeDialog)
        self.featuresTbl.setColumnWidth(0, 300)

        for file in audioFiles:
            self.audio_files.append(file)
            currentRow = self.featuresTbl.rowCount()
            self.featuresTbl.insertRow(currentRow)
            self.featuresTbl.setItem(currentRow, 0, QtGui.QTableWidgetItem(str(file)))
            self.featuresTbl.setItem(currentRow, 1, QtGui.QTableWidgetItem(str(FileReader.get_output_class(str(file)))))

        self.audioFilenameLbl.setText(": " + str(len(self.audio_files)))

    def shuffle_files(self):
        self.audio_files = sample(self.audio_files, len(self.audio_files))
        for i in xrange(self.featuresTbl.rowCount()):
            self.featuresTbl.setItem(i, 0, QtGui.QTableWidgetItem(str(self.audio_files[i])))
            self.featuresTbl.setItem(i, 1, QtGui.QTableWidgetItem(str(FileReader.get_output_class(str(self.audio_files[i])))))

    def include_word(self):
        if self.inclWordCheck.isChecked():
            for i in xrange(self.featuresTbl.rowCount()):
                text = str(self.featuresTbl.item(i, 0).text())
                self.featuresTbl.setItem(i, 1, QtGui.QTableWidgetItem(str(FileReader.get_output_class(str(text)))))
        else:
            for i in xrange(self.featuresTbl.rowCount()):
                text = str(self.featuresTbl.item(i, 1).text())
                self.featuresTbl.setItem(i, 1, QtGui.QTableWidgetItem(str(text[:text.rfind("-")])))

    def extract_and_save(self):
        self.progressLbl.setVisible(True)
        self.n = 0
        self.progressBar.setMaximum(len(self.audio_files) + 1)
        self.progressBar.setValue(0)
        insert_feature = ExtractThread(self, self.audio_files, str(self.databaseNameVal.text()))
        insert_feature.start()
        QtCore.QObject.connect(insert_feature, QtCore.SIGNAL("finish()"), self.finish_thread)
        QtCore.QObject.connect(insert_feature, QtCore.SIGNAL("update()"), self.update_progress)

    def finish_thread(self):
        self.progressLbl.setStyleSheet("color:green;")
        self.progressLbl.setText("COMPLETE!")
        QtGui.QMessageBox.information(None, "Success!",
                                      "Save features of " + str(len(self.audio_files)) + " files to database success!")

    def update_progress(self):
        self.n += 1
        self.audioFilenameLbl_3.setText(": " + str(self.n - 1))
        self.progressBar.setValue(self.n)

    def about(self):
        QtGui.QMessageBox.information(self, "Text Dependent Speaker Verification",
                                      "Text Dependent Speaker Verification - the "
                                      "Final project software to identify and verify Speaker based on their speech.\n\n"
                                      "\xa9 Sukoreno Mukti - 1112051 \n Informatics Engineering Dept. ITHB")
