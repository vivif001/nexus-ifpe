import random
import time
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QTextOption

from utils.json_manager import QUESTIONS, USER_STATS, save_json_data, json_user_stats_path

from gui.ui_forms.Ui_QuestionsWindow import Ui_MainWindow as Ui_QuestionsWindow

class QuestionsWindow(QtWidgets.QMainWindow):
    def __init__(self, user_id=None, discipline_filter=None, theme_filter=None, num_questions=0, random_order=True, selected_time_minutes=0, is_simulado_param=False, parent=None):
        super().__init__(parent)
        self.ui = Ui_QuestionsWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"Simulado de Questões ({selected_time_minutes} min)" if selected_time_minutes > 0 else "Prática de Questões")

        self.setFixedSize(self.width(), self.height())
        
        self.current_user_id = user_id
        self.is_simulado_mode = is_simulado_param
        self.start_time = time.time() if self.is_simulado_mode else 0

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
        
        if random_order:
            random.shuffle(filtered_questions_list)

        if num_questions > 0 and num_questions < len(filtered_questions_list):
            self.questions = filtered_questions_list[:num_questions]
        else:
            self.questions = filtered_questions_list

        if not self.questions:
            QMessageBox.warning(self, "Sem Questões", "Nenhuma questão encontrada para os filtros selecionados. Por favor, tente outros filtros.")
            QtCore.QTimer.singleShot(0, self.back_to_main_menu)
            return


        self.current_question_index = 0
        self.user_answers_history = {} 

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        if self.is_simulado_mode and selected_time_minutes > 0:
            self.time_left_in_seconds = selected_time_minutes * 60
        else:
            self.time_left_in_seconds = 0

        if not hasattr(self.ui, 'label_Timer'):
            self.ui.label_Timer = QtWidgets.QLabel(self.ui.centralwidget)
            self.ui.label_Timer.setGeometry(QtCore.QRect(30, 10, 200, 20))
            font = QtGui.QFont()
            font.setFamily("Arial Rounded MT Bold")
            font.setPointSize(12)
            self.ui.label_Timer.setFont(font)
            self.ui.label_Timer.setStyleSheet("color: blue;")
            self.ui.label_Timer.setText("Tempo: --:--")

        self.update_timer_display()
        
        if self.is_simulado_mode and selected_time_minutes > 0: 
            self.timer.start(1000)
        else:
            if hasattr(self.ui, 'label_Timer'):
                self.ui.label_Timer.hide()
            self.timer.stop()

        self.ui.commandLinkButton.clicked.connect(self.go_to_next_question)
        self.ui.commandLinkButton_2.clicked.connect(self.previous_question)
        self.ui.button_Exit.clicked.connect(self.back_to_main_menu)
        self.ui.button_ConfirmAnswer.clicked.connect(self.confirm_answer)
        
        if hasattr(self.ui, 'button_FinishSim'): 
            self.ui.button_FinishSim.clicked.connect(self.finalize_simulado) 
            if not self.is_simulado_mode:
                self.ui.button_FinishSim.hide()
                self.ui.button_ConfirmAnswer.setGeometry(360, 260, 191, 41) 
            else:
                self.ui.button_FinishSim.show()
                self.ui.button_ConfirmAnswer.setGeometry(460, 260, 201, 41) 
                self.ui.button_FinishSim.setGeometry(230, 260, 201, 41)
        else:
            self.ui.button_ConfirmAnswer.setGeometry(360, 260, 191, 41)
            print("AVISO: 'button_FinishSim' não encontrado na UI. Por favor, adicione-o no Qt Designer.")

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

    def update_timer(self):
        self.time_left_in_seconds -= 1
        self.update_timer_display()

        if self.time_left_in_seconds <= 0:
            self.timer.stop()
            QMessageBox.information(self, "Tempo Esgotado!", "O tempo para o simulado acabou. Suas respostas foram salvas.")
            self.finalize_simulado()

    def update_timer_display(self):
        minutes = self.time_left_in_seconds // 60
        seconds = self.time_left_in_seconds % 60
        time_str = f"Tempo: {minutes:02d}:{seconds:02d}"
        self.ui.label_Timer.setText(time_str)

        if self.time_left_in_seconds <= 60:
            self.ui.label_Timer.setStyleSheet("color: red; font-weight: bold;")
        elif self.time_left_in_seconds <= 120: 
            self.ui.label_Timer.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.ui.label_Timer.setStyleSheet("color: blue;")

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
            self.ui.label_2.setText("Nenhuma questão encontrada no banco de dados para os filtros selecionados.")
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
        
        if hasattr(self.ui, 'themeLabel'):
            self.ui.themeLabel.setText(f"Tema: {question_data['theme']}")

        self.ui.label_2.setText(question_data["question_text"])

        self.ui.label.setText(f"A) {question_data['alternatives']['A']}")
        self.ui.label_5.setText(f"B) {question_data['alternatives']['B']}")
        self.ui.label_4.setText(f"C) {question_data['alternatives']['C']}")
        self.ui.label_6.setText(f"D) {question_data['alternatives']['D']}")
        self.ui.label_7.setText(f"E) {question_data['alternatives']['E']}")
        
        if hasattr(self.ui, 'questProgress'):
            current_num = self.current_question_index + 1
            total_num = len(self.questions)
            self.ui.questProgress.setText(f"Questão {current_num} de {total_num}")

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
            
            if not is_correct_answer:
                correct_answer_letter = question_data["correct_answer"]
                correct_label = self.alternative_labels_by_letter.get(correct_answer_letter)
                if correct_label:
                    correct_label.setStyleSheet("background-color: #C8FFC8; border: 1px solid green; font-weight: bold;")

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

        if is_correct:
            if selected_label:
                selected_label.setStyleSheet("background-color: #C8FFC8; border: 1px solid green;")
            QMessageBox.information(self, "Resposta Correta!",
                                     "Parabéns! Sua resposta está correta. Agora você pode avançar para a próxima questão.")
        else:
            if selected_label:
                selected_label.setStyleSheet("background-color: #FFC8C8; border: 1px solid red;")

            correct_answer_letter = current_question["correct_answer"]
            correct_label = self.alternative_labels_by_letter.get(correct_answer_letter)
            if correct_label:
                correct_label.setStyleSheet("background-color: #C8FFC8; border: 1px solid green; font-weight: bold;")

            QMessageBox.warning(self, "Resposta Incorreta!",
                                 f"A resposta correta era: {correct_answer_letter}. Agora você pode avançar para a próxima questão.")

        for radio_button in self.alternatives_group.buttons():
            radio_button.setEnabled(False)
        self.ui.button_ConfirmAnswer.setEnabled(False)

        self.update_user_statistics(self.current_user_id, discipline, theme, is_correct)

        is_last_question = (self.current_question_index == len(self.questions) - 1)
        if is_last_question and not self.is_simulado_mode: 
            QMessageBox.information(self, "Prática Concluída!", "Você concluiu todas as questões da sua sessão de prática!")
            self.back_to_main_menu()
        elif is_last_question and self.is_simulado_mode: 
            pass
        
        return True
    
    def finalize_simulado(self):
        self.timer.stop() 
        total_time_spent_seconds = 0
        if self.is_simulado_mode and self.start_time > 0:
            total_time_spent_seconds = int(time.time() - self.start_time)
            minutes = total_time_spent_seconds // 60
            seconds = total_time_spent_seconds % 60
            time_spent_str = f"{minutes:02d}:{seconds:02d}"
        else:
            time_spent_str = "N/A"

        correct_answers_count = 0
        total_answered_in_simulado = 0     
        for q_data in self.questions:
            q_id = q_data["id"]
            if q_id in self.user_answers_history:
                user_answer_info = self.user_answers_history[q_id]
                is_correct = user_answer_info['is_correct']
                total_answered_in_simulado +=1
                if is_correct:
                    correct_answers_count +=1
        
        summary_message = (
            f"Simulado Finalizado!\n\n"
            f"Questões Respondidas: {total_answered_in_simulado}\n"
            f"Questões Acertadas: {correct_answers_count}\n"
            f"Tempo Gasto: {time_spent_str}"
        )
        
        QMessageBox.information(self, "Relatório do Simulado", summary_message)
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
            if not self.is_simulado_mode:
                self.back_to_main_menu()

    def previous_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.display_question()

    def back_to_main_menu(self):
        self.timer.stop()
        self.hide()
        if self.parent():
            self.parent().show() 
        else:
            print("Erro: Não há janela pai para retornar. Voltando ao Login.")
          
            from gui.login_window import LoginWindow
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