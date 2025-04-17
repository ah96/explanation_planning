import subprocess
import time
import re
import os
import sys
import argparse

PLANNER_SCRIPT = "src/rosplan/rosplan_planning_system/common/bin/prost/run_prost.sh"
PLANNER_ARGS = "[PROST -s 1 -se [IPPC2014]]"
OUTPUT_PLAN_FILE = "./plan_output.txt"
DOMAIN_FILE = "./domain.rddl"
DEFAULT_INSTANCE_FILE = "./instance_failure_probability.rddl"
REACTIVE_INSTANCE_FILE = "./instance_failure_probability_reactive.rddl"

def run_planner(domain, instance):
    print(f"Running planner on: {instance}")
    with open(OUTPUT_PLAN_FILE, "w") as f:
        subprocess.run([PLANNER_SCRIPT, domain, instance, PLANNER_ARGS, OUTPUT_PLAN_FILE], stdout=f, stderr=subprocess.STDOUT)

def extract_plan(plan_file):
    with open(plan_file, "r") as f:
        text = f.read()
    actions = re.findall(r"\*\* Actions received: \[(.*?)\]", text)
    flat_actions = [a.strip() for group in actions if group for a in group.split(';') if a.strip()]
    return flat_actions

def start_simulator():
    print("Launching RDDLSim...")
    return subprocess.Popen(
        ["python3", "/home/robolab/planning_ws/planners/prost/testbed/run-server.py", "-b", "./"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

def simulate_plan(plan):
    proc = start_simulator()
    time.sleep(2)
    state_history = []
    failure_detected = False
    current_action = None

    for i, action in enumerate(plan):
        print(f"Step {i+1}: Executing action: {action}")
        try:
            proc.stdin.write(action + "\n")
            proc.stdin.flush()
            time.sleep(1)
            output = proc.stdout.readline()
            if "task_failed = true" in output.lower():
                print("Failure detected at action:", action)
                failure_detected = True
                current_action = action
                break
            state_history.append(output.strip())
        except Exception as e:
            print("Simulator error:", e)
            break

    proc.terminate()
    return failure_detected, current_action

def generate_reactive_instance(original_instance_path, new_instance_path, failure_action):
    with open(original_instance_path, "r") as f:
        content = f.read()

    match = re.search(r"fetch_book\(([^,]+),\s*([^,]+),\s*([^)]+)\)", failure_action)
    if not match:
        print("Could not extract book from failing action.")
        return

    _, failing_book, _ = match.groups()

    # Set all prob_failure for the failing book to 0.0
    content = re.sub(
        rf"prob_failure\({failing_book}, ([^)]+)\)\s*=\s*[0-9.]+;",
        rf"prob_failure({failing_book}, \1) = 0.0;",
        content
    )

    content = re.sub(
        r"instance\s+([^\s]+)",
        "instance instance_failure_probability_reactive",
        content
    )

    with open(new_instance_path, "w") as f:
        f.write(content)

    print(f"Generated new instance: {new_instance_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", type=str, default="./domain.rddl", help="Path to the domain file")
    parser.add_argument("--instance", type=str, default="./instance_failures_responses.rddl", help="Path to the instance file")
    args = parser.parse_args()

    # update domain and instance paths
    domain_path = args.domain
    instance_path = args.instance
    instance_name = os.path.splitext(os.path.basename(instance_path))[0]
    #alt_path = "./" + instance_name + "_alternative.rddl"
    #alt_name = os.path.splitext(os.path.basename(alt_path))[0]
    
    # run the planner to get the original plan
    run_planner(domain_path, instance_path)
    print("Waiting for planner output...")
    plan = extract_plan(OUTPUT_PLAN_FILE)

    if not plan:
        print("No plan generated.")
        return

    print("Plan generated:")
    for a in plan:
        print("  -", a)

    print("Simulating plan step-by-step...")
    failure, fail_action = simulate_plan(plan)
    print(failure, fail_action)

    if failure:
        generate_reactive_instance(instance_path, REACTIVE_INSTANCE_FILE, fail_action)
        print("Replanning from new instance...")
        run_planner(domain_path, REACTIVE_INSTANCE_FILE, OUTPUT_PLAN_FILE)
        new_plan = extract_plan(OUTPUT_PLAN_FILE)
        print("New plan generated:")
        for a in new_plan:
            print("  -", a)
    else:
        print("Original plan executed successfully without failure.")

if __name__ == "__main__":
    main()
