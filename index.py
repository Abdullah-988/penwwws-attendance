import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
import json
import os

API_BASE_URL = "http://localhost:5555/api"
TOKEN_FILE = "session.json"

# ----- Home Page -----
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(expand=True, fill="both")
        
        inner = tk.Frame(self)
        inner.place(relx=0.5, rely=0.5, anchor="center")
        
        self.label = tk.Label(inner, text="", font=("Arial", 14))
        self.label.pack(pady=10, anchor="w")
        tk.Button(inner, text="Create Fingerprint", command=self.create_fingerprint, width=20, height=2).pack(pady=5)
        tk.Button(inner, text="Attendance", command=self.attendance, width=20, height=2).pack(pady=5)

    def update_school_info(self):
        name = self.controller.schoolname or "Unknown"
        id = self.controller.schoolid or "N/A"
        self.label.config(text=f"Welcome to {name}")

    def create_fingerprint(self):
        print("Loading students...")
        self.controller.frames["FingerprintListPage"].load_students()
        self.controller.show_frame("FingerprintListPage")

    def attendance(self):
        print("Viewing attendance...")

class FingerprintListPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Create a canvas for scrolling
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_students(self):
        # Clear previous content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        token = self.controller.token
        try:
            response = requests.get(
                f"{API_BASE_URL}/device/school/student",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                students = response.json()
                if not students:
                    tk.Label(self.scrollable_frame, text="No students found.").pack(pady=10)
                else:
                    for student in students:
                        student_name = student.get("fullName")
                        student_id = student.get("id")
                        student_button = tk.Button(
                            self.scrollable_frame, 
                            text=student_name, 
                            command=lambda sid=student_id, name=student_name: self.on_student_click(sid, name)
                        )
                        student_button.pack(fill="x", padx=10, pady=5, anchor="center")
            else:
                tk.Label(self.scrollable_frame, text="Failed to fetch students.", fg="red").pack(pady=10)
        except Exception as e:
            print("Error fetching students:", e)
            tk.Label(self.scrollable_frame, text="Network error.", fg="red").pack(pady=10)

    def on_student_click(self, student_id, student_name):
        self.controller.student_id = student_id
        self.controller.student_name = student_name
        self.controller.show_frame("PlaceFingerPage")

class PlaceFingerPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        inner = tk.Frame(self)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        # Label showing the student info
        self.student_label = tk.Label(inner, text="Place your finger", font=("Arial", 14))
        self.student_label.pack(pady=20)

        # Display selected student name
        self.student_info = tk.Label(inner, text="", font=("Arial", 12))
        self.student_info.pack(pady=10)

        # Update student info once page is shown
        self.update_student_info()

    def update_student_info(self):
        student_name = self.controller.student_name or "Unknown"
        student_id = self.controller.student_id or "N/A"
        self.student_info.config(text=f"Student: {student_name} (ID: {student_id})")


# ----- Token Input Page -----
class TokenInputPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Fill the entire container
        self.pack(expand=True, fill="both")
        
        # Create an inner frame that is centered
        inner = tk.Frame(self)
        inner.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(inner, text="Enter Username:", font=("Arial", 12)).pack(anchor="w")
        self.entryUsername = tk.Entry(inner, width=30, font=("Arial", 11))
        self.entryUsername.pack(pady=1)
        tk.Label(inner, text="Enter Password:", font=("Arial", 12)).pack(anchor="w")
        self.entryPassword = tk.Entry(inner, width=30, font=("Arial", 11))
        self.entryPassword.pack(pady=1)
        tk.Button(inner, text="Submit", command=self.submit_token, width=20, height=2).pack(pady=10)
        
        self.entryUsername.focus()

    def submit_token(self):
        username = self.entryUsername.get().strip()
        password = self.entryPassword.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty")
            return

        if self.validate_login(username, password):
            self.controller.show_frame("HomePage")
        else:
            messagebox.showerror("Error", "Invalid credentials or network issue")

    def validate_login(self, username, password):
        try:
            response = requests.post(f"{API_BASE_URL}/device/login", data={"username": username, "password": password})
            print(response)
            if response.status_code == 200:
                token = response.headers.get("Authorization").split(" ")[1]
                if token:
                    self.save_token(token)
                    return True
                return True
        except Exception as e:
            print("Error validating login:", e)
        return False

    def save_token(self, token):
        self.token = token
        with open(TOKEN_FILE, "w") as f:
            json.dump({"token": token}, f)

# ----- Main Application Class -----
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Penwwws Attendance")
        self.center_window(320, 240)
        self.token = None
        self.student_name = None
        self.student_id = None 
        
        # Outer container that fills the window.
        container = tk.Frame(self)
        container.pack(expand=True, fill="both")
        
        # Use a dictionary to hold pages.
        self.frames = {}
        for F in (TokenInputPage, HomePage, FingerprintListPage, PlaceFingerPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.place(relwidth=1, relheight=1)

        self.check_token_and_start()


    def validate_token(self):
            try:
                response = requests.get(f"{API_BASE_URL}/device/school", headers={"Authorization": f"Bearer {self.token}"})
                if response.status_code == 200:
                    self.schoolid = response.json().get("id")
                    self.schoolname = response.json().get("name")
                    return True
            except Exception as e:
                print("Error validating login:", e)
            return False

    def check_token_and_start(self):
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                data = json.load(f)
                self.token = data.get("token")

            if self.validate_token():
                self.show_frame("HomePage")
                return

        self.show_frame("TokenInputPage")

    def center_window(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if page_name == "HomePage":
            frame.update_school_info()
        frame.lift()

if __name__ == "__main__":
    app = App()
    app.mainloop()
