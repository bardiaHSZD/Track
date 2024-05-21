import psutil
import pygetwindow as gw
import tkinter as tk
from tkinter import messagebox
import time
import json
from datetime import datetime

class NukeWindowTracker:
    def __init__(self):
        self.start_time = None
        self.maximized_time = 0
        self.minimized_time = 0
        self.idle_time = 0
        self.tracking = False

    def get_nuke_pids_with_windows(self):
        """Get all PIDs for running Nuke instances with active windows"""
        pids = []
        for proc in psutil.process_iter(['pid', 'name']):
            if 'nuke' in proc.info['name'].lower():
                pid = proc.info['pid']
                if any(f'Nuke {pid}' in win.title for win in gw.getAllWindows()):
                    pids.append(pid)
        return pids

    def get_window_state(self, pid):
        """Get the window state of the given PID"""
        try:
            win = gw.getWindowsWithTitle(f'Nuke {pid}')[0]
            if win.isMaximized:
                return 'maximized'
            elif win.isMinimized:
                return 'minimized'
            else:
                return 'idle'
        except IndexError:
            return 'idle'

    def start_tracking(self):
        """Start tracking window states"""
        self.tracking = True
        self.start_time = time.time()
        self.track()

    def track(self):
        """Track the window states and update times"""
        if not self.tracking:
            return
        nuke_pids = self.get_nuke_pids_with_windows()
        current_state_counts = {'maximized': 0, 'minimized': 0, 'idle': 0}
        
        for pid in nuke_pids:
            state = self.get_window_state(pid)
            current_state_counts[state] += 1
        
        # Time difference
        elapsed = time.time() - self.start_time
        total_instances = len(nuke_pids) if nuke_pids else 1  # To prevent division by zero
        
        self.maximized_time += (current_state_counts['maximized'] / total_instances) * elapsed
        self.minimized_time += (current_state_counts['minimized'] / total_instances) * elapsed
        self.idle_time += (current_state_counts['idle'] / total_instances) * elapsed
        
        self.start_time = time.time()  # Reset start time
        
        # Repeat every second
        self.root.after(1000, self.track)

    def stop_tracking(self):
        """Stop tracking and log the results"""
        self.tracking = False
        data = {
            'date': str(datetime.now()),
            'maximized_time': self.maximized_time,
            'minimized_time': self.minimized_time,
            'idle_time': self.idle_time
        }
        with open('nuke_window_tracking.json', 'a') as f:
            json.dump(data, f, indent=4)
            f.write('\n')
        messagebox.showinfo("Tracking Stopped", "Tracking data has been saved.")

    def run(self):
        """Run the GUI"""
        self.root = tk.Tk()
        self.root.title("Nuke Window Tracker")
        
        start_button = tk.Button(self.root, text="Start Tracking", command=self.start_tracking)
        start_button.pack(pady=20)
        
        stop_button = tk.Button(self.root, text="Stop Tracking", command=self.stop_tracking)
        stop_button.pack(pady=20)
        
        self.root.mainloop()

if __name__ == "__main__":
    tracker = NukeWindowTracker()
    tracker.run()
