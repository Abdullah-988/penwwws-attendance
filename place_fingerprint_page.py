import tkinter as tk
import threading
import requests
import base64
from pyfingerprint.pyfingerprint import PyFingerprint

from main import API_BASE_URL

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

    def scan_and_send():
        try:
            sensor = PyFingerprint("/dev/ttyAMA0", 57600, 0xFFFFFFFF, 0x00000000)

            if not sensor.verifyPassword():
                raise ValueError('Could not verify sensor password.')

            print('Waiting for finger...')
            while not sensor.readImage():
                pass

        # Convert the image to characteristics and store in char buffer 1
            sensor.convertImage(0x01)

        # Download the characteristics from buffer 1
            template = sensor.downloadCharacteristics(0x01)  # list of integers (0–255)

        # Convert to bytes
            template_bytes = bytes(template)

        # Encode to Base64
            fp_bytes = base64.b64encode(template_bytes).decode('utf-8')


            res = requests.post(
                f"{API_BASE_URL}/device/school/fingerprint",
                headers={
                    "Authorization": f"Bearer {app_state['token']}",
                    "Content-Type": "application/json"
                },
                json={
                    "studentId": student["id"],
                    "fingerprint": fp_bytes
                }
            )
            if res.status_code == 200:
                root.after(1500, lambda: show_groups_students_page(root, app_state))
            else:
                print("Backend error:", res.status_code, res.text)

        except Exception as e:
            print("Error:", e)

    threading.Thread(target=scan_and_send, daemon=True).start()