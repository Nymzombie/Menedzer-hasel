import tkinter as tk
from tkinter import messagebox
import json
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import os
import logging

DATABASE_PATH = "DATA/database.json"
EMAIL_USER = "databaseemailsender@gmail.com"
EMAIL_PASSWORD = "fmxi rfki ksed mful"

# Zmienna przechowująca tymczasowe dane użytkownika
temp_user_data = {'username': None, 'email': None, 'password': None, 'activation_code': None}

# Tworzenie okna rejestracji i jego konfiguracja
def create_registration_window(root):
    global registration_window, username_reg_entry, email_reg_entry, password_reg_entry

    registration_window = tk.Toplevel(root)
    registration_window.title("Rejestracja")
    registration_window.geometry("300x250")
    registration_window.resizable(False, False)

    # Funkcja wywoływana przy zamknięciu okna rejestracji
    def on_closing_registration_window():
        registration_window.destroy()  # Zamknij okno rejestracji
        root.deiconify()  # Pokaż ponownie okno logowania

    registration_window.protocol("WM_DELETE_WINDOW", on_closing_registration_window)

    # Tworzenie i konfiguracja widżetów w oknie rejestracji
    username_label = tk.Label(registration_window, text="Login:")
    username_label.pack(pady=(10, 0))
    username_reg_entry = tk.Entry(registration_window, width=20)
    username_reg_entry.pack()

    email_label = tk.Label(registration_window, text="E-mail:")
    email_label.pack(pady=(10, 0))
    email_reg_entry = tk.Entry(registration_window, width=20)
    email_reg_entry.pack()

    password_label = tk.Label(registration_window, text="Hasło:")
    password_label.pack(pady=(10, 0))
    password_reg_entry = tk.Entry(registration_window, width=20, show="*")
    password_reg_entry.pack()

    confirm_reg_button = tk.Button(registration_window, text="Zarejestruj i wyślij kod", command=lambda: register_and_send_code(root))
    confirm_reg_button.pack(pady=(10, 0))

    return_button = tk.Button(registration_window, text="Powrót do logowania", command=lambda: close_registration_window(root))
    return_button.pack(side=tk.BOTTOM, pady=10, anchor='s')


# Funkcja do tworzenia okna aktywacji
def create_activation_window(root):
    activation_window = tk.Toplevel(root)
    activation_window.title("Aktywacja Konta")
    activation_window.geometry("300x100")
    activation_window.withdraw()

    activation_code_entry = tk.Entry(activation_window, width=6)
    activation_code_entry.place(x=200, y=10)

    password_label = tk.Label(activation_window, text="Kod wyslany na adres e-mail:")
    password_label.place(x=30, y=10)

    confirm_activation_button = tk.Button(activation_window, text="Aktywuj konto", width=20,
                                          command=lambda: verify_activation_code(activation_code_entry.get(),
                                                                                 registration_window,
                                                                                 activation_window, root))
    confirm_activation_button.place(x=140, y=40)

    return activation_window


# Funkcje obsługujące otwieranie i zamykanie okna rejestracji
def open_registration_window(root):
    global is_root_hidden
    is_root_hidden = True
    create_registration_window(root)
    root.withdraw()

# Funkcja do rejestracji i wysyłania kodu aktywacyjnego
def register_and_send_code(root):
    global temp_user_data

    username = username_reg_entry.get()
    email = email_reg_entry.get().strip()
    password = password_reg_entry.get()

    temp_user_data['username'] = username
    temp_user_data['email'] = email
    temp_user_data['password'] = password
    temp_user_data['activation_code'] = random.randint(100000, 999999)

    send_email(email, temp_user_data['activation_code'])
    open_activation_window(root)

# Funkcja do wysyłania e-maila z kodem aktywacyjnym
def send_email(to_email, code):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = "Kod weryfikacyjny"
        msg.attach(MIMEText(f"Twój kod weryfikacyjny to: {code}", 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email został wysłany, kod: {code}")
    except Exception as e:
        print(f'Coś poszło nie tak: {repr(e)}')

# Funkcja do weryfikacji kodu aktywacyjnego
def verify_activation_code(user_code, registration_window, activation_window, root):
    global temp_user_data

    if str(user_code) == str(temp_user_data['activation_code']):
        save_user_to_database(temp_user_data['username'], temp_user_data['email'], temp_user_data['password'])
        temp_user_data = {'username': None, 'email': None, 'password': None, 'activation_code': None}

        messagebox.showinfo("Aktywacja", "Konto zostało pomyślnie aktywowane.")
        activation_window.destroy()
        registration_window.destroy()
        root.deiconify()
    else:
        messagebox.showerror("Aktywacja", "Nieprawidłowy kod aktywacyjny.")

# Funkcja do zapisu nowego użytkownika w bazie danych
def save_user_to_database(username, email, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if not os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, 'w') as db_file:
            json.dump({"users": []}, db_file, indent=4)
    with open(DATABASE_PATH, 'r') as db_file:
        db = json.load(db_file)
    new_user = {"username": username, "email": email, "password": hashed_password, "sites": []}
    db['users'].append(new_user)
    with open(DATABASE_PATH, 'w') as db_file:
        json.dump(db, db_file, indent=4)

def close_registration_window(root):
    global is_root_hidden
    if is_root_hidden:
        root.deiconify()
        is_root_hidden = False
    registration_window.destroy()

# Funkcja do otwierania okna aktywacji
def open_activation_window(root):
    global activation_window
    activation_window = None
    if not activation_window or not activation_window.winfo_exists():
        activation_window = create_activation_window(root)
    activation_window.deiconify()

# Funkcja wywoływana po pomyślnej rejestracji
def on_successful_registration(root):
    close_registration_window(root)
