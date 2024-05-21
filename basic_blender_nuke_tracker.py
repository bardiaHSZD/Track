import tkinter as tk
import time
import psutil
import json
from threading import Thread
from datetime import datetime
import win32gui

class ApplicationTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Application Time Tracker")
        self.running = False
        self.start_time = None
        self.json_file = "app_usage.json"

        self.applications = {
            "blender.exe": {"name": "Blender", "active_time": 0, "idle_time": 0},
            "Nuke": {"name": "Nuke", "active_time": 0, "idle_time": 0}
        }

        self.load_data()

        self.labels = {}
        for app in self.applications:
            self.labels[app] = tk.Label(root, text=f"{self.applications[app]['name']} - Active: {int(self.applications[app]['active_time'])}s, Idle: {int(self.applications[app]['idle_time'])}s")
            self.labels[app].pack()

        self.start_button = tk.Button(root, text="Start Tracking", command=self.start_tracking)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop Tracking", command=self.stop_tracking)
        self.stop_button.pack()

        self.save_button = tk.Button(root, text="Save Data", command=self.save_data)
        self.save_button.pack()

    def start_tracking(self):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            self.track_application_usage()

    def stop_tracking(self):
        if self.running:
            self.running = False
            self.update_labels()

    def track_application_usage(self):
        def check_applications():
            while self.running:
                for app, details in self.applications.items():
                    is_app_running = any(app in proc.name() for proc in psutil.process_iter())
                    active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
                    is_app_active = details["name"] in active_window

                    if is_app_running:
                        if is_app_active:
                            self.applications[app]["active_time"] += 1
                        else:
                            self.applications[app]["idle_time"] += 1

                self.update_labels()
                time.sleep(1)

        thread = Thread(target=check_applications)
        thread.daemon = True
        thread.start()

    def update_labels(self):
        for app, details in self.applications.items():
            self.labels[app].config(text=f"{details['name']} - Active: {int(details['active_time'])}s, Idle: {int(details['idle_time'])}s")

    def save_data(self):
        data = {app: {"active_time": details["active_time"], "idle_time": details["idle_time"], "last_updated": datetime.now().isoformat()} for app, details in self.applications.items()}
        with open(self.json_file, "w") as f:
            json.dump(data, f)
        print("Data saved to", self.json_file)

    def load_data(self):
        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)
                for app, details in self.applications.items():
                    if app in data:
                        self.applications[app]["active_time"] = data[app].get("active_time", 0)
                        self.applications[app]["idle_time"] = data[app].get("idle_time", 0)
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    tracker = ApplicationTracker(root)
    root.mainloop()
