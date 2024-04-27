import subprocess
import psutil
import time

def is_process_running(process_pid):
    if psutil.pid_exists(process_pid):
        process = psutil.Process(process_pid)
        return process.status() != psutil.STATUS_ZOMBIE
    return False

def start_subprocess(script_path):
    try:
        proc = subprocess.Popen(['python', script_path])
        return proc.pid
    except Exception as e:
        print(f"Error starting subprocess '{script_path}': {e}")
        return None

# Kill existing pigpiod processes
subprocess.run(['sudo', 'killall', 'pigpiod'])

# Start pigpiod with timeout option
subprocess.run(['sudo', 'pigpiod', '-t', '0'])

leftScript = '/home/vattu/Documents/rain/d6t-ave-left.py'
rightScript = '/home/vattu/Documents/rain/d6t-ave-right.py'

# Start the subprocesses and store their PIDs
left_pid = start_subprocess(leftScript)
right_pid = start_subprocess(rightScript)

# Store the PIDs of the subprocesses
subprocess_pids = {leftScript: left_pid, rightScript: right_pid}
print(subprocess_pids)

try:
    # Continuous monitoring and restarting of subprocesses
    while True:
        # Check if each subprocess is still running, and restart if not
        for script, pid in subprocess_pids.items():
            if not is_process_running(pid):
                new_pid = start_subprocess(script)
                if new_pid:
                    subprocess_pids[script] = new_pid
                    print(f"{script} restarted.")
        # Adjust the interval based on your needs
        time.sleep(5)  # Check every 5 seconds
except KeyboardInterrupt:
    # Terminate subprocesses upon keyboard interrupt
    for pid in subprocess_pids.values():
        if pid:
            subprocess.Popen(['pkill', '-f', str(pid)])