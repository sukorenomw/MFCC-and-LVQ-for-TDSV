import controller
import sys

from PyQt4 import QtGui

def main():
    app = QtGui.QApplication(sys.argv)
    mainWdw = controller.trainingWindowController.MainWindow()
    mainWdw.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()