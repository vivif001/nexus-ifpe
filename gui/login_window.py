from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from utils.json_manager import USERS
from gui.ui_forms.Ui_LoginWindow import Ui_LoginWindow 
from gui.main_menu_window import MainMenuWindow 

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Login")
        
        self.setFixedSize(self.width(), self.height())
        
        self.ui.pushButton.clicked.connect(self.auth_login)
        self.main_menu_window = None

    def auth_login(self):
        username = self.ui.login_Field.text()
        password = self.ui.password_Field.text()

        if not username or not password:
            QMessageBox.warning(self, "Erro de autenticação", "Usuário e/ou senha não preenchidos.")
            self.ui.password_Field.clear()
            return

        authenticated_user_role = None
        authenticated_user_id = None
        
        for user in USERS: 
            if username == user["login"] and password == user["password"]:
                QMessageBox.information(self, "Login Bem-Sucedido", f"Bem-vindo(a), {user['firstName']} {user['lastName']}!")
                authenticated_user_role = user.get("role", "user")
                authenticated_user_id = user.get("id") 
                self.open_main_menu(authenticated_user_role, authenticated_user_id)
                return 
            
        QMessageBox.warning(self, "Erro de autenticação", "Usuário ou senha incorretos.")
        self.ui.password_Field.clear()

    def open_main_menu(self, user_role, user_id):
        self.main_menu_window = MainMenuWindow(user_role, user_id, parent_login_window=self)
        self.hide()
        self.main_menu_window.show()