import re

plan = ['Plan:', 'goto_waypoint(tiago, start_position, bookshelf)', 'fetch_book(tiago, book, visitor)', 'failure_happens(tiago, book, agent_error)', 'goto_waypoint(tiago, bookshelf, visitor_area)']

def extract_plan_details(plan):
    """
    Extracts robot, human, book, and failure type details from the plan.

    :param plan: List of strings representing the plan.
    :return: Dictionary with extracted details.
    """
    details = {
        "robot": None,
        "human": None,
        "book": None,
        "failure": None,
        "waypoint": None
    }

    waypoint_found = False

    # Regex patterns to match fetch_book and failure_happens actions
    waypoint_pattern = re.compile(r"goto_waypoint\((\w+),\s*(\w+),\s*(\w+)\)")
    fetch_book_pattern = re.compile(r"fetch_book\((\w+),\s*(\w+),\s*(\w+)\)")
    failure_happens_pattern = re.compile(r"failure_happens\((\w+),\s*(\w+),\s*(\w+)\)")

    for action in plan:
        # Match fetch_book to extract robot, book, and human
        fetch_match = fetch_book_pattern.match(action)
        if fetch_match:
            details["robot"] = fetch_match.group(1)
            details["book"] = fetch_match.group(2)
            details["human"] = fetch_match.group(3)

        # Match failure_happens to extract the failure type
        failure_match = failure_happens_pattern.match(action)
        if failure_match:
            details["failure"] = failure_match.group(3)

        waypoint_match = waypoint_pattern.match(action)
        if waypoint_match and not waypoint_found:
            details["waypoint"] = waypoint_match.group(3)
            waypoint_found = True

    return details

details = extract_plan_details(plan)
print(details['waypoint'])

def modify_problem_file(input_file_path, output_file_path):
    """
    Reads an RDDL problem file, modifies its content, and saves the changes to a new file.

    :param input_file_path: Path to the original problem file.
    :param output_file_path: Path to save the modified problem file.
    """
    with open(input_file_path, 'r') as file:
        content = file.readlines()

    updated_content = []

    # Iterate through the content and modify it as needed
    for line in content:
        # Update the non-fluent name
        if "non-fluents nf_explanation_planning_posthoc" in line:
            line = line.replace("nf_explanation_planning_posthoc", "nf_explanation_planning_reactive")

        # Update all probabilities for responses and failures based on the new specifications
        if "prob_response(why_explanation, agent_error)" in line:
            line = "      prob_response(why_explanation, agent_error) = 0.9; //0.2;\n"
        elif "prob_response(what_explanation, agent_error)" in line:
            line = "      prob_response(what_explanation, agent_error) = 0.15;\n"
        elif "prob_response(apology, agent_error)" in line:
            line = "      prob_response(apology, agent_error) = 0.1;\n"
        elif "prob_response(ask_for_help, agent_error)" in line:
            line = "      prob_response(ask_for_help, agent_error) = 0.25;\n"
        elif "prob_response(narrate_next_action, agent_error)" in line:
            line = "      prob_response(narrate_next_action, agent_error) = 0.2;\n"
        elif "prob_response(continue_without_comment, agent_error)" in line:
            line = "      prob_response(continue_without_comment, agent_error) = 0.05;\n"

        elif "prob_response(why_explanation, suboptimal_behavior)" in line:
            line = "      prob_response(why_explanation, suboptimal_behavior) = 0.2;\n"
        elif "prob_response(what_explanation, suboptimal_behavior)" in line:
            line = "      prob_response(what_explanation, suboptimal_behavior) = 0.15;\n"
        elif "prob_response(apology, suboptimal_behavior)" in line:
            line = "      prob_response(apology, suboptimal_behavior) = 0.1;\n"
        elif "prob_response(ask_for_help, suboptimal_behavior)" in line:
            line = "      prob_response(ask_for_help, suboptimal_behavior) = 0.25;\n"
        elif "prob_response(narrate_next_action, suboptimal_behavior)" in line:
            line = "      prob_response(narrate_next_action, suboptimal_behavior) = 0.2;\n"
        elif "prob_response(continue_without_comment, suboptimal_behavior)" in line:
            line = "      prob_response(continue_without_comment, suboptimal_behavior) = 0.05;\n"

        elif "prob_response(why_explanation, agent_inability)" in line:
            line = "      prob_response(why_explanation, agent_inability) = 0.2;\n"
        elif "prob_response(what_explanation, agent_inability)" in line:
            line = "      prob_response(what_explanation, agent_inability) = 0.15;\n"
        elif "prob_response(apology, agent_inability)" in line:
            line = "      prob_response(apology, agent_inability) = 0.1;\n"
        elif "prob_response(ask_for_help, agent_inability)" in line:
            line = "      prob_response(ask_for_help, agent_inability) = 0.25;\n"
        elif "prob_response(narrate_next_action, agent_inability)" in line:
            line = "      prob_response(narrate_next_action, agent_inability) = 0.2;\n"
        elif "prob_response(continue_without_comment, agent_inability)" in line:
            line = "      prob_response(continue_without_comment, agent_inability) = 0.05;\n"

        elif "prob_response(why_explanation, unforeseen_circumstances)" in line:
            line = "      prob_response(why_explanation, unforeseen_circumstances) = 0.2;\n"
        elif "prob_response(what_explanation, unforeseen_circumstances)" in line:
            line = "      prob_response(what_explanation, unforeseen_circumstances) = 0.15;\n"
        elif "prob_response(apology, unforeseen_circumstances)" in line:
            line = "      prob_response(apology, unforeseen_circumstances) = 0.1;\n"
        elif "prob_response(ask_for_help, unforeseen_circumstances)" in line:
            line = "      prob_response(ask_for_help, unforeseen_circumstances) = 0.25;\n"
        elif "prob_response(narrate_next_action, unforeseen_circumstances)" in line:
            line = "      prob_response(narrate_next_action, unforeseen_circumstances) = 0.2;\n"
        elif "prob_response(continue_without_comment, unforeseen_circumstances)" in line:
            line = "      prob_response(continue_without_comment, unforeseen_circumstances) = 0.05;\n"

        elif "prob_response(why_explanation, uncertainty)" in line:
            line = "      prob_response(why_explanation, uncertainty) = 0.2;\n"
        elif "prob_response(what_explanation, uncertainty)" in line:
            line = "      prob_response(what_explanation, uncertainty) = 0.15;\n"
        elif "prob_response(apology, uncertainty)" in line:
            line = "      prob_response(apology, uncertainty) = 0.1;\n"
        elif "prob_response(ask_for_help, uncertainty)" in line:
            line = "      prob_response(ask_for_help, uncertainty) = 0.25;\n"
        elif "prob_response(narrate_next_action, uncertainty)" in line:
            line = "      prob_response(narrate_next_action, uncertainty) = 0.2;\n"
        elif "prob_response(continue_without_comment, uncertainty)" in line:
            line = "      prob_response(continue_without_comment, uncertainty) = 0.05;\n"

        elif "prob_response(why_explanation, social_norm_violation)" in line:
            line = "      prob_response(why_explanation, social_norm_violation) = 0.2;\n"
        elif "prob_response(what_explanation, social_norm_violation)" in line:
            line = "      prob_response(what_explanation, social_norm_violation) = 0.15;\n"
        elif "prob_response(apology, social_norm_violation)" in line:
            line = "      prob_response(apology, social_norm_violation) = 0.1;\n"
        elif "prob_response(ask_for_help, social_norm_violation)" in line:
            line = "      prob_response(ask_for_help, social_norm_violation) = 0.25;\n"
        elif "prob_response(narrate_next_action, social_norm_violation)" in line:
            line = "      prob_response(narrate_next_action, social_norm_violation) = 0.2;\n"
        elif "prob_response(continue_without_comment, social_norm_violation)" in line:
            line = "      prob_response(continue_without_comment, social_norm_violation) = 0.05;\n"

        elif "prob_response(why_explanation, normal_interaction)" in line:
            line = "      prob_response(why_explanation, normal_interaction) = 0.2;\n"
        elif "prob_response(what_explanation, normal_interaction)" in line:
            line = "      prob_response(what_explanation, normal_interaction) = 0.15;\n"
        elif "prob_response(apology, normal_interaction)" in line:
            line = "      prob_response(apology, normal_interaction) = 0.1;\n"
        elif "prob_response(ask_for_help, normal_interaction)" in line:
            line = "      prob_response(ask_for_help, normal_interaction) = 0.25;\n"
        elif "prob_response(narrate_next_action, normal_interaction)" in line:
            line = "      prob_response(narrate_next_action, normal_interaction) = 0.2;\n"
        elif "prob_response(continue_without_comment, normal_interaction)" in line:
            line = "      prob_response(continue_without_comment, normal_interaction) = 0.05;\n"

        # Update the initial state and instance name
        if "init-state {" in line:
            updated_content.append(line)
            #updated_content.append("        robot_at(tiago, bookshelf);\n")
            updated_content.append("        book_fetched("+details["book"]+", "+details["robot"]+", "+details["human"]+");\n")
            updated_content.append("        failure_triggered("+details["failure"]+");\n")
            updated_content.append("        failure_happened = true;\n")
            continue

        if "instance instance_posthoc" in line:
            line = line.replace("instance_posthoc", "instance_reactive")

        if "nf_explanation_planning_posthoc" in line:
            line = line.replace("nf_explanation_planning_posthoc", "nf_explanation_planning_reactive")

        if "robot_at(tiago, start_position);" in line:
            line = line.replace("start_position", details["waypoint"])

        updated_content.append(line)

    # Save the modified content to a new file
    with open(output_file_path, 'w') as file:
        file.writelines(updated_content)

# Example usage
input_file = "./problem_posthoc.rddl"
output_file = "./problem_reactive.rddl"
modify_problem_file(input_file, output_file)
