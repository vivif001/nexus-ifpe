from PyQt5 import QtWidgets, QtCore
from utils.json_manager import USERS, USER_STATS
from gui.ui_forms.Ui_RankingWindow import Ui_RankingWindow 

class RankingWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_RankingWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Ranking de Usuários")

        self.setFixedSize(self.width(), self.height())

        self.ui.button_Exit.clicked.connect(self.back_to_main_menu)
        self.load_ranking_data()

    def load_ranking_data(self):
        ranked_users = []
        for user_stat in USER_STATS:
            user_id = str(user_stat["user_id"])
            user_info = next((u for u in USERS if str(u["id"]) == user_id), None)
            
            if user_info:
                full_name = f"{user_info.get('firstName', '')} {user_info.get('lastName', '')}"
                correct_percentage = user_stat.get("correct_percentage", 0.0)
                total_answered = user_stat.get("total_questions_answered", 0)
                
                if total_answered > 0:
                    ranked_users.append({
                        "full_name": full_name,
                        "correct_percentage": correct_percentage,
                        "total_answered": total_answered
                    })
        
        ranked_users.sort(key=lambda x: (x["correct_percentage"], x["total_answered"]), reverse=True)

        ranking_labels = [
            self.ui.labelName_position1,
            self.ui.labelName_position2,
            self.ui.labelName_position3,
            self.ui.labelName_Position4,
            self.ui.labelName_Position5,
            self.ui.labelName_Position6,
            self.ui.labelName_Position7,
            self.ui.labelName_Position8
        ]

        for i, user in enumerate(ranked_users):
            if i < len(ranking_labels):
                label = ranking_labels[i]
                label.setText(f"{user['full_name']} - {user['correct_percentage']:.2f}%")
                label.setAlignment(QtCore.Qt.AlignCenter)
            else:
                break 

        for i in range(len(ranked_users), len(ranking_labels)):
            ranking_labels[i].clear()
            
        self.ui.label_gold.show()
        self.ui.label_silver.show()
        self.ui.label_bronze.show()
        self.ui.gold_medal.show()
        self.ui.silver_medal.show()
        self.ui.bronze_medal.show()


    def back_to_main_menu(self):
        self.hide()
        if self.parent():
            self.parent().show()
        else:
            print("Erro: Não há janela pai para retornar. Voltando ao Login.")
            from gui.login_window import LoginWindow
            login_window = LoginWindow()
            login_window.show()