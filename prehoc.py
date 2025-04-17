
import subprocess
import time
import re
import shutil
import os
import argparse
from pathlib import Path

# --- Configuration ---
PLANNER_SCRIPT = "src/rosplan/rosplan_planning_system/common/bin/prost/run_prost.sh"
DOMAIN_FILE = "./domain.rddl"
PLANNER_ARGS = "[PROST -s 1 -se [IPPC2014]]"
PLAN_FILE = "./rddl_plan_output.log"

def run_planner(domain_file, instance_file):
    print(f"\nRunning planner with instance: {instance_file}...")
    with open(PLAN_FILE, "w") as f:
        subprocess.run([
            PLANNER_SCRIPT,
            domain_file,
            instance_file,
            PLANNER_ARGS
        ], stdout=f, stderr=subprocess.STDOUT, text=True)

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

def extract_actions(plan_lines):
    actions = []
    for line in plan_lines:
        if "Actions received:" in line:
            matches = re.findall(r"([a-zA-Z_]+\([^()]*\))", line)
            actions.extend([a for a in matches if a != "noop()"])
    return actions

def contains_failure(plan_lines):
    return any("give_response(" in line for line in plan_lines if "Actions received:" in line)

def parse_instance_file(instance_file):
    with open(instance_file, "r") as f:
        content = f.read()

    book_wants = re.findall(r"wants_book\(([^,]+), ([^)]+)\)", content)
    prob_failure_entries = re.findall(r"prob_failure\(([^,]+), ([^)]+)\)\s*=\s*([0-9.]+);", content)

    human_book_map = {h.strip(): b.strip() for h, b in book_wants}
    book_failure_probs = {}
    for book, failure, prob in prob_failure_entries:
        book = book.strip()
        failure = failure.strip()
        prob = float(prob)
        book_failure_probs.setdefault(book, {})[failure] = prob

    return human_book_map, book_failure_probs

def analyze_explanation(plan_lines):
    explanations = []
    for line in plan_lines:
        if "give_response(" in line:
            match = re.search(r"give_response\(([^,]+), ([^,]+), ([^,]+), ([^,]+), ([^)]+)\)", line)
            if match:
                robot, response, failure, book, human = match.groups()
                explanations.append(
                    f"The robot {robot} issued a '{response}' explanation to {human}, "
                    f"after experiencing a '{failure}' failure while handling {book}."
                )
    return explanations

def verbalize_plan_differences(original_actions, new_actions, original_instance, new_instance):
    removed = [a for a in original_actions if a not in new_actions]
    added = [a for a in new_actions if a not in original_actions]

    print("\nPlan comparison:")
    if removed:
        print("Removed actions:")
        for a in removed:
            print("  -", a)
    if added:
        print("Added actions:")
        for a in added:
            print("  +", a)

    if any("give_response" in a for a in removed):
        print("No explanation (give_response) action needed in the new plan — failure was avoided.")

    with Path(original_instance).open("r") as f:
       original_instance_content = f.read()

    with Path(new_instance).open("r") as f:
        new_instance_content = f.read()

    # Extract all prob_failure entries from both files
    original_entries = re.findall(r"prob_failure\(([^,]+), ([^)]+)\)\s*=\s*([\d.]+)", original_instance_content)
    new_entries = re.findall(r"prob_failure\(([^,]+), ([^)]+)\)\s*=\s*([\d.]+)", new_instance_content)

    original_probs = {}
    new_probs = {}

    for book, failure, prob in original_entries:
        original_probs.setdefault(book, {})[failure] = float(prob)

    for book, failure, prob in new_entries:
        new_probs.setdefault(book, {})[failure] = float(prob)

    # Now compare the probabilities and create explanation sentences
    explanations = []
    for book in original_probs:
        for failure in original_probs[book]:
            original_prob = original_probs[book][failure]
            new_prob = new_probs.get(book, {}).get(failure, original_prob)
            if new_prob < original_prob:
                explanations.append(
                    f"In the alternative instance, the probability of the failure '{failure}' for book '{book}' was lowered "
                    f"from {original_prob:.2f} to {new_prob:.2f}, leading to a plan that avoids failure."
                )

    for explanation in explanations:
        print(explanation)


def print_plan_summary(actions):
    if actions:
        print("Generated Plan:")
        for step, act in enumerate(actions, 1):
            print(f"  {step}: {act}")
    else:
        print("No meaningful actions in the plan.")

def main_gui(domain_path, instance_path):
    """Parse the arguments from the terminal and run the prehoc strategy"""
    #parser = argparse.ArgumentParser()
    #parser.add_argument("--domain", type=str, default="./domain.rddl", help="Path to the domain file")
    #parser.add_argument("--instance", type=str, default="./instance_failures_responses.rddl", help="Path to the instance file")
    #args = parser.parse_args()

    # update domain and instance paths
    #domain_path = args.domain
    #instance_path = args.instance
    instance_name = os.path.splitext(os.path.basename(instance_path))[0]
    alt_path = "./" + instance_name + "_alternative.rddl"
    alt_name = os.path.splitext(os.path.basename(alt_path))[0]
    
    # run the planner to get the original plan
    run_planner(domain_path, instance_path)
    original_output = wait_for_plan()
    original_actions = extract_actions(original_output)
    print_plan_summary(original_actions)

    if contains_failure(original_output):
        print("\nExplanation detected in the plan:")
        for line in analyze_explanation(original_output):
            print("  -", line)

        run_planner(DOMAIN_FILE, alt_path)
        new_output = wait_for_plan()
        new_actions = extract_actions(new_output)

        print("\nAlternative plan:")
        print_plan_summary(new_actions)

        verbalize_plan_differences(original_actions, new_actions, instance_path, alt_path)

        return new_actions
    else:
        print("No explanation actions found. Failure was likely avoided in the original plan.")        

    return original_actions

def main():
    """Parse the arguments from the terminal and run the prehoc strategy"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", type=str, default="./domain.rddl", help="Path to the domain file")
    parser.add_argument("--instance", type=str, default="./instance_failures_responses.rddl", help="Path to the instance file")
    args = parser.parse_args()

    # update domain and instance paths
    domain_path = args.domain
    instance_path = args.instance
    instance_name = os.path.splitext(os.path.basename(instance_path))[0]
    alt_path = "./" + instance_name + "_alternative.rddl"
    alt_name = os.path.splitext(os.path.basename(alt_path))[0]
    
    # run the planner to get the original plan
    run_planner(domain_path, instance_path)
    original_output = wait_for_plan()
    original_actions = extract_actions(original_output)
    print_plan_summary(original_actions)

    if contains_failure(original_output):
        print("\nExplanation detected in the plan:")
        for line in analyze_explanation(original_output):
            print("  -", line)

        run_planner(DOMAIN_FILE, alt_path)
        new_output = wait_for_plan()
        new_actions = extract_actions(new_output)

        print("\nAlternative plan:")
        print_plan_summary(new_actions)

        verbalize_plan_differences(original_actions, new_actions, instance_path, alt_path)
    else:
        print("No explanation actions found. Failure was likely avoided in the original plan.")

if __name__ == "__main__":
    main()
