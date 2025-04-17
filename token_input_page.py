# token_page.py

import tkinter as tk
from tkinter import messagebox
import json
import requests
from home_page import show_home_page

from main import API_BASE_URL

TOKEN_FILE = "session.json"

def show_token_input_page(root, app_state):
    for widget in root.winfo_children():
        widget.destroy()

    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both")

    inner = tk.Frame(frame)
    inner.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(inner, text="Enter ID:", font=("Arial", 12)).pack(anchor="w")
    entry_id = tk.Entry(inner, width=30, font=("Arial", 11))
    entry_id.pack(pady=1)

    tk.Label(inner, text="Enter Password:", font=("Arial", 12)).pack(anchor="w")
    entry_password = tk.Entry(inner, show="*", width=30, font=("Arial", 11))
    entry_password.pack(pady=1)

    def submit():
        id = entry_id.get().strip()
        password = entry_password.get().strip()
        if not id or not password:
            messagebox.showerror("Error", "Username and password cannot be empty")
            return

        try:
            response = requests.post(f"{API_BASE_URL}/device/login", data={"id": id, "password": password})
            if response.status_code == 200:
                token = response.headers.get("Authorization").split(" ")[1]

                # Save token to file
                with open(TOKEN_FILE, "w") as f:
                    json.dump({"token": token}, f)

                # Store token in app state
                app_state["token"] = token

                # Validate token and fetch school info
                school_response = requests.get(f"{API_BASE_URL}/device/school", headers={
                    "Authorization": f"Bearer {token}"
                })

                if school_response.status_code == 200:
                    school_data = school_response.json()
                    app_state["school_name"] = school_data.get("name")
                    app_state["school_id"] = school_data.get("id")

                    show_home_page(root, app_state)
                else:
                    messagebox.showerror("Error", "Failed to fetch school info.")
            else:
                messagebox.showerror("Error", "Invalid credentials.")
        except Exception as e:
            print("Login failed:", e)
            messagebox.showerror("Error", "Network error or invalid response.")

    tk.Button(inner, text="Submit", command=submit, width=20, height=2).pack(pady=10)
    entry_id.focus()

    return frame
