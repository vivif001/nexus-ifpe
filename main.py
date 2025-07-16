import sys
import json
import os
from utils.mail_sender import send_new_user_email
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QTextOption
from gui.login_window import Ui_LoginWindow
from gui.main_menu_window import Ui_MainMenuWindow
from gui.questions_window import Ui_MainWindow as Ui_QuestionsWindow
from gui.admin_window import Ui_AdminWindow

USERS = []
QUESTIONS = []
USER_STATS = []

json_users_path = os.path.join('data', 'users.json')
json_questions_path = os.path.join('data', 'questions.json')
json_user_stats_path = os.path.join('data', 'user_stats.json')

def load_json_data(file_path):
    try:
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4)
            print(f"Arquivo '{file_path}' não encontrado. Criado como JSON vazio.")
            return []
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Dados carregados de: {file_path}")
            return data
    except json.JSONDecodeError as e:
        print(f"Erro ao analisar dados em '{file_path}': {e}. Verifique a estrutura do JSON.")
        QMessageBox.critical(None, "Erro de Leitura", f"Erro ao carregar '{file_path}': {e}\nVerifique se o JSON está bem formatado.")
        return []
    except Exception as e:
        print(f"Erro inesperado ao carregar '{file_path}': {e}")
        QMessageBox.critical(None, "Erro", f"Erro inesperado ao carregar '{file_path}': {e}")
        return []

def save_json_data(data, file_path):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Dados salvos em: {file_path}")
    except IOError as e:
        QMessageBox.critical(None, "Erro de Escrita", f"Não foi possível salvar os dados em '{file_path}': {e}")
    except Exception as e:
        QMessageBox.critical(None, "Erro Inesperado", f"Erro inesperado ao salvar '{file_path}': {e}")

USERS = load_json_data(json_users_path)
QUESTIONS = load_json_data(json_questions_path)
USER_STATS = load_json_data(json_user_stats_path)


class FilterQuestionsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtrar Questões")
        self.setFixedSize(350, 250)

        self.selected_discipline = None
        self.selected_theme = None

        self.layout = QtWidgets.QVBoxLayout(self)

        self.discipline_label = QtWidgets.QLabel("Selecione a Disciplina:")
        self.combo_Discipline = QtWidgets.QComboBox(self)
        self.layout.addWidget(self.discipline_label)
        self.layout.addWidget(self.combo_Discipline)

        self.theme_label = QtWidgets.QLabel("Selecione o Tema:")
        self.combo_Theme = QtWidgets.QComboBox(self)
        self.layout.addWidget(self.theme_label)
        self.layout.addWidget(self.combo_Theme)
        
        self.layout.addStretch()

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.button_StartQuiz = QtWidgets.QPushButton("Iniciar Quiz", self)
        self.button_Cancel = QtWidgets.QPushButton("Cancelar", self)
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.button_StartQuiz)
        self.buttons_layout.addWidget(self.button_Cancel)
        self.layout.addLayout(self.buttons_layout)
        self.button_StartQuiz.clicked.connect(self.on_start_quiz_clicked)
        self.button_Cancel.clicked.connect(self.reject) 

        self.combo_Discipline.currentIndexChanged.connect(self.populate_themes)

        self.populate_disciplines()
        self.populate_themes()

    def populate_disciplines(self):
        self.combo_Discipline.clear()
        disciplines = sorted(list(set(q["discipline"] for q in QUESTIONS)))
        self.combo_Discipline.addItem("Todas as Disciplinas")
        self.combo_Discipline.addItems(disciplines)

    def populate_themes(self):
        self.combo_Theme.clear()
        selected_discipline = self.combo_Discipline.currentText()
        
        themes = set()
        if selected_discipline == "Todas as Disciplinas":
            for q in QUESTIONS:
                themes.add(q["theme"])
        else:
            for q in QUESTIONS:
                if q["discipline"] == selected_discipline:
                    themes.add(q["theme"])
        
        sorted_themes = sorted(list(themes))
        self.combo_Theme.addItem("Todos os Temas")
        self.combo_Theme.addItems(sorted_themes)

    def on_start_quiz_clicked(self):
        discipline_text = self.combo_Discipline.currentText()
        theme_text = self.combo_Theme.currentText()

        self.selected_discipline = discipline_text if discipline_text != "Todas as Disciplinas" else None
        self.selected_theme = theme_text if theme_text != "Todos os Temas" else None
        
        self.accept()

    def get_filters(self):
        return self.selected_discipline, self.selected_theme

class QuestionsWindow(QtWidgets.QMainWindow):
    def __init__(self, user_id=None, discipline_filter=None, theme_filter=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_QuestionsWindow()
        self.ui.setupUi(self) 
        self.setWindowTitle("Questões")

        current_width = self.width()
        current_height = self.height()
        self.setFixedSize(current_width, current_height)

        self.current_user_id = user_id
        
        filtered_questions_list = []
        for q in QUESTIONS:
            match_discipline = True
            match_theme = True
            
            if discipline_filter is not None:
                match_discipline = (q["discipline"] == discipline_filter)
            
            if theme_filter is not None:
                match_theme = (q["theme"] == theme_filter)
            
            if match_discipline and match_theme:
                filtered_questions_list.append(q)
        
        self.questions = filtered_questions_list

        if not self.questions:
            QMessageBox.warning(self, "Sem Questões", "Nenhuma questão encontrada para os filtros selecionados. Por favor, tente outros filtros.")
            self.back_to_main_menu() 
            return

        self.current_question_index = 0
        self.user_answers_history = {} 

        self.ui.button_ConfirmAnswer.clicked.connect(self.confirm_answer)
        self.ui.commandLinkButton.clicked.connect(self.go_to_next_question)
        self.ui.commandLinkButton_2.clicked.connect(self.previous_question)
        self.ui.button_Exit.clicked.connect(self.back_to_main_menu)

        self.alternatives_group = QtWidgets.QButtonGroup(self)
        self.alternatives_group.addButton(self.ui.Alternative_A, 0)
        self.alternatives_group.addButton(self.ui.Alternative_B, 1)
        self.alternatives_group.addButton(self.ui.Alternative_C, 2)
        self.alternatives_group.addButton(self.ui.Alternative_D, 3)
        self.alternatives_group.addButton(self.ui.Alternative_E, 4)
        
        self.alternative_labels = {
            0: self.ui.label,
            1: self.ui.label_5,
            2: self.ui.label_4,
            3: self.ui.label_6,
            4: self.ui.label_7 
        }
        
        self.alternative_labels_by_letter = {
            "A": self.ui.label,
            "B": self.ui.label_5,
            "C": self.ui.label_4,
            "D": self.ui.label_6,
            "E": self.ui.label_7
        }

        self.display_question()

    def display_question(self):
        for label in self.alternative_labels.values():
            label.setStyleSheet("")
        
        self.alternatives_group.setExclusive(False)
        for radio_button in self.alternatives_group.buttons():
            radio_button.setChecked(False)
            radio_button.setEnabled(True)
        self.alternatives_group.setExclusive(True)
        self.ui.button_ConfirmAnswer.setEnabled(True) 

        if not self.questions:
            self.ui.label_2.setText("Nenhuma questão encontrada no banco de dados.")
            self.ui.label.setText("")
            self.ui.label_5.setText("")
            self.ui.label_4.setText("")
            self.ui.label_6.setText("")
            self.ui.label_7.setText("")
            self.ui.commandLinkButton.setEnabled(False)
            self.ui.commandLinkButton_2.setEnabled(False)
            self.ui.button_ConfirmAnswer.setEnabled(False)
            return

        question_data = self.questions[self.current_question_index]
        current_question_id = question_data["id"]

        self.ui.label_2.setText(question_data["question_text"])
        
        self.ui.label.setText(f"A) {question_data['alternatives']['A']}")
        self.ui.label_5.setText(f"B) {question_data['alternatives']['B']}")
        self.ui.label_4.setText(f"C) {question_data['alternatives']['C']}") 
        self.ui.label_6.setText(f"D) {question_data['alternatives']['D']}")
        self.ui.label_7.setText(f"E) {question_data['alternatives']['E']}")

        if current_question_id in self.user_answers_history:
            answered_info = self.user_answers_history[current_question_id]
            selected_alternative_letter = answered_info['selected_alternative']
            is_correct_answer = answered_info['is_correct']
            
            for rb_id, rb in enumerate(self.alternatives_group.buttons()):
                label = self.alternative_labels.get(rb_id)
                if label:
                    if self.get_alternative_letter_from_id(rb_id) == selected_alternative_letter:
                        rb.setChecked(True)
                        if is_correct_answer:
                            label.setStyleSheet("background-color: #C8FFC8; border: 1px solid green;")
                        else:
                            label.setStyleSheet("background-color: #FFC8C8; border: 1px solid red;")
                    
                    rb.setEnabled(False)
            
            self.ui.button_ConfirmAnswer.setEnabled(False) 
        
        self.ui.commandLinkButton_2.setEnabled(self.current_question_index > 0)
        self.ui.commandLinkButton.setEnabled(self.current_question_index < len(self.questions) - 1)

    def get_alternative_letter_from_id(self, rb_id):
        mapping = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E"}
        return mapping.get(rb_id)

    def get_selected_alternative(self):
        selected_button = self.alternatives_group.checkedButton()
        if selected_button:
            return self.get_alternative_letter_from_id(self.alternatives_group.id(selected_button))
        return None

    def confirm_answer(self):
        """Processa a resposta do usuário, aplica feedback visual, atualiza estatísticas e encerra se for a última questão."""
        if self.current_user_id is None:
            QMessageBox.critical(self, "Erro de Usuário", "ID do usuário não disponível. Por favor, relogue.")
            self.back_to_main_menu()
            return False

        selected_alternative = self.get_selected_alternative()
        if selected_alternative is None:
            QMessageBox.warning(self, "Atenção", "Por favor, selecione uma alternativa antes de confirmar.")
            return False

        current_question = self.questions[self.current_question_index]
        current_question_id = current_question["id"]
        is_correct = (selected_alternative == current_question["correct_answer"])

        discipline = current_question["discipline"]
        theme = current_question["theme"]

        self.user_answers_history[current_question_id] = {
            'selected_alternative': selected_alternative,
            'is_correct': is_correct
        }

        selected_label = self.alternative_labels.get(self.alternatives_group.id(self.alternatives_group.checkedButton()))
        
        is_last_question = (self.current_question_index == len(self.questions) - 1)

        if is_correct:
            if selected_label:
                selected_label.setStyleSheet("background-color: #C8FFC8; border: 1px solid green;")
            QMessageBox.information(self, "Resposta Correta!", 
                                    "Parabéns! Sua resposta está correta. Agora você pode avançar para a próxima questão." if not is_last_question else "Parabéns! Sua resposta está correta. Você concluiu todas as questões!")
        else:
            if selected_label:
                selected_label.setStyleSheet("background-color: #FFC8C8; border: 1px solid red;")
            
            correct_answer_letter = current_question["correct_answer"]
            correct_label = self.alternative_labels_by_letter.get(correct_answer_letter)
            if correct_label:
                correct_label.setStyleSheet("background-color: #C8FFC8; border: 1px solid green; font-weight: bold;") 

            QMessageBox.warning(self, "Resposta Incorreta!", 
                                f"A resposta correta era: {correct_answer_letter}. Agora você pode avançar para a próxima questão." if not is_last_question else f"Ops! A resposta correta era: {correct_answer_letter}. Você concluiu todas as questões!")

        for radio_button in self.alternatives_group.buttons():
            radio_button.setEnabled(False)

        self.ui.button_ConfirmAnswer.setEnabled(False)

        self.update_user_statistics(self.current_user_id, discipline, theme, is_correct)

        if is_last_question:
            self.back_to_main_menu()

    def go_to_next_question(self):
        current_question_id = self.questions[self.current_question_index]["id"]
        
        if current_question_id not in self.user_answers_history:
            QMessageBox.warning(self, "Atenção", "Por favor, confirme sua resposta antes de avançar para a próxima questão.")
            return

        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.display_question()
        else:
            QMessageBox.information(self, "Fim das Questões", "Você chegou ao final das questões disponíveis!")
            self.back_to_main_menu()

    def previous_question(self):
        """Volta para a questão anterior."""
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.display_question()

    def back_to_main_menu(self):
        self.hide()
        if self.parent():
            self.parent().show()
        else:
            print("Erro: Não há janela pai para retornar. Voltando ao Login.")
            login_window = LoginWindow()
            login_window.show()

    def update_user_statistics(self, user_id, discipline_name, theme_name, is_correct):
        user_stats_entry = next((item for item in USER_STATS if item["user_id"] == user_id), None)
        if not user_stats_entry:
            user_stats_entry = {
                "user_id": user_id,
                "total_questions_answered": 0,
                "total_correct_answers": 0,
                "correct_percentage": 0.0,
                "disciplines": {}
            }
            USER_STATS.append(user_stats_entry)

        user_stats_entry["total_questions_answered"] += 1
        if is_correct:
            user_stats_entry["total_correct_answers"] += 1
        
        user_stats_entry["correct_percentage"] = (user_stats_entry["total_correct_answers"] / user_stats_entry["total_questions_answered"]) * 100 \
                                                if user_stats_entry["total_questions_answered"] > 0 else 0.0

        if discipline_name not in user_stats_entry["disciplines"]:
            user_stats_entry["disciplines"][discipline_name] = {
                "total_answered": 0,
                "total_correct": 0,
                "themes": {}
            }

        discipline_stats = user_stats_entry["disciplines"][discipline_name]
        discipline_stats["total_answered"] += 1
        if is_correct:
            discipline_stats["total_correct"] += 1

        if theme_name not in discipline_stats["themes"]:
            discipline_stats["themes"][theme_name] = {
                "answered": 0,
                "correct": 0,
                "incorrect": 0
            }

        theme_stats = discipline_stats["themes"][theme_name]
        theme_stats["answered"] += 1
        if is_correct:
            theme_stats["correct"] += 1
        else:
            theme_stats["incorrect"] += 1

        save_json_data(USER_STATS, json_user_stats_path)
        
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

        print(f"DEBUG - Nome: '{first_name}'")
        print(f"DEBUG - Sobrenome: '{last_name}'")
        print(f"DEBUG - E-mail: '{email}'")
        print(f"DEBUG - Senha: '{password}'")

        if not all([first_name, last_name, email, password]):
            QMessageBox.warning(self, "Campos Vazios", "Por favor, preencha todos os campos: Nome, Sobrenome, E-mail e Senha.")
            return

        new_user_id = str(len(USERS) + 1)
        
        for user in USERS:
            if user["login"] == email:
                QMessageBox.warning(self, "Usuário Existente", "Já existe um usuário cadastrado com este e-mail/login.")
                return

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

        send_new_user_email(email, first_name, last_name, new_user_data["login"], password)
        
        self.ui.login_Field_6.clear()
        self.ui.login_Field_5.clear()
        self.ui.login_Field_8.clear() 
        self.ui.login_Field_7.clear() 

    def back_to_main_menu(self):
        self.hide()
        if self.parent():
            self.parent().show()
        else:
            print("Erro: Não há janela pai para retornar. Voltando ao Login.")
            login_window = LoginWindow()
            login_window.show()
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

class MainMenuWindow(QtWidgets.QMainWindow):
    def __init__(self, user_role="user", user_id=None, parent_login_window=None):
        super().__init__()
        self.ui = Ui_MainMenuWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Menu Principal")
        
        self.questions_window = None
        self.admin_window = None
        self.current_user_id = user_id
        self.parent_login_window = parent_login_window


        current_width = self.width()
        current_height = self.height()
        self.setFixedSize(current_width, current_height)

        self.ui.button_Questions.clicked.connect(self.open_questions_window)
        self.ui.button_Exit.clicked.connect(self.quit_main_menu)
        
        if hasattr(self.ui, 'button_Admin'):
            if user_role != "admin":
                self.ui.button_Admin.hide()
                if hasattr(self.ui, 'label_Admin'):
                    self.ui.label_Admin.hide()
            else:
                self.ui.button_Admin.show()
                if hasattr(self.ui, 'label_Admin'):
                    self.ui.label_Admin.show()     
                self.ui.button_Admin.clicked.connect(self.open_admin_window)
                    
                    
    def quit_main_menu(self):
        self.hide()
        if self.parent_login_window:
            self.parent_login_window.show()
        else:
            print("Erro: Não há janela de login pai para retornar. Saindo da aplicação.")
            QtWidgets.QApplication.quit()

    def open_questions_window(self):
        filter_dialog = FilterQuestionsDialog(self) 
        
        if filter_dialog.exec_() == QtWidgets.QDialog.Accepted:
            discipline_filter, theme_filter = filter_dialog.get_filters()
            
            self.questions_window = QuestionsWindow(
                user_id=self.current_user_id, 
                discipline_filter=discipline_filter,
                theme_filter=theme_filter,       
                parent=self
            )
            if self.questions_window.questions:
                self.hide()
                self.questions_window.show()
            else:
                pass 
        else:
            QMessageBox.information(self, "Seleção Cancelada", "Nenhum filtro aplicado. Retornando ao menu principal.")
            
    def open_admin_window(self):
        self.admin_window = AdminWindow(parent=self)
        self.hide()
        self.admin_window.show()

    def open_main_menu(self, user_role, user_id):
        self.main_menu_window = MainMenuWindow(user_role, user_id, parent_login_window=self)
        self.hide()
        self.main_menu_window.show()
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())