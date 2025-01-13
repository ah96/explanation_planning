import subprocess
import re

def extract_plan_from_prost(problem_instance, planner_settings="[Prost -s 1 -se [IPC2014]]"):
    """
    Run PROST and extract the sequence of actions (final plan).

    :param problem_instance: Name of the problem instance.
    :param planner_settings: Settings for the planner.
    :return: A list of actions forming the plan.
    """
    try:
        # Run PROST
        planner_settings="[Prost -s 1 -se [IPC2014]]"
        prost_command = ["./prost.py", problem_instance, planner_settings]
        result = subprocess.run(prost_command, capture_output=True, text=True, check=True)

        #print(result)

        # Extract actions from the output
        action_pattern = re.compile(r"[a-zA-Z_]+\([^()0-9]*\)") #re.compile(r"\([^\d()]*\)")  # Match actions in parentheses
        actions = action_pattern.findall(result.stdout)

        #print(action_pattern)
        #print(actions)
        #print(len(actions))

        plan_length = int(len(actions) / 2)
        print(plan_length)
        plan = actions[len(actions)-plan_length:len(actions)]
        print(plan)
        plan_final = []
        print('\nPlan:')
        for a in plan:
            if a != 'noop()':
                plan_final.append(a)
                print(a)

        return actions

    except subprocess.CalledProcessError as e:
        print("An error occurred while running PROST:")
        print(e.stderr)
        return []

# Example usage
if __name__ == "__main__":
    problem_instance_name = "explanation_planning_instance"
    plan = extract_plan_from_prost(problem_instance_name)
    '''
    if plan:
        print("Extracted Plan:")
        for step, action in enumerate(plan, 1):
            print(f"{step}: {action}")
    else:
        print("No plan found.")
    '''