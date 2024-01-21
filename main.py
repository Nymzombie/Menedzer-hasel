import tkinter as tk
import user_interface
import login
import registration

# Stałe globalne
DATABASE_PATH = "DATA/database.json"

# Ustawienie głównego okna aplikacji
root = tk.Tk()
root.title("Logowanie")
root.geometry("350x150")
root.resizable(False, False)

# Tworzenie i konfiguracja głównych widgetów
lock_icon = tk.PhotoImage(file="DATA/graphics/lock_icon.png")
lock_label = tk.Label(root, image=lock_icon)
lock_label.place(x=0, y=0)

login_label = tk.Label(root, text="Login:")
login_label.pack()
login_entry = tk.Entry(root, width=20)
login_entry.pack(pady=5)

password_label = tk.Label(root, text="Hasło:")
password_label.pack()
password_entry = tk.Entry(root, width=20, show="*")
password_entry.pack(pady=5)

login_button = tk.Button(root, text="→\nLogowanie", command=lambda: login.on_login(root, login_entry, password_entry, user_interface), height=5)
login_button.place(x=255, y=15)

register_button = tk.Button(root, text="Rejestracja", command=lambda: registration.open_registration_window(root))
register_button.place(x=255, y=110)

root.mainloop()
