import tkinter as tk
import os
from groups_page import show_groups_page
from subjects_page import show_subjects_page


def logout(root, app_state):
    from main import TOKEN_FILE
    from token_input_page import show_token_input_page
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    app_state.clear()
    show_token_input_page(root, app_state)

def show_home_page(root, app_state):
    for widget in root.winfo_children():
        widget.destroy()

    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both")

    inner = tk.Frame(frame)
    inner.place(relx=0.5, rely=0.5, anchor="center")

    school_name = app_state.get("school_name", "Unknown School")
    tk.Label(inner, text=f"Welcome to {school_name}", font=("Arial", 14)).pack(pady=10, anchor="w")

    tk.Button(inner, height=2, text="Create Fingerprint", command=lambda: show_groups_page(root, app_state)).pack(pady=1, fill="x")
    tk.Button(inner, height=2, text="Attendance", command=lambda: show_subjects_page(root, app_state)).pack(pady=1, fill="x")

    tk.Button(inner, text="Logout", width=25, height=2, command=lambda: logout(root, app_state)).pack(pady=20)