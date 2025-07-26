import json
import os
from PyQt5.QtWidgets import QMessageBox

json_users_path = os.path.join('data', 'users.json')
json_questions_path = os.path.join('data', 'questions.json')
json_user_stats_path = os.path.join('data', 'user_stats.json')
json_game_cards_path = os.path.join('data', 'game_cards.json')

def load_json_data(file_path):
    try:
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            initial_data = []
            if file_path == json_game_cards_path:
                print(f"Arquivo '{file_path}' não encontrado. Criado como JSON de cartas vazio.")
                pass
            else:
                print(f"Arquivo '{file_path}' não encontrado. Criado como JSON vazio.")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=4)
            return initial_data
            
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
_GAME_CARDS_LIST = load_json_data(json_game_cards_path)
GAME_CARDS = {card["id"]: card for card in _GAME_CARDS_LIST}