from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from utils.json_manager import USERS

class LoginDialog(QDialog):
    def __init__(self, title="Login", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(300, 180)

        self.user_id = None
        self.user_role = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.username_label = QLabel("Usuário:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Digite o nome de usuário")

        self.password_label = QLabel("Senha:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Digite a senha")

        self.login_button = QPushButton("Entrar")
        self.login_button.clicked.connect(self.attempt_login)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Erro de Autenticação", "Usuário e/ou senha não preenchidos.")
            return

        authenticated = False
        for user in USERS:
            if username == user["login"] and password == user["password"]:
                self.user_id = user.get("id")
                self.user_role = user.get("role", "user")
                authenticated = True
                QMessageBox.information(self, "Login Sucesso", f"Bem-vindo(a), {user['firstName']} {user['lastName']}!")
                self.accept()
                break
        
        if not authenticated:
            QMessageBox.warning(self, "Erro de Autenticação", "Usuário ou senha incorretos.")
            self.password_input.clear()

    def get_credentials(self):
        return self.user_id, self.user_role