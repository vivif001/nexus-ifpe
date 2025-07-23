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
        
        self.setFixedSize(self.width(), self.height()) # Mantém o tamanho fixo da janela
        
        self.ui.pushButton.clicked.connect(self.auth_login) # Conecta o botão de login
        self.main_menu_window = None # Referência para a janela do menu principal

    def auth_login(self):
        """
        Autentica o usuário com base no nome de usuário (e-mail) e senha fornecidos.
        Exibe mensagens de erro ou sucesso e abre o menu principal se o login for bem-sucedido.
        """
        username = self.ui.login_Field.text()
        password = self.ui.password_Field.text()

        # Validação de campos vazios
        if not username or not password:
            QMessageBox.warning(self, "Erro de autenticação", "Usuário e/ou senha não preenchidos.")
            self.ui.password_Field.clear() # Limpa o campo da senha
            return

        authenticated_user_role = None
        authenticated_user_id = None
        
        # Procura o usuário na lista global de usuários
        for user in USERS: 
            if username == user["login"] and password == user["password"]:
                QMessageBox.information(self, "Login Bem-Sucedido", f"Bem-vindo(a), {user['firstName']} {user['lastName']}!")
                authenticated_user_role = user.get("role", "user") # Pega o papel, padrão 'user'
                authenticated_user_id = user.get("id") # Pega o ID do usuário
                self.open_main_menu(authenticated_user_role, authenticated_user_id) # Abre o menu principal
                return 
            
        # Se o loop terminar e o usuário não for encontrado
        QMessageBox.warning(self, "Erro de autenticação", "Usuário ou senha incorretos.")
        self.ui.password_Field.clear() # Limpa o campo da senha

    def open_main_menu(self, user_role, user_id):
        """
        Cria e exibe a janela do Menu Principal, passando o papel e ID do usuário autenticado.
        Esconde a janela de login.
        """
        self.main_menu_window = MainMenuWindow(user_role, user_id, parent_login_window=self)
        self.hide()
        self.main_menu_window.show()