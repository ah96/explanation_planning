import re

def parse_problem_file(problem_file_path):
    """
    Parse the RDDL problem file to extract failure probabilities and response probabilities.

    :param problem_file_path: Path to the RDDL problem file.
    :return: Tuple of failure probabilities and response probabilities.
    """
    failure_probabilities = {}
    response_probabilities = {}

    with open(problem_file_path, 'r') as file:
        content = file.read()

    # Extract failure probabilities
    failure_matches = re.findall(r"prob_failure\((\w+)\)\s*=\s*([\d.]+);", content)
    for failure, prob in failure_matches:
        failure_probabilities[failure] = float(prob)

    # Extract response probabilities for each failure
    response_matches = re.findall(r"prob_response\((\w+),\s*(\w+)\)\s*=\s*([\d.]+);", content)
    for response, failure, prob in response_matches:
        if failure not in response_probabilities:
            response_probabilities[failure] = {}
        response_probabilities[failure][response] = float(prob)

    return failure_probabilities, response_probabilities


def identify_failure_and_response_from_file(plan, problem_file_path):
    """
    Identify a failure type and the most probable response based on the problem file,
    then add the response to the plan after a `goto_waypoint` action to `visitor_area`.

    :param plan: List of strings representing the current plan.
    :param problem_file_path: Path to the RDDL problem file.
    :return: Updated plan with the response action added.
    """
    # Parse the problem file
    failure_probabilities, response_probabilities = parse_problem_file(problem_file_path)
    #print(failure_probabilities)
    #print(response_probabilities)

    # Step 1: Identify the most probable failure type
    failure = max(failure_probabilities, key=failure_probabilities.get)
    print(failure)

    # Step 2: Identify the most probable response for the failure
    response_probs = response_probabilities.get(failure, {})
    response = max(response_probs, key=response_probs.get) if response_probs else None

    if not response:
        print("No valid response found for failure:", failure)
        return plan

    # Step 3: Add the response action to the plan after the relevant `goto_waypoint` action
    response_action = f"give_response(robot, {response}, {failure}, visitor)"
    updated_plan = []

    for action in plan:
        updated_plan.append(action)
        # Check if the action is a `goto_waypoint` to `visitor_area`
        if "goto_waypoint" in action and "visitor_area" in action:
            updated_plan.append(response_action)  # Add the response action after it

    return updated_plan


# Example usage
problem_file = "./testbed/benchmarks/gerard_wo_response/full_problem.rddl"

current_plan = [
    "goto_waypoint(robot, start_position, bookshelf)",
    "fetch_book(robot, book, visitor)",
    "goto_waypoint(robot, bookshelf, visitor_area)"
]

updated_plan = identify_failure_and_response_from_file(current_plan, problem_file)
print("Updated Plan:")
print("\n".join(updated_plan))
