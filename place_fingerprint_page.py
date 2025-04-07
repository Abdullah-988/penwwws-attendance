import tkinter as tk

def show_place_fingerprint_page(root, app_state):
    from group_students_page import show_groups_students_page

    for widget in root.winfo_children():
        widget.destroy()

    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both")

    inner = tk.Frame(frame)
    inner.place(relx=0.5, rely=0.5, anchor="center")

    student = app_state.get("selected_student", {})
    name = student.get("fullName", "Unknown")

    tk.Label(inner, text=f"Student: {name}", font=("Arial", 14)).pack(pady=10)
    tk.Label(inner, text="Place your finger on the sensor...", font=("Arial", 12)).pack(pady=5)

    tk.Button(inner, text="Cancel", command=lambda: show_groups_students_page(root, app_state)).pack(pady=10)
