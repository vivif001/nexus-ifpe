import sys
import json
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox 
from gui.login_window import Ui_LoginWindow
from gui.main_menu_window import Ui_MainMenuWindow

Users = []

json_file_path = os.path.join('data', 'users.json')

try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        USERS = json.load(f)
    print(f"Dados carregados: {json_file_path}")
except FileNotFoundError:
    print(f"Erro: O arquivo '{json_file_path}' não foi encontrado")
except json.JSONDecodeError as e:
    print(f"Erro ao analisar dados (possivel estrutura do JSON) '{json_file_path}': {e}")

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Login")
        current_width = self.width()
        current_height = self.height()
        self.setFixedSize(current_width, current_height)
        self.ui.pushButton.clicked.connect(self.auth_login)
        self.main_menu_window = None

    def auth_login(self):
   
        username = self.ui.login_Field.text()
        password = self.ui.password_Field.text()

        if not username or not password:
            QMessageBox.warning(self, "Erro de autenticação", "Usuário e/ou senha não preenchidos.")
            self.ui.password_Field.clear()
            return
        
        authenticated = False
        for user in USERS:
            if username == user["login"] and password == user["password"]:
                QMessageBox.information(self, "Login Bem-Sucedido", f"Bem-vindo(a), {user['firstName']} {user['lastName']}!")
                self.open_main_menu()
                authenticated = True
                break
            
        if not authenticated:
            QMessageBox.warning(self, "Erro de autenticação", "Usuário ou senha incorretos.")
            self.ui.password_Field.clear()
            return

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
        current_width = self.width()
        current_height = self.height()
        self.setFixedSize(current_width, current_height)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())