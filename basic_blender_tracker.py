import tkinter as tk
import time
import psutil
import json
from threading import Thread
from datetime import datetime
import win32gui

class BlenderTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Blender Time Tracker")
        self.running = False
        self.start_time = None
        self.total_active_time = 0
        self.total_idle_time = 0
        self.json_file = "blender_usage.json"
        self.load_data()

        self.label = tk.Label(root, text=f"Active Time: {int(self.total_active_time)}s\nIdle Time: {int(self.total_idle_time)}s")
        self.label.pack()

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
            self.track_blender_usage()

    def stop_tracking(self):
        if self.running:
            self.running = False
            self.label.config(text=f"Active Time: {int(self.total_active_time)}s\nIdle Time: {int(self.total_idle_time)}s")

    def track_blender_usage(self):
        def check_blender():
            while self.running:
                is_blender_running = any(proc.name() == "blender.exe" for proc in psutil.process_iter())
                is_blender_active = (win32gui.GetWindowText(win32gui.GetForegroundWindow()) == "Blender")

                if is_blender_running:
                    if is_blender_active:
                        self.total_active_time += 1
                    else:
                        self.total_idle_time += 1

                self.label.config(text=f"Active Time: {int(self.total_active_time)}s\nIdle Time: {int(self.total_idle_time)}s")
                time.sleep(1)

        thread = Thread(target=check_blender)
        thread.daemon = True
        thread.start()

    def save_data(self):
        data = {
            "total_active_time": self.total_active_time,
            "total_idle_time": self.total_idle_time,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.json_file, "w") as f:
            json.dump(data, f)
        print("Data saved to", self.json_file)

    def load_data(self):
        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)
                self.total_active_time = data.get("total_active_time", 0)
                self.total_idle_time = data.get("total_idle_time", 0)
        except FileNotFoundError:
            self.total_active_time = 0
            self.total_idle_time = 0

if __name__ == "__main__":
    root = tk.Tk()
    tracker = BlenderTracker(root)
    root.mainloop()
