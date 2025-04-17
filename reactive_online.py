import subprocess
import time
import os
import re
import shutil
import argparse

DOMAIN_FILE = "./domain.rddl"
ORIGINAL_INSTANCE = "./instance_failure_probability.rddl"
ALT_INSTANCE = "./instance_failure_probability_reactive.rddl"
PLAN_FILE = "./plan_output.txt"
SEARCH_OPTIONS = "[PROST -s 1 -se [IPPC2014]]"
PLANNER_SCRIPT = "src/rosplan/rosplan_planning_system/common/bin/prost/run_prost_online.sh"
TASK_FAILED_VAR = "task_failed"

def run_planner(instance_file):
    print(f"Running planner on: {instance_file}")
    with open(PLAN_FILE, "w") as out:
        subprocess.run([
            PLANNER_SCRIPT,
            DOMAIN_FILE,
            instance_file,
            SEARCH_OPTIONS,
            PLAN_FILE
        ], stdout=out, stderr=subprocess.STDOUT, text=True)

def extract_plan_actions():
    with open(PLAN_FILE) as f:
        content = f.read()
    pattern = r"\*\* Actions received: \[([^\]]*)\]"
    matches = re.findall(pattern, content)
    actions = []
    for group in matches:
        acts = [a.strip() for a in group.split(";") if a.strip()]
        actions.extend(acts)
    return actions

def start_simulator(domain_path, instance_path):
    return subprocess.Popen([
        "python3", "src/rosplan/rosplan_planning_system/common/bin/prost/testbed/run-server.py",
        "-b", os.path.dirname(domain_path)
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)

def step_simulation(sim_proc, action):
    sim_proc.stdin.write(action + "\n")
    sim_proc.stdin.flush()
    time.sleep(0.5)
    output = []
    while True:
        line = sim_proc.stdout.readline()
        if not line:
            break
        output.append(line.strip())
        if TASK_FAILED_VAR in line:
            break
        if "state reward" in line or "----------" in line:
            break
    return output

def detect_task_failure(output_lines):
    for line in output_lines:
        if TASK_FAILED_VAR in line and "true" in line.lower():
            return True
    return False

def modify_instance_to_avoid_failure(original_instance, new_instance, failed_action):
    with open(original_instance, "r") as f:
        content = f.read()

    print("Generating new instance to avoid failure...")
    if "fetch_book" in failed_action:
        # Disable failure probabilities
        content = re.sub(r"prob_failure\(([^,]+), ([^)]+)\)\s*=\s*[\d.]+", r"prob_failure(\1, \2) = 0.0", content)

    content = content.replace("instance_failure_probability", "instance_failure_probability_reactive")
    with open(new_instance, "w") as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", default=ORIGINAL_INSTANCE)
    args = parser.parse_args()

    run_planner(args.instance)
    actions = extract_plan_actions()
    if not actions:
        print("No actions found.")
        return

    print("Plan generated:")
    for a in actions:
        print(f"  - {a}")

    print("Launching RDDLSim...")
    sim_proc = start_simulator(DOMAIN_FILE, args.instance)
    time.sleep(1)

    print("Simulating plan step-by-step...")
    for step, action in enumerate(actions):
        print(f"Step {step+1}: Executing action: {action}")
        out = step_simulation(sim_proc, action)
        if detect_task_failure(out):
            print("Failure detected during execution!")
            sim_proc.kill()
            modify_instance_to_avoid_failure(args.instance, ALT_INSTANCE, action)
            print(f"Generated new instance: {ALT_INSTANCE}")
            print("Replanning from new instance...")
            run_planner(ALT_INSTANCE)
            new_actions = extract_plan_actions()
            print("New plan generated:")
            for a in new_actions:
                print(f"  - {a}")
            return

    print("Original plan executed successfully without failure.")

if __name__ == "__main__":
    main()
