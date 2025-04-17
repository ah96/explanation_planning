import subprocess
import time
from rosgraph.masterapi import Master

def launch_rosplan():
    print("Launching ROSPlan (explanation_planning.launch)...")
    return subprocess.Popen(["roslaunch", "explanation_planning.launch"])

def wait_for_roscore(timeout=20):
    print("Waiting for roscore to start...")
    master = Master('/rostopic')
    for _ in range(timeout):
        try:
            master.getSystemState()
            print("roscore is running.")
            return True
        except:
            time.sleep(1)
    print("Timeout waiting for roscore.")
    return False

def main():
    # Step 1: Launch ROSPlan
    rosplan_process = launch_rosplan()

    # Step 2: Wait for roscore
    if not wait_for_roscore():
        rosplan_process.terminate()
        return

if __name__ == "__main__":
    main()    