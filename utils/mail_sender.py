import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from PyQt5.QtWidgets import QMessageBox
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT")) if os.getenv("SMTP_PORT") else 587 #
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

if not SENDER_EMAIL or not SENDER_PASSWORD or not SMTP_SERVER:
    QMessageBox.critical(None, "Erro de Configuração",
                         "As credenciais de e-mail (SENDER_EMAIL, SENDER_PASSWORD, SMTP_SERVER) não foram definidas no arquivo .env ou nas variáveis de ambiente.")

def send_new_user_email(receiver_email, first_name, last_name, username, password):
    if not SENDER_EMAIL or not SENDER_PASSWORD or not SMTP_SERVER:
        print("Não foi possível enviar o e-mail: credenciais ou servidor ausentes.")
        return False

    subject = "Suas Credenciais de Acesso - Nexus-IFPE"
    body = f"""
    Olá, {first_name}!

    Bem-vindo(a) ao Sistema de Questões Nexus-IFPE.

    Suas credenciais de acesso são:

    Usuário: {username}
    Senha: {password}

    Recomendamos que altere sua senha no primeiro acesso.

    Atenciosamente,
    Equipe Nexus-IFPE
    """

    msg = MIMEMultipart()
    msg['From'] = f"Nexus-IFPE <{SENDER_EMAIL}>"
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"E-mail enviado com sucesso para {receiver_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"Erro de autenticação SMTP: {e}. Verifique suas credenciais.")
        QMessageBox.critical(None, "Erro de E-mail", f"Erro de autenticação ao enviar e-mail: {e}.")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"Erro de conexão SMTP: {e}. Verifique o servidor e a porta.")
        QMessageBox.critical(None, "Erro de E-mail", f"Erro de conexão ao servidor de e-mail: {e}.")
        return False
    except Exception as e:
        print(f"Erro inesperado ao enviar e-mail: {e}")
        QMessageBox.critical(None, "Erro de E-mail", f"Erro inesperado ao enviar e-mail: {e}")
        return False