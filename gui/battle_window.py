import random
import time 
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox

from gui.ui_forms.Ui_BattleWindow import Ui_BattleWindow 
from utils.json_manager import USERS, QUESTIONS, USER_STATS, save_json_data, json_user_stats_path

class BattleWindow(QtWidgets.QMainWindow):
    def __init__(self, player1_id, player2_id, battle_settings, parent=None):
        super().__init__(parent)
        self.ui = Ui_BattleWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Modo Batalha")
        self.parent_menu = parent 

        self.player1_id = player1_id 
        self.player2_id = player2_id 
        self.battle_settings = battle_settings 

        self.num_rounds = self.battle_settings.get("num_rounds", 5)
        self.time_per_question = self.battle_settings.get("time_per_question", 30)
        self.use_game_cards = self.battle_settings.get("use_game_cards", False)
        self.enable_power_ups = self.battle_settings.get("enable_power_ups", False)
        self.discipline_filter = self.battle_settings.get("discipline_filter", None)
        self.theme_filter = self.battle_settings.get("theme_filter", None)

        self.player1_name = self.get_user_name_by_id(self.player1_id)
        self.player2_name = self.get_user_name_by_id(self.player2_id)
        
        self.ui.player1Label.setText(self.player1_name.upper())
        self.ui.player2Label.setText(self.player2_name.upper())

        self.current_player_turn = self.player1_id 
        self.player_scores = {
            self.player1_id: 0,
            self.player2_id: 0
        }
        self.current_round = 0
        self.questions_answered_in_round = 0 

        self.available_questions = self.load_and_filter_questions()
        self.used_questions_ids = set() 

        if not self.available_questions:
            QMessageBox.warning(self, "Sem Questões", "Nenhuma questão encontrada para os filtros selecionados. Retornando ao menu principal.")
            QtCore.QTimer.singleShot(0, self.close_battle_window)
            return

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.handle_timeout)
        self.time_left_in_seconds = self.time_per_question

        self.ui.labelTimer.setText("TEMPO: --:--") 
        
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

        self.ui.button_Exit.clicked.connect(self.close_battle_window)
        self.ui.button_ConfirmAnswer.clicked.connect(self.confirm_answer)
        
        if hasattr(self.ui, 'commandLinkButton'): self.ui.commandLinkButton.hide()
        if hasattr(self.ui, 'commandLinkButton_2'): self.ui.commandLinkButton_2.hide()
        if hasattr(self.ui, 'button_FinishSim'): self.ui.button_FinishSim.hide() 

        self.setFixedSize(self.width(), self.height())

        self.start_new_round()
        self.display_question() 

    def get_user_name_by_id(self, user_id):
        for user in USERS:
            if user.get("id") == user_id:
                first_name = user.get("firstName", "")
                return first_name.strip()
        return f"Usuário Desconhecido (ID: {user_id})"
    
    def load_and_filter_questions(self):
        filtered_questions_list = []
        for q in QUESTIONS:
            match_discipline = True
            match_theme = True

            if self.discipline_filter is not None:
                match_discipline = (q["discipline"] == self.discipline_filter)

            if self.theme_filter is not None:
                match_theme = (q["theme"] == self.theme_filter)

            if match_discipline and match_theme:
                filtered_questions_list.append(q)
        
        random.shuffle(filtered_questions_list) 
        return filtered_questions_list

    def get_next_question(self):
        for q in self.available_questions:
            if q["id"] not in self.used_questions_ids:
                self.used_questions_ids.add(q["id"]) 
                return q
        return None 

    def start_new_round(self):
        self.current_round += 1
        self.questions_answered_in_round = 0
        self.update_score_display() 
        
        if hasattr(self.ui, 'labelTurn'): 
            self.ui.labelTurn.setText(f"RODADA {self.current_round} DE {self.num_rounds}")
        else:
            print(f"Rodada {self.current_round} de {self.num_rounds}")


    def display_question(self):
        for label in self.alternative_labels.values():
            label.setStyleSheet("")
        self.alternatives_group.setExclusive(False)
        for radio_button in self.alternatives_group.buttons():
            radio_button.setChecked(False)
            radio_button.setEnabled(True) 
        self.alternatives_group.setExclusive(True)
        self.ui.button_ConfirmAnswer.setEnabled(True)

        current_question_data = self.get_next_question()

        if current_question_data:
            self.current_question = current_question_data 
            
            if hasattr(self.ui, 'themeLabel'):
                self.ui.themeLabel.setText(f"Tema: {self.current_question['theme']}")
            
            self.ui.label_2.setText(self.current_question["question_text"])

            self.ui.label.setText(f"A) {self.current_question['alternatives']['A']}")
            self.ui.label_5.setText(f"B) {self.current_question['alternatives']['B']}")
            self.ui.label_4.setText(f"C) {self.current_question['alternatives']['C']}")
            self.ui.label_6.setText(f"D) {self.current_question['alternatives']['D']}")
            self.ui.label_7.setText(f"E) {self.current_question['alternatives']['E']}")
            
            self.time_left_in_seconds = self.time_per_question
            self.update_timer_display()
            self.timer.start(1000) 
            
            self.highlight_current_player()

        else:
            QMessageBox.information(self, "Fim das Questões", "Não há mais questões disponíveis. A batalha será finalizada.")
            self.finalize_battle()


    def highlight_current_player(self):
        if self.current_player_turn == self.player1_id:
            self.ui.player1Label.setStyleSheet("font-weight: bold; color: blue; font-size: 20px;") 
            self.ui.player2Label.setStyleSheet("font-weight: normal; color: black; font-size: 16px;") 
        else:
            self.ui.player1Label.setStyleSheet("font-weight: normal; color: black; font-size: 16px;")
            self.ui.player2Label.setStyleSheet("font-weight: bold; color: red; font-size: 20px;")

    def update_timer_display(self):
        minutes = self.time_left_in_seconds // 60
        seconds = self.time_left_in_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}" 
        
        if hasattr(self.ui, 'labelTimer'): 
            self.ui.labelTimer.setText(time_str)
            if self.time_left_in_seconds <= 10:
                self.ui.labelTimer.setStyleSheet("color: red; font-weight: bold;")
            elif self.time_left_in_seconds <= 20: 
                self.ui.labelTimer.setStyleSheet("color: orange; font-weight: bold;")
            else:
                self.ui.labelTimer.setStyleSheet("color: black; font-weight: bold;") 

    def handle_timeout(self):
        self.time_left_in_seconds -= 1
        self.update_timer_display()

        if self.time_left_in_seconds <= 0:
            self.timer.stop()
            QMessageBox.information(self, "Tempo Esgotado!", f"Tempo esgotado para {self.get_user_name_by_id(self.current_player_turn).upper()}!")
            self.process_answer(selected_alternative=None, is_timeout=True) 

    def get_alternative_letter_from_id(self, rb_id):
        mapping = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E"}
        return mapping.get(rb_id)

    def get_selected_alternative(self):
        selected_button = self.alternatives_group.checkedButton()
        if selected_button:
            return self.get_alternative_letter_from_id(self.alternatives_group.id(selected_button))
        return None

    def confirm_answer(self):
        selected_alternative = self.get_selected_alternative()
        if selected_alternative is None:
            QMessageBox.warning(self, "Atenção", "Por favor, selecione uma alternativa antes de confirmar.")
            return

        self.timer.stop() 
        self.process_answer(selected_alternative)

    def process_answer(self, selected_alternative, is_timeout=False):
        is_correct = False
        if not is_timeout and selected_alternative is not None:
            is_correct = (selected_alternative == self.current_question["correct_answer"])

        self.update_user_statistics(
            user_id=self.current_player_turn,
            discipline_name=self.current_question["discipline"],
            theme_name=self.current_question["theme"],
            is_correct=is_correct
        )

        if is_correct:
            self.player_scores[self.current_player_turn] += 1
            selected_label = self.alternative_labels.get(self.alternatives_group.id(self.alternatives_group.checkedButton()))
            if selected_label:
                selected_label.setStyleSheet("background-color: #C8FFC8; border: 1px solid green;")
            QMessageBox.information(self, "Resposta Correta!", "Ponto para você!")
        else:
            if not is_timeout: 
                selected_label = self.alternative_labels.get(self.alternatives_group.id(self.alternatives_group.checkedButton()))
                if selected_label:
                    selected_label.setStyleSheet("background-color: #FFC8C8; border: 1px solid red;")

            correct_answer_letter = self.current_question["correct_answer"]
            correct_label = self.alternative_labels_by_letter.get(correct_answer_letter)
            if correct_label:
                correct_label.setStyleSheet("background-color: #C8FFC8; border: 1px solid green; font-weight: bold;")
            
            QMessageBox.warning(self, "Resposta Incorreta!", f"A resposta correta era: {correct_answer_letter}.")
        
        for radio_button in self.alternatives_group.buttons():
            radio_button.setEnabled(False)
        self.ui.button_ConfirmAnswer.setEnabled(False)

        self.questions_answered_in_round += 1
        self.update_score_display()

        if self.questions_answered_in_round == 2:
            if self.current_round < self.num_rounds:
                self.start_new_round()
            else:
                self.finalize_battle() 
                return 

        self.current_player_turn = self.player2_id if self.current_player_turn == self.player1_id else self.player1_id
        
        QtCore.QTimer.singleShot(1500, self.display_question) 

    def update_score_display(self):
        self.ui.P1Score.setText(str(self.player_scores[self.player1_id]))
        self.ui.P1Score_2.setText(str(self.player_scores[self.player2_id])) 

    def finalize_battle(self):
        self.timer.stop() 

        p1_score = self.player_scores[self.player1_id]
        p2_score = self.player_scores[self.player2_id]

        winner_message = ""
        if p1_score > p2_score:
            winner_message = f"O VENCEDOR É: {self.player1_name.upper()}!"
        elif p2_score > p1_score:
            winner_message = f"O VENCEDOR É: {self.player2_name.upper()}!"
        else:
            winner_message = "A BATALHA TERMINOU EM EMPATE!"
        
        final_summary = (
            f"Batalha Finalizada!\n\n"
            f"Placar Final:\n"
            f"{self.player1_name}: {p1_score} pontos\n"
            f"{self.player2_name}: {p2_score} pontos\n\n"
            f"{winner_message}"
        )
        QMessageBox.information(self, "Fim da Batalha!", final_summary)

        self.close_battle_window() 

    def close_battle_window(self):
        self.timer.stop() 
        self.hide()
        if self.parent_menu:
            self.parent_menu.show()

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
