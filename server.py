import subprocess
import threading
import time

def start_server_with_output():
    """
    Starts the server and captures its output in real-time.
    """
    server_command = ["./run-server.py", "-b", "benchmarks/explanation_planning/"]

    def read_output(process):
        """
        Reads the server's output in real-time.
        """
        for line in iter(process.stdout.readline, b""):
            print("[SERVER]:", line.decode().strip())  # Print server output
        process.stdout.close()

    try:
        print("Starting the server...")
        server_process = subprocess.Popen(
            server_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Start a thread to read the server output
        server_output_thread = threading.Thread(target=read_output, args=(server_process,), daemon=True)
        server_output_thread.start()

        return server_process

    except Exception as e:
        print(f"Error starting server: {e}")
        return None
    
#start_server_with_output()

# Start the server
server_process = start_server_with_output()

# Wait for the server to be ready
print("Waiting for server to initialize...")
time.sleep(5)  # Replace with actual check if server outputs a ready message