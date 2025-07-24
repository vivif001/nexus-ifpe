import sys
from PyQt5 import QtWidgets

from gui.login_window import LoginWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())