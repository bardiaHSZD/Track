import time
import psutil
import os

# Get all Nuke processes
nuke_processes = []
for proc in psutil.process_iter():
	if proc.name() == "Nuke.exe":
		nuke_processes.append(proc)

# Check if Nuke is running
if not nuke_processes:
	print("Nuke is not running")
	exit()

# Track time for each instance
for proc in nuke_processes:
	maximized_time = 0
	idle_time = 0
	minimized_time = 0
	last_state = None
	start_time = None
	while True:
		# Get the Nuke window handle
		nuke_window_handle = None
		for window in psutil.window_enum():
			if window.pid == proc.pid:
				nuke_window_handle = window.handle
				break
		
		# Check if Nuke is maximized, idle, or minimized
		state = None
		if psutil.window_is_maximized(nuke_window_handle):
			state = "maximized"
		elif psutil.window_is_minimized(nuke_window_handle):
			state = "minimized"
		elif psutil.window_is_idle(nuke_window_handle):
			state = "idle"
		else:
			state = "unknown"
		
		# Track time for each state
		if state != last_state:
			if state == "maximized":
				start_time = time.time()
			elif state == "minimized":
				minimized_time += time.time() - start_time
			elif state == "idle":
				idle_time += time.time() - start_time
			last_state = state
		if state == "maximized" and start_time is not None:
			maximized_time += time.time() - start_time
			start_time = time.time()
		time.sleep(1)
	
	# Print the tracked times for each instance
	print(f"Instance {proc.pid}:")
	print(f"Time maximized: {maximized_time:.2f} seconds")
	print(f"Time idle: {idle_time:.2f} seconds")
	print(f"Time minimized: {minimized_time:.2f} seconds")