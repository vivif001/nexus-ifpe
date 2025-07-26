import json
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

STATISTICS_FILE_PATH = 'data/user_stats.json' 

class StatisticsWindow(QtWidgets.QMainWindow):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle(f"Estatísticas do Usuário")
        self.setGeometry(100, 100, 900, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.load_and_plot_statistics()

    def load_user_statistics(self):
        try:
            with open(STATISTICS_FILE_PATH, 'r', encoding='utf-8') as f:
                all_stats = json.load(f)
            for user_stats in all_stats:
                if user_stats.get("user_id") == self.user_id:
                    return user_stats
            return None
        except FileNotFoundError:
            QMessageBox.critical(self, "Erro de Arquivo", f"Arquivo de estatísticas não encontrado: {STATISTICS_FILE_PATH}")
            return None
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Erro de Leitura", f"Erro ao decodificar o arquivo JSON: {STATISTICS_FILE_PATH}. Verifique a sintaxe.")
            return None
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao carregar as estatísticas: {e}")
            return None

    def plot_discipline_performance(self, discipline_data):
        if not discipline_data:
            QMessageBox.information(self, "Sem Dados", "Não há dados de disciplinas para exibir gráficos.")
            return

        disciplines = []
        correct_percentages = []

        for discipline_name, data in discipline_data.items():
            total_answered = data.get("total_answered", 0)
            total_correct = data.get("total_correct", 0)

            if total_answered > 0:
                percentage = (total_correct / total_answered) * 100
                disciplines.append(discipline_name.replace('_', ' ').title()) 
                correct_percentages.append(percentage)

        if not disciplines:
            QMessageBox.information(self, "Sem Dados", "Não há dados válidos de disciplinas para gerar o gráfico.")
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        bars = ax.bar(disciplines, correct_percentages, color='skyblue')
        
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{round(yval, 2)}%', ha='center', va='bottom')

        ax.set_title("Desempenho por Disciplina (%)", y=1.05)
        ax.set_xlabel("Disciplinas")
        ax.set_ylabel("Porcentagem de Acertos (%)")
        ax.set_ylim(0, 100)
        self.figure.autofmt_xdate(rotation=45, ha='right')
        self.canvas.draw()

    def load_and_plot_statistics(self):
        user_stats = self.load_user_statistics()
        if user_stats and "disciplines" in user_stats:
            self.plot_discipline_performance(user_stats["disciplines"])
        else:
            QMessageBox.information(self, "Dados Ausentes", "Não foi possível encontrar dados de disciplinas para este usuário.")