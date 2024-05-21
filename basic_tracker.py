import time
import psutil
import pygetwindow as gw
from datetime import datetime
import tkinter as tk
from tkinter import ttk

# Global variable to control the tracking loop
tracking = False

def get_nuke_processes():
    nuke_processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and proc.info['name'].startswith('Nuke'):
            nuke_processes.append(proc)
    return nuke_processes

def get_window_state(window):
    if window.isMaximized:
        return "maximized"
    elif window.isMinimized:
        return "minimized"
    elif window.isActive:
        return "active"
    else:
        return "unknown"

def update_times(active_time, idle_time, minimized_time):
    time_info = f"Total time active: {active_time:.2f} seconds\n"
    time_info += f"Total time idle: {idle_time:.2f} seconds\n"
    time_info += f"Total time minimized: {minimized_time:.2f} seconds\n"
    return time_info

def track_time(label):
    global tracking
    active_time = 0
    idle_time = 0
    minimized_time = 0
    last_state = "unknown"
    start_time = datetime.now()

    while tracking:
        nuke_processes = get_nuke_processes()
        current_time = datetime.now()
        elapsed_time = (current_time - start_time).total_seconds()

        any_active = False
        any_minimized = False
        all_idle_or_maximized = True

        for proc in nuke_processes:
            try:
                windows = [w for w in gw.getAllWindows() if 'Nuke' in w.title and w.pid == proc.info['pid']]
                if windows:
                    window = windows[0]
                    state = get_window_state(window)
                else:
                    state = "unknown"

                if state == "active":
                    any_active = True
                elif state == "minimized":
                    any_minimized = True
                if state != "unknown" and state != "minimized":
                    all_idle_or_maximized = False

            except Exception as e:
                print(f"Error processing window for PID {proc.info['pid']}: {e}")
                continue

        if any_active:
            active_time += elapsed_time
            last_state = "active"
        elif any_minimized:
            minimized_time += elapsed_time
            last_state = "minimized"
        elif all_idle_or_maximized:
            idle_time += elapsed_time
            last_state = "idle"

        start_time = current_time

        time.sleep(1)

        time_info = update_times(active_time, idle_time, minimized_time)
        label.config(text=time_info)
        label.update()

def start_tracking(label):
    global tracking
    tracking = True
    track_time(label)

def stop_tracking():
    global tracking
    tracking = False

def main():
    root = tk.Tk()
    root.title("Nuke Process State Tracker")

    label = ttk.Label(root, text="", anchor="center", justify="left")
    label.pack(padx=10, pady=10)

    start_button = ttk.Button(root, text="Start Tracking", command=lambda: start_tracking(label))
    start_button.pack(padx=10, pady=5)

    stop_button = ttk.Button(root, text="Stop Tracking", command=stop_tracking)
    stop_button.pack(padx=10, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
