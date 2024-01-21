import tkinter as tk
from tkinter import messagebox
import json
import hashlib
from datetime import datetime
import pyperclip

import binascii
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from os import urandom

DATABASE_PATH = "DATA/database.json"

# Funkcje szyfrowania i deszyfrowania AES
def get_aes_key(key):
    return hashlib.sha256(key.encode()).digest()

def encrypt_aes(input_string, key):
    # Funkcja szyfrująca dane wejściowe przy użyciu AES
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(input_string.encode()) + padder.finalize()
    aes_key = get_aes_key(key)
    iv = urandom(16)
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    encrypted_data = iv + encrypted
    return base64.b64encode(encrypted_data).decode()

def decrypt_aes(encrypted_data, key):
    # Funkcja deszyfrująca dane wejściowe przy użyciu AES
    try:
        encrypted_data = base64.b64decode(encrypted_data)
    except binascii.Error:
        print("Błąd dekodowania Base64")
        return ""
    iv = encrypted_data[:16]
    encrypted = encrypted_data[16:]
    aes_key = get_aes_key(key)
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
    return decrypted.decode()

# Funkcje pomocnicze interfejsu użytkownika
def update_time_label(time_label):
    # Aktualizuje etykietę z aktualną godziną co sekundę
    current_time = datetime.now().strftime("%D, %H:%M:%S")
    time_label.config(text=f"Aktualny czas: {current_time}")
    time_label.after(1000, lambda: update_time_label(time_label))

def copy_to_clipboard(decrypted_data, root):
    # Kopiuje dane do schowka i czyści schowek po 5 sekundach
    pyperclip.copy(decrypted_data)
    root.after(5000, lambda: pyperclip.copy(""))

# Funkcja do otwierania interfejsu użytkownika po zalogowaniu
def open_user_interface(root, username, user_password):
    root.withdraw()
    user_window = tk.Toplevel(root)
    user_window.title(f"Menedżer haseł - {username}")
    user_window.geometry("350x150")
    user_window.protocol("WM_DELETE_WINDOW", lambda: on_closing_user_interface(root, user_window))

    user_window.lock_icon = tk.PhotoImage(file="DATA/graphics/lock_icon.png")
    lock_label = tk.Label(user_window, image=user_window.lock_icon)
    lock_label.place(x=0, y=20)

    time_label = tk.Label(user_window, text="")
    time_label.place(x=150, y=130)
    update_time_label(time_label)

    welcome_label = tk.Label(user_window, text=f"Zalogowany użytkownik: {username}", font=("Helvetica", 13))
    welcome_label.place(x=0, y=0, )

    logout_button = tk.Button(user_window, text="Wyloguj", command=lambda: logout(user_window, root), height=1, width=15)
    logout_button.place(x=235, y=85, )

    add_site_button = tk.Button(user_window, text="Dodaj stronę", command=lambda: add_new_site(user_window, username, user_password), height=1, width=15)
    add_site_button.place(x=235, y=55, )

    view_sites_button = tk.Button(user_window, text="Pokaż strony", command=lambda: view_sites(user_window, username, user_password, root), height=1, width=15)
    view_sites_button.place(x=235, y=25, )


# Funkcja wywoływana przy zamknięciu okna użytkownika
def on_closing_user_interface(root, user_window):
    user_window.destroy()
    root.deiconify()


def logout(user_window, root):
    global user_password
    user_password = None  # Wyczyszczenie hasła użytkownika
    user_window.destroy()
    root.deiconify()


def add_new_site(user_window, username, user_password):
    new_site_window = tk.Toplevel(user_window)
    new_site_window.title("Dodaj nową stronę")
    new_site_window.geometry("300x200")

    site_name_label = tk.Label(new_site_window, text="Nazwa strony:")
    site_name_label.pack()
    site_name_entry = tk.Entry(new_site_window)
    site_name_entry.pack()

    site_login_label = tk.Label(new_site_window, text="Login/E-mail:")
    site_login_label.pack()
    site_login_entry = tk.Entry(new_site_window)
    site_login_entry.pack()

    site_password_label = tk.Label(new_site_window, text="Hasło:")
    site_password_label.pack()
    site_password_entry = tk.Entry(new_site_window, show="*")
    site_password_entry.pack()

    save_button = tk.Button(new_site_window, text="Zapisz",
                            command=lambda: save_site_data(username, site_name_entry.get(), site_login_entry.get(),
                                                           site_password_entry.get(), user_password, new_site_window))
    save_button.pack()


def save_site_data(username, site_name, site_login, site_password, user_password, new_site_window):
    hashed_password = hashlib.sha256(site_password.encode()).hexdigest()
    with open(DATABASE_PATH, 'r+') as db_file:
        db = json.load(db_file)
        for user in db['users']:
            if user['username'] == username:
                user['sites'].append({'site': site_name, 'login': encrypt_aes(site_login, user_password), 'password': encrypt_aes(site_password, user_password)})
                break
        db_file.seek(0)
        json.dump(db, db_file, indent=4)
        db_file.truncate()
    new_site_window.destroy()
    messagebox.showinfo("Sukces", "Strona została dodana.")

def remove_site(username, site_name, user_window, user_password, root):
    with open(DATABASE_PATH, 'r+') as db_file:
        db = json.load(db_file)
        for user in db['users']:
            if user['username'] == username:
                user['sites'] = [site for site in user['sites'] if site['site'] != site_name]
                break
        db_file.seek(0)
        json.dump(db, db_file, indent=4)
        db_file.truncate()
    view_sites(user_window, username, user_password, root)  # Odświeżanie listy stron w istniejącym oknie


def view_sites(user_window, username, user_password, root):
    global view_sites_window
    if 'view_sites_window' in globals() and view_sites_window.winfo_exists():
        for widget in view_sites_window.winfo_children():
            widget.destroy()
    else:
        view_sites_window = tk.Toplevel(user_window)
        view_sites_window.title("Twoje strony")
        view_sites_window.geometry("400x300")

    with open(DATABASE_PATH, 'r') as db_file:
        db = json.load(db_file)
        for user in db['users']:
            if user['username'] == username:
                for site in user['sites']:
                    site_frame = tk.Frame(view_sites_window)
                    site_frame.pack(fill=tk.X)
                    tk.Label(site_frame, text=f"{site['site']}:", width=20, anchor="w").pack(side=tk.LEFT)
                    login_button = tk.Button(site_frame, text="Login",
                                             command=lambda site_login=site['login']: copy_to_clipboard(decrypt_aes(site_login, user_password), root))
                    login_button.pack(side=tk.LEFT, padx=5)
                    password_button = tk.Button(site_frame, text="Hasło",
                                                command=lambda site_password=site['password']: copy_to_clipboard(decrypt_aes(site_password, user_password), root))
                    password_button.pack(side=tk.LEFT)
                    remove_button = tk.Button(site_frame, text="Usuń",
                                              command=lambda site_name=site['site']: remove_site(username, site_name, user_window, user_password, root))
                    remove_button.pack(side=tk.RIGHT, padx=5)
