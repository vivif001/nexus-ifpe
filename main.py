import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox 

from gui.login_window import Ui_LoginWindow
from gui.main_menu_window import Ui_MainMenuWindow

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Login")

        self.ui.pushButton.clicked.connect(self.auth_login)

        self.main_menu_window = None

    def auth_login(self):
   
        username = self.ui.login_Field.text()
        password = self.ui.password_Field.text()

        mocked_username = "vivi"
        mocked_password = "123"

        if username == mocked_username and password == mocked_password:
            QMessageBox.information(self, "Login Bem-Sucedido", "Bem-vindo!")
            self.open_main_menu()
        elif username != mocked_username or password != mocked_password:
            QMessageBox.warning(self, "Erro de Login", "Usuário ou senha incorretos. Tente novamente.")
            self.ui.password_Field.clear()
        elif username == "" or password == "":
            QMessageBox.warning(self, "Erro de autenticação, ", "Usuário ou senha não preenchidos")
            self.ui.password_Field.clear()

    def open_main_menu(self):
        if self.main_menu_window is None:
            self.main_menu_window = MainMenuWindow()
        self.hide() 
        self.main_menu_window.show() 

class MainMenuWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainMenuWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Menu Principal")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())