import tkinter as tk
import requests
from place_fingerprint_page import show_place_fingerprint_page

from main import API_BASE_URL

def show_groups_students_page(root, app_state):
    from groups_page import show_groups_page
    for widget in root.winfo_children():
        widget.destroy()

    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both")

    header = tk.Frame(frame)
    header.pack(fill="x", pady=5, padx=5)

    tk.Button(header, text="← Back", command=lambda: show_groups_page(root, app_state)).pack(side="left")
    tk.Label(header, text="Choose Student", font=("Arial", 16)).pack(side="top", pady=5)

    canvas = tk.Canvas(frame)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 10))

    
    window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def on_canvas_resize(event):
        canvas.itemconfig(window_id, width=event.width)

    canvas.bind("<Configure>", on_canvas_resize)

    try:
        res = requests.get(f"{API_BASE_URL}/device/school/student", headers={
            "Authorization": f"Bearer {app_state['token']}"
        })
        if res.status_code == 200:
            students = res.json()
            for student in students:
                name = student["fullName"]
                btn = tk.Button(scrollable_frame, text=name, width=40, height=2, anchor="w",
                                command=lambda s=student: open_place_page(root, app_state, s))
                btn.pack(expand=True, pady=3)
    except Exception as e:
        print("Error fetching groups:", e)

def open_place_page(root, app_state, student):
    app_state["selected_student"] = student
    show_place_fingerprint_page(root, app_state)
