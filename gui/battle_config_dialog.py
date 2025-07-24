from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QComboBox, QCheckBox, QPushButton, QMessageBox
from utils.json_manager import QUESTIONS

class BattleConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Batalha")
        self.setFixedSize(400, 400)

        self.num_rounds = 5
        self.time_per_question = 30
        self.use_game_cards = False
        self.selected_discipline = None
        self.selected_theme = None

        self.init_ui()
        self.populate_disciplines_and_themes()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        basic_config_group = QtWidgets.QGroupBox("Configurações da Partida")
        basic_config_layout = QVBoxLayout()

        rounds_layout = QHBoxLayout()
        rounds_label = QLabel("Nº de Rodadas (perguntas):")
        self.spinBox_rounds = QSpinBox()
        self.spinBox_rounds.setMinimum(1)
        self.spinBox_rounds.setMaximum(20)
        self.spinBox_rounds.setValue(self.num_rounds)
        rounds_layout.addWidget(rounds_label)
        rounds_layout.addStretch()
        rounds_layout.addWidget(self.spinBox_rounds)
        basic_config_layout.addLayout(rounds_layout)

        time_layout = QHBoxLayout()
        time_label = QLabel("Tempo por Pergunta (segundos):")
        self.combo_time = QComboBox()
        self.time_options = ["30", "45", "60", "90", "120"]
        self.combo_time.addItems(self.time_options)
        self.combo_time.setCurrentText(str(self.time_per_question))
        time_layout.addWidget(time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.combo_time)
        basic_config_layout.addLayout(time_layout)

        basic_config_group.setLayout(basic_config_layout)
        main_layout.addWidget(basic_config_group)

        options_group = QtWidgets.QGroupBox("Opções de Jogo")
        options_layout = QVBoxLayout()

        self.checkbox_cards = QCheckBox("Usar Cartas de Jogo (Habilidades)")
        self.checkbox_cards.setChecked(self.use_game_cards)
        options_layout.addWidget(self.checkbox_cards)

        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        filter_group = QtWidgets.QGroupBox("Filtro de Questões")
        filter_layout = QVBoxLayout()

        discipline_layout = QHBoxLayout()
        discipline_label = QLabel("Disciplina:")
        self.combo_discipline = QComboBox(self)
        discipline_layout.addWidget(discipline_label)
        discipline_layout.addWidget(self.combo_discipline)
        filter_layout.addLayout(discipline_layout)

        theme_layout = QHBoxLayout()
        theme_label = QLabel("Tema:")
        self.combo_theme = QComboBox(self)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.combo_theme)
        filter_layout.addLayout(theme_layout)

        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)

        main_layout.addStretch()

        buttons_layout = QHBoxLayout()
        self.button_start = QPushButton("Iniciar Batalha")
        self.button_cancel = QPushButton("Cancelar")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.button_start)
        buttons_layout.addWidget(self.button_cancel)
        main_layout.addLayout(buttons_layout)

        self.button_start.clicked.connect(self.accept_config)
        self.button_cancel.clicked.connect(self.reject)
        self.combo_discipline.currentIndexChanged.connect(self.populate_themes)

        self.setLayout(main_layout) 

    def populate_disciplines_and_themes(self):
        self.combo_discipline.clear()
        self.combo_discipline.addItem("Todas as Disciplinas")
        
        if QUESTIONS:
            disciplines = sorted(list(set(q["discipline"] for q in QUESTIONS)))
            self.combo_discipline.addItems(disciplines)
        
        self.populate_themes()

    def populate_themes(self):
        self.combo_theme.clear()
        self.combo_theme.addItem("Todos os Temas")
        
        selected_discipline = self.combo_discipline.currentText()
        themes = set()
        
        if QUESTIONS:
            if selected_discipline == "Todas as Disciplinas":
                for q in QUESTIONS:
                    themes.add(q["theme"])
            else:
                for q in QUESTIONS:
                    if q["discipline"] == selected_discipline:
                        themes.add(q["theme"])
        
        sorted_themes = sorted(list(themes))
        self.combo_theme.addItems(sorted_themes)


    def accept_config(self):
        try:
            self.num_rounds = self.spinBox_rounds.value()
            self.time_per_question = int(self.combo_time.currentText())
            self.use_game_cards = self.checkbox_cards.isChecked()
            self.selected_discipline = self.combo_discipline.currentText() if self.combo_discipline.currentText() != "Todas as Disciplinas" else None
            self.selected_theme = self.combo_theme.currentText() if self.combo_theme.currentText() != "Todos os Temas" else None
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Erro de Configuração", "Por favor, verifique os valores inseridos para o tempo por pergunta.")

    def get_battle_config(self):
        return {
            "num_rounds": self.num_rounds,
            "time_per_question": self.time_per_question,
            "use_game_cards": self.use_game_cards,
            "discipline_filter": self.selected_discipline,
            "theme_filter": self.selected_theme
        }