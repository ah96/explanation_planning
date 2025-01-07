import random
from collections import defaultdict
import pandas as pd

class ExplanationScenarioModel:
    def __init__(self):
        """
        Initialize the scenario-response model with predefined probabilities.
        """
        self.scenarios = [
            "agent_error",
            "suboptimal_behavior",
            "agent_inability",
            "unforeseen_circumstances",
            "uncertainty",
            "social_norm_violation",
            "normal_interaction",
        ]

        self.responses = [
            "why_explanation",
            "what_explanation",
            "apology",
            "ask_for_help",
            "narrate_next_action",
            "continue_without_comment",
        ]

        # Initial probabilities for response preferences and failure likelihoods
        self.probability_table = self._initialize_response_probabilities()
        self.failure_probabilities = self._initialize_failure_probabilities()

    def _initialize_response_probabilities(self):
        """
        Create the initial probability table for scenario-response relationships.
        """
        table = defaultdict(dict)

        table["agent_error"] = {
            "why_explanation": 0.4,
            "what_explanation": 0.2,
            "apology": 0.3,
            "ask_for_help": 0.05,
            "narrate_next_action": 0.05,
            "continue_without_comment": 0.0,
        }

        table["suboptimal_behavior"] = {
            "why_explanation": 0.5,
            "what_explanation": 0.2,
            "apology": 0.1,
            "ask_for_help": 0.05,
            "narrate_next_action": 0.1,
            "continue_without_comment": 0.05,
        }

        table["agent_inability"] = {
            "why_explanation": 0.4,
            "what_explanation": 0.1,
            "apology": 0.2,
            "ask_for_help": 0.3,
            "narrate_next_action": 0.0,
            "continue_without_comment": 0.0,
        }

        table["unforeseen_circumstances"] = {
            "why_explanation": 0.6,
            "what_explanation": 0.2,
            "apology": 0.1,
            "ask_for_help": 0.05,
            "narrate_next_action": 0.05,
            "continue_without_comment": 0.0,
        }

        table["uncertainty"] = {
            "why_explanation": 0.4,
            "what_explanation": 0.1,
            "apology": 0.0,
            "ask_for_help": 0.4,
            "narrate_next_action": 0.1,
            "continue_without_comment": 0.0,
        }

        table["social_norm_violation"] = {
            "why_explanation": 0.3,
            "what_explanation": 0.1,
            "apology": 0.5,
            "ask_for_help": 0.0,
            "narrate_next_action": 0.1,
            "continue_without_comment": 0.0,
        }

        table["normal_interaction"] = {
            "why_explanation": 0.0,
            "what_explanation": 0.0,
            "apology": 0.0,
            "ask_for_help": 0.0,
            "narrate_next_action": 0.0,
            "continue_without_comment": 1.0,
        }

        return table

    def _initialize_failure_probabilities(self):
        """
        Initialize probabilities for failures in each scenario.
        """
        return {
            "agent_error": 0.2,
            "suboptimal_behavior": 0.15,
            "agent_inability": 0.1,
            "unforeseen_circumstances": 0.25,
            "uncertainty": 0.2,
            "social_norm_violation": 0.05,
            "normal_interaction": 0.05,
        }

    def randomize_probabilities(self):
        """
        Randomize the probability values for response preferences and failures.
        """
        for scenario in self.scenarios:
            # Randomize response probabilities
            total = 0.0
            random_probs = {}

            for response in self.responses:
                prob = random.random()
                random_probs[response] = prob
                total += prob

            for response in self.responses:
                random_probs[response] /= total

            self.probability_table[scenario] = random_probs

            # Randomize failure probabilities
        total = 0.0
        failure_probs = {}

        for scenario in self.scenarios:
            prob = random.random()
            failure_probs[scenario] = prob
            total += prob

        for scenario in self.scenarios:
            failure_probs[scenario] /= total

        self.failure_probabilities = failure_probs

    def get_probabilities(self):
        """
        Retrieve the current probability table.
        """
        return self.probability_table

    def get_failure_probabilities(self):
        """
        Retrieve the current failure probabilities.
        """
        return self.failure_probabilities

    def display_probabilities_as_table(self):
        """
        Display the response probability table as a pandas DataFrame.
        """
        df = pd.DataFrame.from_dict(self.probability_table, orient="index", columns=self.responses)
        print("Response Probabilities:")
        print(df)

    def display_failure_probabilities(self):
        """
        Display failure probabilities as a pandas DataFrame.
        """
        df = pd.DataFrame(list(self.failure_probabilities.items()), columns=["Scenario", "Failure Probability"])
        print("\nFailure Probabilities:")
        print(df)

# Explanation Planning Methods
class ExplanationPlanning:
    def __init__(self, model):
        """
        Initialize the explanation planning with the scenario model.
        :param model: Instance of ExplanationScenarioModel.
        """
        self.model = model

    def pre_hoc_planning(self):
        """
        Pre-hoc planning considering both failure probabilities and response preferences.
        """
        print("\nPre-Hoc Planning:")
        combined = {}
        for scenario in self.model.scenarios:
            for response, prob in self.model.probability_table[scenario].items():
                combined[(scenario, response)] = prob * self.model.failure_probabilities[scenario]
        df = pd.DataFrame.from_dict(combined, orient="index", columns=["Combined Probability"])
        print(df)

    def reactive_planning(self, detected_scenario):
        """
        Reactive planning given a detected failure scenario.
        :param detected_scenario: The scenario detected during runtime.
        """
        print("\nReactive Planning:")
        if detected_scenario in self.model.scenarios:
            df = pd.DataFrame.from_dict(
                self.model.probability_table[detected_scenario], orient="index", columns=["Response Probability"]
            )
            print(df)
        else:
            print(f"Unknown scenario: {detected_scenario}")

    def post_hoc_planning(self, executed_plan):
        """
        Post-hoc planning considering the executed plan.
        :param executed_plan: A dictionary with scenarios and counts from the plan.
        """
        print("\nPost-Hoc Planning:")
        combined = {}
        for scenario, count in executed_plan.items():
            for response, prob in self.model.probability_table[scenario].items():
                combined[(scenario, response)] = prob * count
        df = pd.DataFrame.from_dict(combined, orient="index", columns=["Weighted Response"])
        print(df)

# Example Usage
if __name__ == "__main__":
    model = ExplanationScenarioModel()

    print("Initial Response Probability Table:")
    model.display_probabilities_as_table()

    print("\nInitial Failure Probability Table:")
    model.display_failure_probabilities()

    model.randomize_probabilities()
    print("\nRandomized Response Probability Table:")
    model.display_probabilities_as_table()

    print("\nRandomized Failure Probability Table:")
    model.display_failure_probabilities()

    planner = ExplanationPlanning(model)
    planner.pre_hoc_planning()
    planner.reactive_planning("agent_error")
    executed_plan = {"agent_error": 3, "uncertainty": 2}
    planner.post_hoc_planning(executed_plan)



class ExplanationPlanning:
    def __init__(self, model, domain_file, problem_file):
        """
        Initialize the explanation planning with the scenario model and planner.
        :param model: Instance of ExplanationScenarioModel.
        :param domain_file: Path to the PDDL domain file.
        :param problem_file: Path to the PDDL problem file.
        """
        self.model = model
        self.planner = PDDLPlanner(domain_file, problem_file)

    def pre_hoc_planning(self):
        """
        Pre-hoc planning using the PDDL planner.
        """
        print("\nPre-Hoc Planning:")
        plan = self.planner.run_planner()
        if plan:
            print("Generated Plan:")
            print(plan)
        else:
            print("Failed to generate plan.")
