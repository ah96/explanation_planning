import subprocess
import time
import re
import argparse

# --- Configuration ---

PLANNER_SCRIPT = "src/rosplan/rosplan_planning_system/common/bin/prost/run_prost.sh"
DOMAIN_FILE = "./domain.rddl"
INSTANCE_FILE = "./instance_failures_responses.rddl"
PLANNER_ARGS = "[PROST -s 1 -se [IPPC2014]]"
PLAN_FILE = "./rddl_plan_output.log"

# --- Run the Planner ---

def run_planner(domain_path, instance_path):
    print("Running planner via shell script...")
    with open(PLAN_FILE, "w") as f:
        subprocess.run([
            PLANNER_SCRIPT,
            domain_path,
            instance_path,
            PLANNER_ARGS
        ], stdout=f, stderr=subprocess.STDOUT, text=True)

# --- Wait for Output File ---

def wait_for_plan(timeout=30):
    print("Waiting for planner output...")
    waited = 0
    while waited < timeout:
        try:
            with open(PLAN_FILE, "r") as f:
                lines = f.readlines()
                if lines:
                    return lines
        except FileNotFoundError:
            pass
        time.sleep(2)
        waited += 2
    return []

# --- Analyze Plan for Explanation Actions ---

def analyze_plan(plan_lines):
    """Extract give_response actions and generate general verbalizations."""
    explanations = []
    for line in plan_lines:
        if "** Actions received:" in line:
            match = re.search(r"give_response\(([^,]+), ([^,]+), ([^,]+), ([^,]+), ([^)]+)\);", line)
            if match:
                robot, response_type, failure_type, book, human = match.groups()
                readable = failure_type.replace("_", " ").lower()
                response_readable = response_type.replace("_", " ").lower()
                explanation = (
                    f"The robot {robot} needed to provide a {response_readable} response "
                    f"after encountering a {readable} problem while attempting to deliver {book} to {human}."
                )
                explanations.append(explanation)
    return explanations

# --- Print the Plan Actions ---

def extract_actions(plan_lines):
    actions = []
    for line in plan_lines:
        if "Actions received:" in line:
            matches = re.findall(r"([a-zA-Z_]+\([^()]*\))", line)
            actions.extend([a for a in matches if a != "noop()"])
    return actions

def print_plan_actions(plan_lines):
    """Print all meaningful actions from the plan."""
    non_empty_found = False
    actions = []
    for line in plan_lines:
        if "** Actions received:" in line and not re.search(r"\[\s*\]", line):
            print(line.strip())
            actions.append(line.strip())
            non_empty_found = True
    if not non_empty_found:
        print("Plan contains no meaningful actions.")
    return extract_actions(plan_lines)

# --- Main Execution ---

def main_gui(domain_path, instance_path):
    run_planner(domain_path, instance_path)
    plan_lines = wait_for_plan()
    if not plan_lines:
        print("No planner output found.")
    else:
        print("Planner output captured. Plan:")
        plan = print_plan_actions(plan_lines)
        explanations = analyze_plan(plan_lines)
        if explanations:
            print("\nPosthoc Explanation(s):")
            for exp in explanations:
                print(exp)
        else:
            print("No explanation actions (give_response) found in the plan.")
        return plan

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", type=str, default="./domain.rddl", help="Path to the domain file")
    parser.add_argument("--instance", type=str, default="./instance_failures_responses.rddl", help="Path to the instance file")
    args = parser.parse_args()

    # update domain and instance paths
    domain_path = args.domain
    instance_path = args.instance

    run_planner(domain_path, instance_path)
    plan_lines = wait_for_plan()
    if not plan_lines:
        print("No planner output found.")
    else:
        print("Planner output captured. Plan:")
        plan = print_plan_actions(plan_lines)
        explanations = analyze_plan(plan_lines)
        if explanations:
            print("\nPosthoc Explanation(s):")
            for exp in explanations:
                print(exp)
        else:
            print("No explanation actions (give_response) found in the plan.")

if __name__ == "__main__":
    main()
