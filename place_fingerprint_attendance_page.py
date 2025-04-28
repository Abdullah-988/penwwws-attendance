import tkinter as tk
import base64
import requests
from pyfingerprint.pyfingerprint import PyFingerprint

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

    def run_attendance_scan():
        try:
            student = app_state.get("selected_student")
            if not student:
                update_status("No student selected.")
                return

            f = PyFingerprint("/dev/ttyAMA0", 57600, 0xFFFFFFFF, 0x00000000)

            if not f.verifyPassword():
                raise ValueError('Sensor password is wrong!')

            print('Sensor initialized.')

            res = requests.get(
                f"{API_BASE_URL}/device/school/fingerprint/{student['id']}",
                headers={"Authorization": f"Bearer {app_state['token']}"}
            )
            if res.status_code != 200:
                update_status("Failed to fetch stored fingerprint.")
                print(res)
                return

            fingerprint_array = list(base64.b64decode(res.json()['fingerprint']))

            if not f.uploadCharacteristics(0x01, fingerprint_array):
                raise Exception('Failed to upload template.')

            matched = False
            while not matched:
                print('Please place your finger for scanning...')
                update_status("Place your finger...")

                while not f.readImage():
                    root.update()
                    pass

                f.convertImage(0x02)

                match_score = f.compareCharacteristics()

                print(f'Match score: {match_score}')
                if match_score < 40:
                    update_status("No match, try again...")
                    continue

                print("Fingerprint matched!")
                update_status("Fingerprint matched!")

                post_res = requests.post(
                    f"{API_BASE_URL}/device/school/session/{app_state.get('selected_session_id')}",
                    json={"studentId": student['id']},
                    headers={
                        "Authorization": f"Bearer {app_state['token']}",
                    }
                )
                if post_res.status_code == 200:
                    update_status("Attendance marked successfully.")
                    root.after(1000, lambda: show_session_students_page(root, app_state))
                else:
                    update_status("Failed to mark attendance.")
                matched = True

        except Exception as e:
            update_status(f"Error: {e}")

    tk.Button(inner, text="Back", command=lambda: show_session_students_page(root, app_state)).pack(pady=10)

    root.after(500, run_attendance_scan)
