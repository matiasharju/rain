import subprocess
import psutil
import time

def is_process_running(process_pid):
    return psutil.pid_exists(process_pid)

def start_subprocess(script_path):
    return subprocess.Popen(['python', script_path])

# Kill existing pigpiod processes
subprocess.run(['sudo', 'killall', 'pigpiod'])

# Start pigpiod with timeout option
subprocess.run(['sudo', 'pigpiod', '-t', '0'])

leftScript = '/home/vattu/Documents/rain/d6t-ave-left.py'
rightScript = '/home/vattu/Documents/rain/d6t-ave-right.py'

# Start the subprocesses and store their PIDs
left_proc = start_subprocess(leftScript)
right_proc = start_subprocess(rightScript)

# Store the PIDs of the subprocesses
subprocess_pids = {leftScript: left_proc.pid, rightScript: right_proc.pid}

try:
    # Continuous monitoring and restarting of subprocesses
    while True:
        # Check if each subprocess is still running, and restart if not
        for script, pid in subprocess_pids.items():
            if not is_process_running(pid):
                subprocess_pids[script] = start_subprocess(script).pid
                print(f"{script} restarted.")
        # Adjust the interval based on your needs
        time.sleep(5)  # Check every 5 seconds
except KeyboardInterrupt:
    # Terminate subprocesses upon keyboard interrupt
    left_proc.terminate()
    right_proc.terminate()