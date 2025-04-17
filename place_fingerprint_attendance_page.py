import tkinter as tk
from adafruit_fingerprint import Adafruit_Fingerprint
import serial
import requests
import time

from main import API_BASE_URL

def show_place_fingerprint_page(root, app_state):
    from session_students_page import show_session_students_page
    for widget in root.winfo_children():
        widget.destroy()

    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both")

    inner = tk.Frame(frame)
    inner.place(relx=0.5, rely=0.5, anchor="center")

    status_label = tk.Label(inner, text="Place your finger...", font=("Arial", 14))
    status_label.pack(pady=10)

    def update_status(text):
        status_label.config(text=text)
        root.update_idletasks()

    tk.Button(inner, text="Back", command=lambda: show_session_students_page(root, app_state)).pack(pady=10)

    root.after(500, lambda: run_attendance_scan(app_state, update_status))

    def run_attendance_scan(app_state, update_status_callback):
        try:
            ser = serial.Serial("/dev/ttyAMA0", baudrate=57600, timeout=1)
            finger = Adafruit_Fingerprint(ser)

            update_status_callback("Waiting for finger...")
            while finger.get_image() != Adafruit_Fingerprint.OK:
                time.sleep(0.5)

            if finger.image_2_tz(1) != Adafruit_Fingerprint.OK:
                update_status_callback("Failed to convert image.")
                return

            if finger.download_model(1) != Adafruit_Fingerprint.OK:
                update_status_callback("Failed to download template.")
                return

            scanned_data = list(finger.data)

            student = app_state.get("selected_student")
            if not student:
                update_status_callback("No student selected.")
                return

            res = requests.get(
                f"{API_BASE_URL}/device/fingerprint/{student['id']}",
                headers={"Authorization": f"Bearer {app_state['token']}"}
            )
            if res.status_code != 200:
                update_status_callback("Failed to fetch stored fingerprint.")
                return

            stored_data = res.json().get("fingerprint")
            if not stored_data:
                update_status_callback("No fingerprint saved for this student.")
                return

            if len(scanned_data) != len(stored_data):
                update_status_callback("Fingerprint does not match.")
                return

            # Compare element-wise
            if all(scanned_data[i] == stored_data[i] for i in range(len(scanned_data))):
                update_status_callback("✅ Fingerprint matched. Attendance marked.")
            else:
                update_status_callback("❌ Fingerprint does not match.")

        except Exception as e:
            update_status_callback(f"Error: {e}")