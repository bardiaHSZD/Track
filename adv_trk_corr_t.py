import tkinter as tk
import time
import psutil
import json
import os
from threading import Thread
from datetime import datetime, timedelta
import win32gui

class ApplicationTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Application Time Tracker")
        self.running = False
        self.start_time = None
        self.json_file = "app_usage.json"
        self.username = os.getlogin()

        self.applications = {
            "blender.exe": {"name": "Blender", "active_time": 0, "idle_time": 0},
            "Nuke": {"name": "Nuke", "active_time": 0, "idle_time": 0},
            "maya.exe": {"name": "Autodesk Maya", "active_time": 0, "idle_time": 0},
            "houdinifx.exe": {"name": "Houdini", "active_time": 0, "idle_time": 0},
            "Adobe Premiere Pro.exe": {"name": "Adobe Premiere", "active_time": 0, "idle_time": 0},
            "AfterFX.exe": {"name": "After Effects", "active_time": 0, "idle_time": 0},
            "chrome.exe": {"name": "Chrome", "active_time": 0, "idle_time": 0},
            "firefox.exe": {"name": "Firefox", "active_time": 0, "idle_time": 0}
        }

        self.load_data()

        self.labels = {}
        for app in self.applications:
            self.labels[app] = tk.Label(root, text=self.get_label_text(app))
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
            self.previous_time = time.time()
            self.track_application_usage()

    def stop_tracking(self):
        if self.running:
            self.running = False
            self.update_labels()

    def track_application_usage(self):
        def check_applications():
            while self.running:
                current_time = time.time()
                elapsed_time = current_time - self.previous_time
                self.previous_time = current_time

                for app, details in self.applications.items():
                    is_app_running = any(app in proc.name() for proc in psutil.process_iter())
                    active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
                    is_app_active = details["name"] in active_window

                    if is_app_running:
                        if is_app_active:
                            self.applications[app]["active_time"] += elapsed_time
                        else:
                            self.applications[app]["idle_time"] += elapsed_time

                self.update_labels()
                time.sleep(1)

        thread = Thread(target=check_applications)
        thread.daemon = True
        thread.start()

    def update_labels(self):
        for app in self.applications:
            self.labels[app].config(text=self.get_label_text(app))

    def get_label_text(self, app):
        details = self.applications[app]
        active_time_str = str(timedelta(seconds=int(details["active_time"])))
        idle_time_str = str(timedelta(seconds=int(details["idle_time"])))
        return f"{details['name']} - Active: {active_time_str}, Idle: {idle_time_str}"

    def save_data(self):
        now = datetime.now()
        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        today = now.date().isoformat()

        if self.username not in data:
            data[self.username] = {}

        if today not in data[self.username]:
            data[self.username][today] = {app: {"active_time": "0:00:00", "idle_time": "0:00:00"} for app in self.applications}

        for app, details in self.applications.items():
            data[self.username][today][app]["active_time"] = str(timedelta(seconds=self.convert_time_to_seconds(data[self.username][today][app]["active_time"]) + details["active_time"]))
            data[self.username][today][app]["idle_time"] = str(timedelta(seconds=self.convert_time_to_seconds(data[self.username][today][app]["idle_time"]) + details["idle_time"]))

        with open(self.json_file, "w") as f:
            json.dump(data, f, indent=4)
        print("Data saved to", self.json_file)

    def load_data(self):
        now = datetime.now()
        today = now.date().isoformat()

        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)
                if self.username in data and today in data[self.username]:
                    for app, details in self.applications.items():
                        if app in data[self.username][today]:
                            details["active_time"] = self.convert_time_to_seconds(data[self.username][today][app].get("active_time", "0:00:00"))
                            details["idle_time"] = self.convert_time_to_seconds(data[self.username][today][app].get("idle_time", "0:00:00"))
        except FileNotFoundError:
            pass

    @staticmethod
    def convert_time_to_seconds(time_str):
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s

if __name__ == "__main__":
    root = tk.Tk()
    tracker = ApplicationTracker(root)
    root.mainloop()
