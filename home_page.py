import tkinter as tk
from groups_page import show_groups_page
from subjects_page import show_subjects_page

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
