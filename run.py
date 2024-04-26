import subprocess
import psutil

subprocess.run(['sudo', 'killall', 'pigpiod'])
subprocess.run(['sudo', 'pigpiod', '-t', '0'])

def is_process_running(process_name):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            return True
    return False

leftScript = 'd6t-ave-left.py'
rightScript = 'd6t-ave-right.py'

if not is_process_running(leftScript):
    subprocess.Popen(['python', '/home/vattu/Documents/rain/' + leftScript])

if not is_process_running(rightScript):
    subprocess.Popen(['python', '/home/vattu/Documents/rain/' + rightScript])

try:
    # Keep the main script running until interrupted by Ctrl+C
    while True:
        pass
except KeyboardInterrupt:
    # Handle keyboard interrupt (Ctrl+C) to gracefully terminate subprocesses
    if is_process_running(leftScript):
        subprocess.Popen(['pkill', '-f', leftScript])
    if is_process_running(rightScript):
        subprocess.Popen(['pkill', '-f', rightScript])