from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
from gui.questions_window import QuestionsWindow
from gui.admin_window import AdminWindow
from gui.ranking_window import RankingWindow
from gui.filter_questions_dialog import FilterQuestionsDialog
from gui.ui_forms.Ui_MainMenuWindow import Ui_MainMenuWindow
from gui.battle_window import BattleWindow
from gui.login_dialog import LoginDialog
from gui.battle_config_dialog import BattleConfigDialog
from gui.statistics_window import StatisticsWindow

class MainMenuWindow(QtWidgets.QMainWindow):
    def __init__(self, user_role="user", user_id=None, parent_login_window=None):
        super().__init__()
        self.ui = Ui_MainMenuWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Menu Principal")
        
        self.questions_window = None
        self.admin_window = None
        self.ranking_window = None
        self.battle_window = None
        self.statistics_window = None
        
        self.current_user_id = user_id
        self.parent_login_window = parent_login_window

        self.setFixedSize(self.width(), self.height())

        self.ui.button_Questions.clicked.connect(lambda: self.open_questions_window(is_simulado=False))
        self.ui.pushButton_Simulated.clicked.connect(lambda: self.open_questions_window(is_simulado=True))
        self.ui.button_Ranking.clicked.connect(self.open_ranking_window)
        self.ui.button_Exit.clicked.connect(self.quit_main_menu)
        
        if hasattr(self.ui, 'button_statistic'):
            self.ui.button_statistic.clicked.connect(self.open_statistics_window)
        else:
            print("Atenção: 'button_statistic' não encontrado na UI do MainMenuWindow. Certifique-se de adicioná-lo no Qt Designer.")
        
        if hasattr(self.ui, 'button_battle'): 
            self.ui.button_battle.clicked.connect(self.open_battle_window)
        else:
            print("Atenção: 'button_battle' não encontrado na UI do MainMenuWindow. Certifique-se de adicioná-lo no Qt Designer.")

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
            QtWidgets.QApplication.quit()

    def open_ranking_window(self):
        self.ranking_window = RankingWindow(parent=self)
        self.hide()
        self.ranking_window.show()
    
    def open_questions_window(self, is_simulado):
        filter_dialog = FilterQuestionsDialog(is_simulado=is_simulado, parent=self)

        if filter_dialog.exec_() == QtWidgets.QDialog.Accepted:
            discipline_filter, theme_filter, num_questions, random_order, selected_time_minutes = filter_dialog.get_filters()

            self.questions_window = QuestionsWindow(
                user_id=self.current_user_id,
                discipline_filter=discipline_filter,
                theme_filter=theme_filter,
                num_questions=num_questions,
                random_order=random_order, 
                selected_time_minutes=selected_time_minutes,
                is_simulado_param=is_simulado,
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
        
    def open_battle_window(self):
        login_dialog_player2 = LoginDialog(title="Login do Jogador 2", parent=self)
        
        if login_dialog_player2.exec_() == QtWidgets.QDialog.Accepted:
            player2_id, player2_role = login_dialog_player2.get_credentials()
            
            if player2_id is not None:
                if player2_id == self.current_user_id:
                    QMessageBox.warning(self, "Erro na Batalha", "O Jogador 2 não pode ser o mesmo que o Jogador 1. Por favor, use outra conta.")
                    return

                config_dialog = BattleConfigDialog(parent=self)
                if config_dialog.exec_() == QtWidgets.QDialog.Accepted:
                    battle_settings = config_dialog.get_battle_config()
                    
                    self.battle_window = BattleWindow(
                        player1_id=self.current_user_id,
                        player2_id=player2_id,
                        battle_settings=battle_settings,
                        parent=self
                    )
                    self.hide()
                    self.battle_window.show()
                else:
                    QMessageBox.information(self, "Batalha Cancelada", "Configuração da batalha cancelada. Retornando ao menu principal.")
            else:
                QMessageBox.warning(self, "Login Necessário", "O Jogador 2 precisa fazer login para iniciar a batalha.")
        else:
            QMessageBox.information(self, "Batalha Cancelada", "Login do Jogador 2 cancelado. Retornando ao menu principal.")

    def open_statistics_window(self):
        if self.current_user_id:
            if self.statistics_window is None:
                self.statistics_window = StatisticsWindow(user_id=self.current_user_id, parent=self)
            
            self.statistics_window.load_and_plot_statistics() 
            self.hide()
            self.statistics_window.show()
        else:
            QMessageBox.warning(self, "Erro de Usuário", "Não foi possível obter o ID do usuário para exibir as estatísticas.")