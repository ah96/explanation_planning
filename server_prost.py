import subprocess
import time
import threading
import os

def start_server(server_command):
    """
    Starts the server as a subprocess and captures its output.

    :param server_command: Command to start the server.
    :return: The server process.
    """
    try:
        print("Starting the server...")
        server_process = subprocess.Popen(
            server_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # Start a thread to print server output
        def print_server_output():
            for line in iter(server_process.stdout.readline, ""):
                print(f"[SERVER]: {line.strip()}")

        threading.Thread(target=print_server_output, daemon=True).start()
        return server_process

    except Exception as e:
        print(f"Error starting server: {e}")
        return None

def run_prost(prost_command):
    """
    Runs PROST and captures its output.

    :param prost_command: Command to run PROST.
    """
    try:
        print("Running PROST...")
        result = subprocess.run(prost_command, capture_output=True, text=True, check=True)
        print("[PROST Output]:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("An error occurred while running PROST:")
        print(e.stderr)

def main():
    # Define commands
    server_command = ["./run-server.py", "-b", "benchmarks/gerard_new/"]
    prost_command = ["./prost.py", "instance_posthoc", "[Prost -s 1 -se [IPC2014]]"]

    # Start the server
    server_process = start_server(server_command)

    if not server_process:
        print("Failed to start the server. Exiting.")
        return

    # Wait for the server to initialize
    print("Waiting for the server to initialize...")
    #time.sleep(5)  # Adjust this delay based on server startup time

    # Run PROST
    #run_prost(prost_command)

    # Stop the server
    #print("Stopping the server...")
    #server_process.terminate()
    #server_process.wait()

if __name__ == "__main__":
    main()
