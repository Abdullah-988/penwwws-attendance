import tkinter as tk
import json
import os
import requests
from token_input_page import show_token_input_page
from home_page import show_home_page
from groups_page import show_groups_page
from place_fingerprint_page import show_place_fingerprint_page

API_BASE_URL = "http://localhost:5555/api"
TOKEN_FILE = "session.json"

app_state = {
    "token": None,
    "school_name": None,
    "school_id": None,
    "selected_student": None,
    "selected_group": None,
    "selected_subject": None
}

def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

def validate_token(token):
    try:
        response = requests.get(f"{API_BASE_URL}/device/school", headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 200:
            data = response.json()
            app_state["school_id"] = data.get("id")
            app_state["school_name"] = data.get("name")
            return True
    except Exception as e:
        print("Token validation failed:", e)
    return False

def check_saved_token(root):
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            token = json.load(f).get("token")
            if token and validate_token(token):
                app_state["token"] = token
                show_home_page(root, app_state)
                return
            
    show_token_input_page(root, app_state)

def main():
    root = tk.Tk()
    root.title("Penwwws Attendance")
    center_window(root, 320, 240)
    check_saved_token(root)
    root.mainloop()

if __name__ == "__main__":
    main()
