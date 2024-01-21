import tkinter as tk
from tkinter import messagebox
import json
import hashlib
import user_interface

DATABASE_PATH = "DATA/database.json"

def on_login(root, login_entry, password_entry, user_interface_module):
    username = login_entry.get()
    password = password_entry.get()

    if verify_login(username, password):
        messagebox.showinfo("Sukces", "Zalogowano pomyślnie.")
        user_password = password  # Zmienna do przechowywania hasła użytkownika
        user_interface_module.open_user_interface(root, username, user_password)
    else:
        messagebox.showerror("Błąd", "Niepoprawny login lub hasło.")

def verify_login(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    with open(DATABASE_PATH, 'r') as db_file:
        db = json.load(db_file)
        for user in db['users']:
            if user['username'] == username and user['password'] == hashed_password:
                return True
        return False
