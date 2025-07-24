from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox

from utils.json_manager import QUESTIONS

class FilterQuestionsDialog(QtWidgets.QDialog):
    def __init__(self, is_simulado=False, parent=None):
        super().__init__(parent)
        self.is_simulado = is_simulado
        if self.is_simulado:
            self.setWindowTitle("Configurar Simulado")
            self.setFixedSize(400, 350)
        else:
            self.setWindowTitle("Filtrar Questões para Prática")
            self.setFixedSize(350, 250)

        self.selected_discipline = None
        self.selected_theme = None
        self.num_questions = 0
        self.random_order = True
        self.selected_time_minutes = 0

        self.layout = QtWidgets.QVBoxLayout(self)

        self.discipline_label = QtWidgets.QLabel("Selecione a Disciplina:")
        self.combo_Discipline = QtWidgets.QComboBox(self)
        self.layout.addWidget(self.discipline_label)
        self.layout.addWidget(self.combo_Discipline)

        self.theme_label = QtWidgets.QLabel("Selecione o Tema:")
        self.combo_Theme = QtWidgets.QComboBox(self)
        self.layout.addWidget(self.theme_label)
        self.layout.addWidget(self.combo_Theme)
        
        self.num_questions_label = QtWidgets.QLabel("Número de Questões (0 para todas):")
        self.spinBox_NumQuestions = QtWidgets.QSpinBox(self)
        self.spinBox_NumQuestions.setMinimum(0)
        self.spinBox_NumQuestions.setMaximum(len(QUESTIONS))
        self.spinBox_NumQuestions.setValue(0)
        
        self.time_label = QtWidgets.QLabel("Tempo do Simulado (minutos):")
        self.combo_Time = QtWidgets.QComboBox(self)
        self.time_options = ["15", "30", "45", "60", "90", "180"]
        self.combo_Time.addItems(self.time_options)
        self.combo_Time.setCurrentText("60")

        self.layout.addWidget(self.time_label)
        self.layout.addWidget(self.combo_Time)

        self.layout.addWidget(self.num_questions_label)
        self.layout.addWidget(self.spinBox_NumQuestions)

        if not self.is_simulado:
            self.num_questions_label.hide()
            self.spinBox_NumQuestions.hide()
            self.time_label.hide() 
            self.combo_Time.hide()

        self.layout.addStretch()

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.button_StartQuiz = QtWidgets.QPushButton("Iniciar Simulado" if self.is_simulado else "Iniciar Prática", self)
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

        if self.is_simulado:
            self.num_questions = self.spinBox_NumQuestions.value()
            self.random_order = True
            try: 
                self.selected_time_minutes = int(self.combo_Time.currentText())
            except ValueError:
                self.selected_time_minutes = 60
                QMessageBox.warning(self, "Erro de Tempo", "Tempo inválido selecionado. Usando 60 minutos como padrão.")
        else: 
            self.num_questions = 0 
            self.random_order = True
            self.selected_time_minutes = 0

        self.accept()

    def get_filters(self):
        return self.selected_discipline, self.selected_theme, self.num_questions, self.random_order, self.selected_time_minutes