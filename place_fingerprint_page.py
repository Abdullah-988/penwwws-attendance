import tkinter as tk
import threading
import requests
import serial
import adafruit_fingerprint

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
            uart = serial.Serial("/dev/ttyAMA0", baudrate=57600, timeout=1)
            finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

            if finger.get_image() != adafruit_fingerprint.OK:
                return

            if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                return

            characteristics = finger.download_model(1)
            if not characteristics:
                return

            fingerprint_data = list(characteristics)

            res = requests.post(
                f"{API_BASE_URL}/device/school/fingerprint",
                headers={
                    "Authorization": f"Bearer {app_state['token']}",
                    "Content-Type": "application/json"
                },
                json={
                    "studentId": student["id"],
                    "fingerprint": fingerprint_data
                }
            )

            if res.status_code == 200:
                root.after(1500, lambda: show_groups_students_page(root, app_state))
            else:
                print("Backend error:", res.status_code, res.text)

        except Exception as e:
            print("Error:", e)

    threading.Thread(target=scan_and_send, daemon=True).start()