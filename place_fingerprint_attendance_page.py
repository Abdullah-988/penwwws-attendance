import tkinter as tk
import base64
import requests
from pyfingerprint.pyfingerprint import PyFingerprint

from main import API_BASE_URL

def show_place_fingerprint_page(root, app_state):
    from subjects_presets_page import show_subjects_presets_page

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

    def run_subject_attendance_scan():
        try:
            f = PyFingerprint("/dev/ttyAMA0", 57600, 0xFFFFFFFF, 0x00000000)

            if not f.verifyPassword():
                raise ValueError('Sensor password is wrong!')

            print('Sensor initialized.')

            subject_id = app_state.get("selected_subject_id")
            if not subject_id:
                update_status("No subject selected.")
                return

            res = requests.get(
                f"{API_BASE_URL}/device/school/subject/{subject_id}/fingerprint",
                headers={"Authorization": f"Bearer {app_state['token']}"}
            )
            if res.status_code != 200:
                update_status("Failed to fetch fingerprints.")
                print(res)
                return

            fingerprint_entries = res.json()  # List of { content: base64 fingerprint, user: { id, fullName } }

            if not fingerprint_entries:
                update_status("No fingerprints found.")
                return

            print("Waiting for user to scan...")

            while True:
                update_status("Place your finger...")
                while not f.readImage():
                    root.update()
                    pass

                f.convertImage(0x02)  # Save scanned finger to char buffer 2

                recognized_user = None

                for entry in fingerprint_entries:
                    template_bytes = base64.b64decode(entry["content"])
                    template_list = list(template_bytes)

                    if not f.uploadCharacteristics(0x01, template_list):
                        continue  # Skip if upload failed

                    match_score = f.compareCharacteristics()

                    print(f"Comparing with {entry['user']['fullName']}, score: {match_score}")

                    if match_score >= 40:
                        recognized_user = entry['user']
                        break  # Stop searching after first match

                if recognized_user:
                    update_status(f"Attendance added for {recognized_user['fullName']}")
                    post_res = requests.post(
                        f"{API_BASE_URL}/device/school/session/{app_state.get('selected_session_id')}",
                        json={"studentId": recognized_user['id']},
                        headers={"Authorization": f"Bearer {app_state['token']}"}
                    )
                    if post_res.status_code == 200:
                        print("Attendance marked.")
                    else:
                        print("Failed to mark attendance.")
                    root.after(1500, lambda: show_subjects_presets_page(root, app_state))
                    break
                else:
                    update_status("Not recognized. Try again.")
                    root.after(1500, lambda: update_status("Place your finger..."))

        except Exception as e:
            update_status(f"Error: {e}")

    tk.Button(inner, text="Back", command=lambda: show_subjects_presets_page(root, app_state)).pack(pady=10)

    root.after(500, run_subject_attendance_scan)
