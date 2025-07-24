from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from utils.json_manager import USERS, save_json_data, json_users_path
from utils.mail_sender import send_new_user_email
from gui.ui_forms.Ui_AdminWindow import Ui_AdminWindow

class AdminWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AdminWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Painel de Administração")
        
        self.ui.button_Exit.clicked.connect(self.back_to_main_menu)
        self.ui.register_button.clicked.connect(self.create_new_user_and_send_email)
        
    def create_new_user_and_send_email(self):
        first_name = self.ui.login_Field_6.text().strip() 
        last_name = self.ui.login_Field_5.text().strip() 
        email = self.ui.login_Field_8.text().strip()
        password = self.ui.login_Field_7.text().strip() 

        if not all([first_name, last_name, email, password]):
            QMessageBox.warning(self, "Campos Vazios", "Por favor, preencha todos os campos: Nome, Sobrenome, E-mail e Senha.")
            return

        for user in USERS:
            if user["login"] == email:
                QMessageBox.warning(self, "Usuário Existente", "Já existe um usuário cadastrado com este e-mail/login.")
                return

        new_user_id = str(len(USERS) + 1)
        
        new_user_data = {
            "id": new_user_id,
            "firstName": first_name,
            "lastName": last_name,
            "login": email,
            "password": password,
            "role": "user"
        }

        USERS.append(new_user_data)

        save_json_data(USERS, json_users_path)
        QMessageBox.information(self, "Cadastro Concluído", f"Usuário '{first_name} {last_name}' cadastrado e salvo com sucesso!")

        try:
            send_new_user_email(email, first_name, last_name, new_user_data["login"], password)
            QMessageBox.information(self, "E-mail Enviado", "E-mail de boas-vindas enviado com sucesso!")
        except Exception as e:
            QMessageBox.warning(self, "Erro ao Enviar E-mail", f"Não foi possível enviar o e-mail de boas-vindas: {e}")
        
        self.ui.login_Field_6.clear()
        self.ui.login_Field_5.clear()
        self.ui.login_Field_8.clear() 
        self.ui.login_Field_7.clear() 

    def back_to_main_menu(self):
        self.hide()
        if self.parent():
            self.parent().show()
        else:
            from gui.login_window import LoginWindow
            login_window = LoginWindow()
            login_window.show()