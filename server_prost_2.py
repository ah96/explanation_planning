import subprocess
import time
import threading
import os

def start_server_in_terminal():
    """
    Starts the server in an external terminal.
    """
    try:
        print("Starting the server in an external terminal...")
        os.system('gnome-terminal -- bash -c "./run-server.py -b ./testbed/benchmarks/gerard_mix/; exec bash"')
        print("Server started.")
    except Exception as e:
        print(f"Failed to start the server in an external terminal: {e}")

def run_prost():
    """
    Runs PROST in the current process and captures its output.
    """
    prost_command = ["./prost.py", "instance_prehoc", "[Prost -s 1 -se [IPC2014]]"]
    try:
        print("Running PROST...")
        result = subprocess.run(prost_command, capture_output=True, text=True, check=True)
        print("[PROST Output]:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("An error occurred while running PROST:")
        print(e.stderr)

def main():
    # Start the server in an external terminal
    start_server_in_terminal()

    # Wait for the server to initialize
    print("Waiting for the server to initialize...")
    time.sleep(5)  # Adjust this delay based on server startup time

    # Run PROST
    run_prost()

if __name__ == "__main__":
    main()
